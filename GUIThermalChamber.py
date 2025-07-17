import sys
import csv
import time
import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout,
    QHBoxLayout, QLabel, QLineEdit, QMessageBox, QComboBox, QTextEdit
)
from PyQt5.QtCore import QTimer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from classThermalChamber import ThermalChamber
import serial.tools.list_ports


class EmittingStream:
    def __init__(self, text_edit):
        self.text_edit = text_edit

    def write(self, text):
        self.text_edit.append(text)

    def flush(self):
        pass


class ChamberGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VC4020 Thermal Chamber GUI")
        self.chamber = None
        self.csv_file = None
        self.csv_writer = None
        self.csv_filename = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.poll_chamber)

        self.timestamps = []
        self.temp_setpoints = []
        self.temp_actuals = []
        self.start_time = time.time()
        self.moving_window = 7200

        self.scheduled_off_datetime = None
        self.time_checker = QTimer()
        self.time_checker.timeout.connect(self.check_turnoff_time)
        self.time_checker.start(1000)  # check every secon

        self.init_ui()

        # Redirect print output to QTextEdit
        sys.stdout = EmittingStream(self.log_output)
        sys.stderr = EmittingStream(self.log_output)

    def init_ui(self):
        layout = QVBoxLayout()

         # --- Port Selection + Status Light ---
        port_layout = QHBoxLayout()
        self.port_combo = QComboBox()
        self.refresh_ports()

        self.connect_btn = QPushButton("Connect")
        self.disconnect_btn = QPushButton("Disconnect")
        self.connect_btn.clicked.connect(self.connect_chamber)
        self.disconnect_btn.clicked.connect(self.disconnect_chamber)

        self.status_light = QLabel()
        self.status_light.setFixedSize(20, 20)
        self.status_light.setStyleSheet("border-radius: 10px; background-color: red;")  # 🔴 Default: Disconnected

        port_layout.addWidget(QLabel("Port:"))
        port_layout.addWidget(self.port_combo)
        port_layout.addWidget(self.connect_btn)
        port_layout.addWidget(self.disconnect_btn)
        port_layout.addWidget(self.status_light)  # Add light to layout
        layout.addLayout(port_layout)

        # --- Temperature Setpoint ---
        setpoint_layout = QHBoxLayout()
        self.setpoint_input = QLineEdit()
        self.setpoint_input.setPlaceholderText("Setpoint (°C)")
        self.set_btn = QPushButton("Set Temperature")
        self.set_btn.clicked.connect(self.set_temperature)
        setpoint_layout.addWidget(self.setpoint_input)
        setpoint_layout.addWidget(self.set_btn)
        layout.addLayout(setpoint_layout)

        # --- Plotting ---
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.temp_line, = self.ax.plot([], [], label="Temp Actual", color="red")
        self.set_line, = self.ax.plot([], [], label="Temp Setpoint", color="orange", linestyle="dashed")
        self.ax.set_xlabel("Ellapsed time since start (s)")
        self.ax.set_ylabel("Temperature (°C)")
        self.ax.grid()
        self.ax.legend()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

        # --- Turn Off Chamber ---
        turn_off_layout = QHBoxLayout()
        self.turn_off_btn = QPushButton("Turn Off Chamber")
        self.turn_off_btn.clicked.connect(self.turn_off_chamber)
        turn_off_layout.addStretch()
        turn_off_layout.addWidget(self.turn_off_btn)
        turn_off_layout.addStretch()
        layout.addLayout(turn_off_layout)

        # --- Console Output ---
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(QLabel("Console Output:"))
        layout.addWidget(self.log_output)

        # --- Scheduled Turn-Off by Duration ---
        duration_layout = QHBoxLayout()
        self.duration_input = QLineEdit()
        self.duration_input.setPlaceholderText("Duration (minutes)")
        self.schedule_btn = QPushButton("Schedule Turn-Off")
        self.cancel_timer_btn = QPushButton("Cancel Timer")
        self.schedule_btn.clicked.connect(self.schedule_turnoff_by_duration)
        self.cancel_timer_btn.clicked.connect(self.cancel_scheduled_turnoff)

        self.timer_info_label = QLabel("No shutoff scheduled.")
        duration_layout.addWidget(QLabel("Turn Off In:"))
        duration_layout.addWidget(self.duration_input)
        duration_layout.addWidget(self.schedule_btn)
        duration_layout.addWidget(self.cancel_timer_btn)
        layout.addLayout(duration_layout)
        layout.addWidget(self.timer_info_label)

        

    def refresh_ports(self):
        ports = serial.tools.list_ports.comports()
        self.port_combo.clear()
        self.port_combo.addItems([p.device for p in ports])

    def connect_chamber(self):
        port = self.port_combo.currentText()
        if not port:
            QMessageBox.warning(self, "Warning", "Select a serial port.")
            return

        try:
            self.chamber = ThermalChamber(port)
            self.start_logging()
            self.timer.start(5000)
            self.update_status_light('connected')
            print("Chamber connected")
        except Exception as e:
            QMessageBox.critical(self, "Connection Failed", str(e))

    def disconnect_chamber(self):
        if self.chamber:
            self.chamber.close_com()
            self.chamber = None
            self.update_status_light('disconnected')
            print("Chamber disconnected")
        self.timer.stop()
        self.stop_logging()

    def update_status_light(self, status: str):
        """
        status: 'connected', 'disconnected', or 'error'
        """
        color_map = {
            'connected': 'green',
            'disconnected': 'red',
            'error': 'yellow'
        }
        color = color_map.get(status, 'red')
        self.status_light.setStyleSheet(f"border-radius: 10px; background-color: {color};")

    def turn_off_chamber(self):
        if not self.chamber:
            QMessageBox.warning(self, "Not Connected", "Connect to the chamber first.")
            return
        try:
            self.chamber.turn_off_chamber()
            print("🔌 Chamber control turned off.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def set_temperature(self):
        if not self.chamber:
            QMessageBox.warning(self, "Not Connected", "Connect to the chamber first.")
            return
        try:
            temp = float(self.setpoint_input.text())
            self.chamber.set_temperature(temp)
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Enter a valid number.")
        except Exception as e:
            QMessageBox.critical(self, "Setpoint Error", str(e))

    def start_logging(self):
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.csv_filename = f"{now}_camber_logs.csv"
        self.csv_file = open(self.csv_filename, mode='w', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(["Wall_Timestamp", "Elapsed_Seconds", "Temp_Setpoint", "Temp_Actual"])

    def stop_logging(self):
        if self.csv_file:
            self.csv_file.close()
            print(f'Chamber logs saved in {self.csv_filename}')
            self.csv_file = None
            self.csv_writer = None

    def poll_chamber(self):
        if not self.chamber:
            return

        try:
            self.chamber.ser.write(b'$00I\r')
            response = self.chamber.ser.readline().decode(errors='ignore').strip()
            raw = response.split(' ')
            values = [float(v) for v in raw[:2]]  # T_set and T_act
            self.update_status_light('connected')

            if len(values) < 2:
                return

            t_set, t_act = values[0], values[1]
            elapsed = time.time() - self.start_time
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Update data
            self.timestamps.append(elapsed)
            self.temp_setpoints.append(t_set)
            self.temp_actuals.append(t_act)

            # Update plot
            self.temp_line.set_data(self.timestamps, self.temp_actuals)
            self.set_line.set_data(self.timestamps, self.temp_setpoints)
            self.ax.set_xlim(max(0, elapsed - self.moving_window), elapsed)
            self.ax.set_ylim(
                min(self.temp_actuals + self.temp_setpoints) - 5,
                max(self.temp_actuals + self.temp_setpoints) + 5,
            )
            self.canvas.draw()

            # Log
            if self.csv_writer:
                self.csv_writer.writerow([now, round(elapsed, 2), t_set, t_act])
                self.csv_file.flush()

        except Exception as e:
            print(f"Polling error: {e}")
            self.update_status_light('error')

    def schedule_turnoff_by_duration(self):
        try:
            minutes = float(self.duration_input.text().strip())
            if minutes <= 0:
                raise ValueError
            self.scheduled_off_datetime = datetime.datetime.now() + datetime.timedelta(minutes=minutes)
            formatted_time = self.scheduled_off_datetime.strftime("%H:%M:%S")
            self.timer_info_label.setText(f"⏱ Chamber scheduled to turn off at {formatted_time}")
            print(f"⏳ Chamber will turn off at {formatted_time} (in {minutes} minutes)")
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid number of minutes.")

    def check_turnoff_time(self):
        if self.scheduled_off_datetime and self.chamber:
            now = datetime.datetime.now()
            if now >= self.scheduled_off_datetime:
                print("🛑 Scheduled duration reached. Turning off chamber.")
                try:
                    self.chamber.turn_off_chamber()
                    self.stop_logging()
                    self.scheduled_off_datetime = None
                    self.timer_info_label.setText("✅ Chamber turned off and log saved.")
                    print("💾 Log file saved after scheduled shutdown.")
                except Exception as e:
                    print(f"Error during scheduled shutdown: {e}")

    def cancel_scheduled_turnoff(self):
        self.scheduled_off_datetime = None
        self.timer_info_label.setText("❌ Shutdown timer cancelled.")
        print("❌ Shutdown timer cancelled.")

    def closeEvent(self, event):
        self.disconnect_chamber()
        self.update_status_light(False)
        self.stop_logging()  # Safe to call twice
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = ChamberGUI()
    gui.resize(800, 600)
    gui.show()
    sys.exit(app.exec_())