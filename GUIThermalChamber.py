import sys
import csv
import time
import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout,
    QHBoxLayout, QLabel, QLineEdit, QMessageBox, QComboBox
)
from PyQt5.QtCore import QTimer
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from classThermalChamber import ThermalChamber
import serial.tools.list_ports


class ChamberGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VC4020 Thermal Chamber GUI")
        self.chamber = None
        self.csv_file = None
        self.csv_writer = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.poll_chamber)

        self.timestamps = []
        self.temp_setpoints = []
        self.temp_actuals = []
        self.start_time = time.time()

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # --- Port Selection ---
        port_layout = QHBoxLayout()
        self.port_combo = QComboBox()
        self.refresh_ports()
        self.connect_btn = QPushButton("Connect")
        self.disconnect_btn = QPushButton("Disconnect")
        self.connect_btn.clicked.connect(self.connect_chamber)
        self.disconnect_btn.clicked.connect(self.disconnect_chamber)
        port_layout.addWidget(QLabel("Port:"))
        port_layout.addWidget(self.port_combo)
        port_layout.addWidget(self.connect_btn)
        port_layout.addWidget(self.disconnect_btn)
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
        self.ax.set_xlabel("Time (s)")
        self.ax.set_ylabel("Temperature (°C)")
        self.ax.legend()
        layout.addWidget(self.canvas)

        self.setLayout(layout)

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
        except Exception as e:
            QMessageBox.critical(self, "Connection Failed", str(e))

    def disconnect_chamber(self):
        if self.chamber:
            self.chamber.close_com()
            self.chamber = None
        self.timer.stop()
        self.stop_logging()

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
        self.csv_file = open(f"chamber_log_{now}.csv", mode='w', newline='')
        self.csv_writer = csv.writer(self.csv_file)
        self.csv_writer.writerow(["Wall_Timestamp", "Elapsed_Seconds", "Temp_Setpoint", "Temp_Actual"])

    def stop_logging(self):
        if self.csv_file:
            self.csv_file.close()
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
            self.ax.set_xlim(max(0, elapsed - 600), elapsed)
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
            print("Polling error:", e)

    def closeEvent(self, event):
        self.disconnect_chamber()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = ChamberGUI()
    gui.resize(800, 600)
    gui.show()
    sys.exit(app.exec_())