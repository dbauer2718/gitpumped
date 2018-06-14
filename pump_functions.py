import serial;
import time;




def pump_adr(pmp_obj, adr=0):
	pmp_obj.write('*ADR%i\r'%adr);
	time.sleep(0.5);
	output = pmp_obj.read_all();
	print(parse_output(output));

def pump_rate(pmp_obj, rat=0, adr=0):
	if not rat: pmp_obj.write('%iRAT\r'%adr); # if no rate given, this line runs
	else: pmp_obj.write('%iRAT'%adr + rat + '\r'); 
	time.sleep(0.5);
	output = pmp_obj.read_all();
	print( parse_output(output) );

def pump_stop(pmp_obj, adr=0):
	pmp_obj.write('%istp\r'%adr);
	time.sleep(0.5);
	output = pmp_obj.read_all();
	print( parse_output(output));

def pump_run(pmp_obj, adr=0):
	pmp_obj.write('%irun\r'%adr);
	time.sleep(0.5);
	output = pmp_obj.read_all();
	print( parse_output(output));

def pump_dir(pmp_obj, dir='', adr=0):
	if not dir: pmp_obj.write('%idir\r'%adr); # runs if no argument given
	if 'inf' in dir: pmp_obj.write('%idirinf\r'%adr);
	if 'wdr' in dir: pmp_obj.write('%idirwdr\r'%adr);
	else: print('ERROR: Direction must be either \'inf\' or \'wdr\' ');
	time.sleep(0.5);
	output = pmp_obj.read_all();
	print( parse_output(output));

def pump_vol(pmp_obj, vol='', adr=0):
	if not vol: pmp_obj.write('%ivol\r'%adr);
	elif type(gg) == str and str in ['ul', 'ml', 'uL', 'mL']: pmp_obj.write('%ivol'%adr + vol + '\r');
	elif type(gg) == float: pmp_obj.write('%ivol%f\r'%(adr,vol));
	else: print( 'second argument must be either omitted, units, or a number');
	time.sleep(0.5);
	output = pmp_obj.read_all();
	print( parse_output(output));
	

def pump_dia(pmp_obj, dia='', adr=0):
	BD = {'1ml':'4.699', 
		  '3ml':'8.585',
		  '5ml':'11.99',
		  '10ml':'14.43',
		  '20ml':'19.05',
		  '60ml':'26.59',
		  }
	if not dia: pmp_obj.write('%idia\r'%adr);
	elif dia in BD.keys(): pmp_obj.write('%idia'%adr + BD[dia] + '\r');
	time.sleep(0.5);
	output = pmp_obj.read_all();
	print( parse_output(output));

def initialize_pump(port='/dev/tty.usbserial'):
	return serial.Serial(port = '/dev/tty.usbserial', baudrate=19200)

def parse_output(output):
	splitout = output[:-1];
	return 'Pump ' + splitout[1:3] + ' says: ' + splitout[3:];
