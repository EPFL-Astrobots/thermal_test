## Class to control the thermal chamber Weiss Teknik VC 4020 via RS232
import serial
import time


class ThermalChamber:
    def __init__(self, PORT : str):
        
        self.PORT = PORT
        try:
            self.ser = serial.Serial(
                port = PORT,
                baudrate = 9600,
                bytesize = serial.EIGHTBITS,
                parity = serial.PARITY_NONE,
                stopbits = serial.STOPBITS_ONE,
                timeout = 1)
            
        except:
            print("ERROR: serial connection with thermal chamber failed")

    def close_com(self):
        """ Closes serial communication with chamber 
        """
        self.ser.close()

    def set_temperature(self, temp_value: float):
        """
        Input: 

        """

        if temp_value < -40 or temp_value > 90:
            """ 
            Lower chamber limit is -40°C
            Higher chamber limit WHITHOUT removing humidity probe is 90°C
            """
            raise("Temperature outside range [-40;90]°C")

        # Format: 5-character float, zero-padded (e.g. 0003.0) --> respect EXACTLY the number of characters here
        temp_binary = f"{temp_value:06.1f}".encode('utf-8')  # e.g. 0003.0
        command = b'$00E '+ temp_binary  + b' 0000.0 0000.0 0000.0 0000.0 0000.0 0000.0' + b' 01010000010101010000010101000000' + b'\r'
        print(f"Sending: {repr(command.strip())}")
        self.ser.write(command)
        time.sleep(0.5)
        response = self.ser.readline().decode(errors='ignore').strip()
        print(f"Response: {repr(response)}")

    def read_temperature(self):
        self.ser.write(b'$00I\r')  # Or use appropriate command
        response = self.ser.readline()
        raw = response.decode(errors='ignore').strip().split(' ')

        return raw

    def turn_off_chamber(self):

        """
        Stops chamber active control, but does not switch off power
        """

        command = b'$00E 0000.0 0000.0 0000.0 0000.0 0000.0 0000.0 0000.0' + b' 00000000000000000000000000000000' + b'\r'
        print(f"Sending: {repr(command.strip())}")
        self.ser.write(command)
        time.sleep(0.5)
        response = self.ser.readline().decode(errors='ignore').strip()
        print(f"Response: {repr(response)}")

if __name__ == '__main__':
    #%%
    from classThermalChamber import ThermalChamber
    PORT = 'COM5'
    thermal = ThermalChamber(PORT)
    #%%
    temp_value = 20
    thermal.set_temperature(temp_value)

    #%%
    thermal.turn_off_chamber()
    #%%
    thermal.close_com()