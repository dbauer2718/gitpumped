import serial;
import time;
import sys;


def pump_adr(pmp_obj, adr=0):
	"""
	This function can be used to change the address of the pump currently connected to the computer. Before trying to change the address of the pump ensure that the intended pump is the only pump connected to your computer. The default address assigned is 0. This function should not be necessary unless you have more than one pump connected to your computer.
	>>> pf.pump_adr(pump_object, adr=0)
	Pump 00 says: S
	>>> pf.pump_adr(pump_object, adr=1)
	Pump 01 says: S

	"""
	pmp_obj.write('*ADR%i\r'%adr);
	time.sleep(0.5);
	output = pmp_obj.read_all();
	print(parse_output(output));

def pump_rate(pmp_obj, rat=0, adr=0):
	"""
	This function can be used to query or set the flow rate of the pump. Note that the flow rate will be incorrect if you have not correctly set the diameter/size of the syringe in the pump (see pump_dia). Acceptable rate units are uL/mL per hour/minute. If you do not specify a rate, the command will query the pump for the current flow rate setting. You can specify a number as an int/float or as a string to include the units. The rate cannot be changed while the pump is running. Returns the response from the pump. This command can only accept a maximum of 4 significant digits, and will give an error if you include more. Include the address of the pump if you have more than one pump connected, otherwise it will default to pump 0 (the default address).
	>>> pf.pump_rate(pump_object)
	Pump 00 says: S10.00MH
	>>> pf.pump_rate(pump_object, rat=1)
	Pump 00 says: S1.00MH
	>>> pf.pump_rate(pump_object, rat='100uh')
	Pump 00 says: S100.00UH

	"""
	if not rat: pmp_obj.write('%iRAT\r'%adr); # if no rate given, this line runs
	elif type(rat) == str: pmp_obj.write('%iRAT'%adr + rat + '\r'); 
	elif type(rat) == float or type(rat) == int: 
		pmp_obj.write('%iRAT'%adr + str(round(rat,2)) + '\r'); 
	else:
		print('ERROR: Could not interpret command. Please see documentation.');
	time.sleep(0.5);
	output = pmp_obj.read_all();
	print( parse_output(output) );

def pump_stop(pmp_obj, adr=0):
	"""
	This function is used to stop the pump from running. I Note that telling the pump to stop while it is already stopped will cause the pump to return a "not applicable" error. All three of the below examples have the same functional behavior (the pump stops), but have slightly different return values. Include the address of the pump if you have more than one pump connected, otherwise it will default to pump 0 (the default address).
	>>> pf.pump_stop(pump_object)   # initial state of the pump was 'infusing' (running)
	Pump 00 says: P
	>>> pf.pump_stop(pump_object)  # state is 'paused' before running this command
	Pump 00 says: S
	>>> pf.pump_stop(pump_object)   # state is 'stopped' before running this command
	Pump 00 says: S?NA

	"""
	pmp_obj.write('%istp\r'%adr);
	time.sleep(0.5);
	output = pmp_obj.read_all();
	print( parse_output(output));

def pump_run(pmp_obj, adr=0):
	"""
	This function is used to run the pump. The pump will run at the flow rate that is stored in memory, which can be queried via pump_rate. Note that you must stop the pump using pump_stop to change any properties of the pump (address, flow rate, syringe diameter, volume). Include the address of the pump if you have more than one pump connected, otherwise it will default to pump 0 (the default address).
	>>> pf.pump_run(pump_object)
	Pump 00 says: I

	"""
	pmp_obj.write('%irun\r'%adr);
	time.sleep(0.5);
	output = pmp_obj.read_all();
	print( parse_output(output));

def pump_dir(pmp_obj, dir='', adr=0):
	"""
	This function can be used to query or set the direction that the pump can run. If you leave the argument 'dir' blank, the command will query the current direction setting. Acceptable values for dir are 'inf' or 'wdr' for infuse or withdraw. Include the address of the pump if you have more than one pump connected, otherwise it will default to pump 0 (the default address).
	>>> pf.pump_dir(pump_object)
	Pump 00 says: SINF
	>>> pf.pump_dir(pump_object, dir='wdr')
	Pump 00 says: S

	"""
	if not dir: 
		pmp_obj.write('%idir\r'%adr); # runs if no argument given
	elif 'inf' in dir: pmp_obj.write('%idirinf\r'%adr);
	elif 'wdr' in dir: pmp_obj.write('%idirwdr\r'%adr);
	else: print('ERROR: Direction must be either \'inf\' or \'wdr\' ');
	time.sleep(0.5);
	output = pmp_obj.read_all();
	print( parse_output(output));

def pump_vol(pmp_obj, vol='', adr=0):
	"""
	This function can be used to query volume to be dispensed, set the volume to be dispensed, or set the units used in this function. If you leave the argument 'vol' blank, the command will query the current volume to be dispensed. After dispensing this volume, the pump will stop automatically. The argument 'vol' can be blank, a float, or a string denoting units ('ul' or 'ml'). If the value for 'vol' is out of range, the pump will return a '?OOR' error. Include the address of the pump if you have more than one pump connected, otherwise it will default to pump 0 (the default address).
	>>> pf.pump_vol(pump_object)
	Pump 00 says: S14.53ML
	>>> pf.pump_vol(pump_object, vol='ul') # change units to microliters
	Pump 00 says: S
	>>> pf.pump_vol(pump_object, vol=3.14) # change volume to be dispensed to 3.14 UL
	Pump 00 says: S

	"""
	if not vol: 
		pmp_obj.write('%ivol\r'%adr);
	elif type(vol) == str and vol in ['ul', 'ml', 'uL', 'mL', 'ML', 'UL']: pmp_obj.write('%ivol'%adr + vol + '\r');
	elif type(vol) == float or type(vol) == int: pmp_obj.write('%ivol%.02f\r'%(adr,vol));
	else: print( 'ERROR: Second argument must be either omitted, units, or a float/int');
	time.sleep(0.5);
	output = pmp_obj.read_all();
	print( parse_output(output));
	
def pump_clearvol(pmp_obj, dir='inf', adr=0):
	"""
	This function is used to clear the volume dispensed (see pump_querydis). The volumes dispensed in the 'infuse' and 'withdraw' directions are stored separately in memory, and must be cleared individually. The command defaults to clearing the volume dispensed in the 'infuse' direction. Include the address of the pump if you have more than one pump connected, otherwise it will default to pump 0 (the default address).
	>>> pf.pump_clearvol(pump_object)
	Pump 00 says: S

	"""
	if dir not in ['inf', 'wdr']:
		print('ERROR: Second argument must be either \'inf\' or \'wdr\'');
		return;
#	output = pmp_obj.write('%icld%s\r'%(adr, dir));
	error = pmp_obj.write('%icld'%adr + dir + '\r');
	time.sleep(0.5);
	output = pmp_obj.read_all()
	print( parse_output(output));

def pump_querydis(pmp_obj, adr=0):
	"""
	This function is used only to query the volume that the pump has dispensed since the volume has last been cleared (pump_clearvol). The pump returns the volumes dispensed in both the infuse and withdraw directions. Include the address of the pump if you have more than one pump connected, otherwise it will default to pump 0 (the default address).
	>>> pf.pump_querydis(pump_object)
	Pump 00 says: SI1.000W0.000ML

	"""
	pmp_obj.write('%idis\r'%adr);
	time.sleep(0.5);
	output = pmp_obj.read_all()
	print( parse_output(output));

def pump_dia(pmp_obj, dia='', adr=0):
	"""
	This function can be used to query or set the diameter of the syringe in the pump. If you do not specify a diameter/size, the command will query the pump for the current diameter setting. Acceptable values for the "dia" argument are: '1ml', '3ml', '5ml', '10ml', '20ml', or '60ml'. Include the address of the pump if you have more than one pump connected, otherwise it will default to pump 0 (the default address). You cannot change the diameter of the pump while the pump is running.
	>>> pf.pump_dia(pump_object)
	('Pump 00 says: S11.99', 5ml')
	>>> pf.pump_dia(pump_object, '60ml')
	Pump 00 says: S

	"""
	BD = {'1ml':'4.699', 
		  '3ml':'8.585',
		  '5ml':'11.99',
		  '10ml':'14.43',
		  '20ml':'19.05',
		  '60ml':'26.59',
		  }
	BD_lookup = {v: k for k, v in BD.iteritems()};
	if not dia: 
		pmp_obj.write('%idia\r'%adr);
	elif dia in BD.keys(): pmp_obj.write('%idia'%adr + BD[dia] + '\r');
	else:
		print('ERROR in interpreting command. Available syringe types: 1ml, 3ml, 5ml, 10ml, 20ml, 60ml.');
		return
	time.sleep(0.5);
	output = pmp_obj.read_all();
	tmp = parse_output(output);
	tmp_splt = tmp.split('says: ');
	if '?' in tmp:
		print(tmp);
		print('ERROR in interpreting command. Available syringe types: 1ml, 3ml, 5ml, 10ml, 20ml, 60ml.');
	elif tmp_splt[-1][1:] in BD_lookup.keys():
		print(tmp, BD_lookup[tmp_splt[-1][1:]]);
	else:
		print(tmp);


def initialize_pump(port='/dev/tty.usbserial'):
	"""
	This function returns a Serial object that we will pass to all functions used to control the pump. You must run this first to initialize communication with the pump.
	>>> import pump_functions as pf
	>>> pump_object = pf.initialize_pump()

	"""
	try:
		pu = serial.Serial(port = '/dev/tty.usbserial', baudrate=19200);
		output = pu.read_all(); # read error code in case pump is in alarm state. this line should clear the alarm. 
		return pu;
	except Exception as ex:
		type, value, traceback = sys.exc_info();
		print(value);
		print("ERROR: Pump is not connected to the computer, or the port is incorrect. Please see documentation for initialize_pump for troubleshooting.");


def parse_output(output):
	splitout = output[:-1];
	if splitout[0] != '\x02':
		return 'ERROR: Response from pump not interpretable. Your command was probably invalid.'

	return 'Pump ' + splitout[1:3] + ' says: ' + splitout[3:];
