import serial

### SET THESE PARAMETERS HERE
serial_port = '/dev/tty.usbserial'
#serial_port = 'COM1' # windows, may have to check device manager to check which COM port is assigned
pump_number = 1


### LEAVE EVERYTHING BELOW HERE THE SAME
def print_pump_number(ser,tot_range=100):
    for i in range(tot_range):
        ser.write(b'%iADR\x0D'%i)
        output = ser.readline()
        if len(output)>0:
            print('current pump set to %i'%i)
            break

ser = serial.Serial(serial_port,19200,timeout=0.1)
print_pump_number(ser)
print('setting pump to %i'%pump_number)
ser.write(b'*ADR%iB19200\x0D'%pump_number)
ser.readline()
print_pump_number(ser)
ser.close()
