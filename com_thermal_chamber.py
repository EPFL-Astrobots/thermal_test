import serial

ser = serial.Serial(
    port='COM3',        # Change to your port
    baudrate=9600,      # Match the chamber setting
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=1           # seconds
)
# 

ser.write(b'$00I\r')  # Command to read temperature
response = ser.readline()
fields = response.decode(errors='ignore').strip().split(' ')
# print('Response:', response.decode(errors='ignore').strip().split(','))
print(f'Temperature setpoint: {float(fields[0])} °C')
print(f'Temperature current: {float(fields[1])} °C')
print(f'Humidity setpoint: {float(fields[2])} %')
print(f'Humidity current: {float(fields[3])} %')
ser.close()