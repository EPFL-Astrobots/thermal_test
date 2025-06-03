import serial
import time
import csv
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque

# Config
ROLLING_WINDOW_SECONDS = 300  # Show only last 5 minutes
PORT = 'COM3'
NOW_TIME = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
LOG_FILE = NOW_TIME + 'chamber_log.csv'
MAX_POINTS = 100  # max points in graph
start_time = time.time()

# Setup serial
ser = serial.Serial(
    port=PORT,
    baudrate=9600,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=1
)

# Setup CSV
log_file = open(LOG_FILE, mode='a', newline='')
csv_writer = csv.writer(log_file)
if log_file.tell() == 0:
    csv_writer.writerow([
        'Wall_Timestamp',
        'Elapsed_Seconds',
        'Temp_Setpoint',
        'Temp_Actual',
        'Humidity_Setpoint',
        'Humidity_Actual'
    ])

# Buffers for plotting
timestamps = []
temp_set = []
temp_actual = []
humidity_set = []
humidity_actual = []

# Plot setup
fig, ax = plt.subplots()
line_temp = ax.plot([], [], label='Temp Actual (°C)', color='red')[0]
line_temp_set = ax.plot([], [], label='Temp Setpoint', color='orange', linestyle='dashed')[0]
line_humidity = ax.plot([], [], label='Humidity Actual (%)', color='blue')[0]
line_humidity_set = ax.plot([], [], label='Humidity Setpoint', color='green', linestyle='dashed')[0]
ax.set_xlabel('Time (s since start)')
ax.set_ylabel('Values')
ax.legend()
plt.title("Live Chamber Data")

def parse_response(raw):
    try:
        return [float(f) for f in raw.split(' ')]
    except ValueError:
        return []

def update(frame):
    global ser
    elapsed_seconds = round(time.time() - start_time, 2)
    try:
        ser.write(b'$00I\r')  # Or use appropriate command
        response = ser.readline()
        raw = response.decode(errors='ignore').strip().split(' ')
        values = [float(f) for f in raw[:4]]  # Expecting 4 values: T_set, T_act, H_set, H_act
        print(len(values), values)

        if len(values) >= 4:
            now = datetime.now().strftime("%H:%M:%S")
            t_set, t_act, h_set, h_act = values[0], values[1], values[2], values[3]

            # Append to buffers
            timestamps.append(elapsed_seconds)
            temp_set.append(t_set)
            temp_actual.append(t_act)
            humidity_set.append(h_set)
            humidity_actual.append(h_act)

            while timestamps and elapsed_seconds - timestamps[0] > ROLLING_WINDOW_SECONDS:
                timestamps.pop(0)
                temp_set.pop(0)
                temp_actual.pop(0)
                humidity_set.pop(0)
                humidity_actual.pop(0)

            # Log to CSV
            csv_writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            elapsed_seconds, t_set, t_act, h_set, h_act])
            log_file.flush()

            # Update plot
            x = list(timestamps)
            line_temp.set_data(x, temp_actual)
            line_temp_set.set_data(x, temp_set)
            line_humidity.set_data(x, humidity_actual)
            line_humidity_set.set_data(x, humidity_set)

            if x:
                ax.set_xlim(x[0], x[-1])
                ymin = min(temp_actual + temp_set + humidity_actual + humidity_set) - 5
                ymax = max(temp_actual + temp_set + humidity_actual + humidity_set) + 5
                ax.set_ylim(ymin, ymax)

            print(f"Time: {now}, Temp Setpoint: {t_set} °C, Temp Actual: {t_act} °C, ")

    except Exception as e:
        print(f"Error: {e}")

    return line_temp, line_temp_set, line_humidity, line_humidity_set

ani = FuncAnimation(fig, update, interval=5000)
plt.tight_layout()
plt.show()

# Cleanup
log_file.close()
ser.close()