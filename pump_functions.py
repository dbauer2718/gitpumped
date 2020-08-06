import serial
import time
import sys

class pump_control(object):
	def __init__(self,):
		ser_port = '/dev/tty.usbserial'
#		ser_port = 'COM1'
		"""
		This function returns a Serial object that we will use to control the pump.
		>>> import pump_functions as pf
		>>> pump_object = pump_control()
		
		"""
		try:
			print('Trying to reach the pump on {0}...'.format(ser_port))
			self.serpump = serial.Serial(port = ser_port, baudrate=19200)
			output = self.serpump.read_all() # read error code in case pump is in alarm state. this line should clear the alarm. 

		except serial.serialutil.SerialException:
			# conider for loop for trying com ports other than 1? shouldnt need to go higher than 10
			for i in range(1, 11):
				try:
					ser_port = 'COM' + str(i)
					print('Trying to reach the pump on {0}...'.format(ser_port))
					self.serpump = serial.Serial(port = ser_port, baudrate=19200)
					output = self.serpump.read_all() # read error code in case pump is in alarm state. this line should clear the alarm.
					if output == b'':
						break
				except Exception as ex2:
					type, value, traceback = sys.exc_info()
#					print(value)
					self.serpump = False
					print("ERROR: Pump is not connected to the computer, or the port is incorrect. Please see documentation for initialize_pump for troubleshooting.")
		except Exception as ex:
			type, value, traceback = sys.exc_info()
			print(type)
			print(value)
			self.serpump = False
			print("ERROR: Pump is not connected to the computer, or the port is incorrect. Please see documentation for initialize_pump for troubleshooting.")

	def _parse_output(self, output):
		output = output.decode('utf-8')
		splitout = output[:-1]
		if splitout[0] != '\x02':
			return 'ERROR: Pump response not interpretable. Your command was probably invalid.'
		else:
			return output[1:-1]



	def parse_output_fluff(self, output):
		splitout = output[:-1]
		if splitout[0] != '\x02':
			return 'ERROR: Response from pump not interpretable. Your command was probably invalid.'
	
		return 'Pump ' + splitout[1:3] + ': ' + splitout[3:]

	def serwrite(self, cmd, adr=0):
		''' Wrapper for the serial.write command. 
		'''
		self.serpump.write(cmd.encode('ascii')) # convert to binary string
		time.sleep(0.25) # give time for the pump to respond
		unparsed = self.serpump.read_all()
		return self._parse_output(unparsed)

	def rate(self, rat=0, adr=0):
		"""
		This function can be used to query or set the flow rate of the pump. Note that the flow rate will be incorrect if you have not correctly set the diameter/size of the syringe in the pump (see self.dia). Acceptable rate units are uL/mL per hour/minute. If you do not specify a rate, the command will query the pump for the current flow rate setting. You can specify a number as an int/float or as a string to include the units. The rate cannot be changed while the pump is running. Returns the response from the pump. This command can only accept a maximum of 4 significant digits, and will give an error if you include more. Include the address of the pump if you have more than one pump connected, otherwise it will default to pump 0 (the default address).
		>>> pc.rate()
		Pump 00 says: S10.00MH
		>>> pc.rate(rat=1)
		Pump 00 says: S1.00MH
		>>> pc.rate(rat='100uh')
		Pump 00 says: S100.00UH
	
		"""
		if not rat: 
			parsed_out = self.serwrite('%iRAT\r'%adr) # if no rate given, this line runs
		elif type(rat) == str: 
			parsed_out = self.serwrite('%iRAT'%adr + rat + '\r')
		elif type(rat) == float or type(rat) == int: 
			parsed_out = self.serwrite('%iRAT'%adr + str(round(rat,2)) + '\r')
		else:
			return 'ERROR: Could not interpret command. Please see documentation.'
		return parsed_out

	def adr(self, adr=0):
		# it might be worth disabling this function because i dont think people in the lab are familiar with multiple pump setups
		# not intuitive at all that you have to connect each pump individualy to the computer to change their address before you re-network them
		"""
		This function can be used to change the address of the pump currently connected to the computer. Before trying to change the address of the pump ensure that the intended pump is the only pump connected to your computer. The default address assigned is 0. This function should not be necessary unless you have more than one pump connected to your computer.
		>>> pc.adr(adr=0)
		Pump 00 says: S
		>>> pc.adr(adr=1)
		Pump 01 says: S
	
		"""
		parsed_out = self.serwrite('*ADR%i\r'%adr)
		return parsed_out


	def stop(self, adr=0):

		"""
		This function is used to stop the pump from running. I Note that telling the pump to stop while it is already stopped will cause the pump to return a "not applicable" error. All three of the below examples have the same functional behavior (the pump stops), but have slightly different return values. Include the address of the pump if you have more than one pump connected, otherwise it will default to pump 0 (the default address).
		>>> pc.stop()   # initial state of the pump was 'infusing' (running)
		Pump 00 says: P
		>>> pc.stop()  # state is 'paused' before running this command
		Pump 00 says: S
		>>> pc.stop()   # state is 'stopped' before running this command
		Pump 00 says: S?NA
	
		"""
		parsed_out = self.serwrite('%istp\r'%adr)
		return parsed_out

	def run(self, adr=0):
		"""
		This function is used to run the pump. The pump will run at the flow rate that is stored in memory, which can be queried via pump_rate. Note that you must stop the pump using pump_stop to change any properties of the pump (address, flow rate, syringe diameter, volume). Include the address of the pump if you have more than one pump connected, otherwise it will default to pump 0 (the default address).
		>>> pc.run()
		Pump 00 says: I
	
		"""
		parsed_out = self.serwrite('%irun\r'%adr)
		return parsed_out
	
	def dir(self, dir='', adr=0):
		"""
		This function can be used to query or set the direction that the pump can run. If you leave the argument 'dir' blank, the command will query the current direction setting. Acceptable values for dir are 'inf' or 'wdr' for infuse or withdraw. Include the address of the pump if you have more than one pump connected, otherwise it will default to pump 0 (the default address).
		>>> pc.dir()
		Pump 00 says: SINF
		>>> pc.dir(dir='wdr')
		Pump 00 says: S
	
		"""
		if not dir: 
			parsed_out = self.serwrite('%idir\r'%adr) # runs if no argument given
		elif 'inf' in dir or 'INF' in dir: 
			parsed_out = self.serwrite('%idirinf\r'%adr)
		elif 'wdr' in dir or 'WDR' in dir: 
			parsed_out = self.serwrite('%idirwdr\r'%adr)
		else: 
			parsed_out = 'ERROR: Direction must be either \'inf\' or \'wdr\''
		return parsed_out

	def query_dir(self, adr=0):
		'''
		Returns string (INF or WDR) representing direction of pump.
		'''
		parsed_out = self.serwrite('%idir\r'%adr)

		if 'INF' in parsed_out:
			return 'INF'
		elif 'WDR' in parsed_out:
			return 'WDR'
		else:
			return '?'

	def dia(self, adr=0, dia=''):

		"""
		This function can be used to query or set the diameter of the syringe in the pump. If you do not specify a diameter/size, the command will query the pump for the current diameter setting. Acceptable values for the "dia" argument are: '1ml', '3ml', '5ml', '10ml', '20ml', or '60ml'. Include the address of the pump if you have more than one pump connected, otherwise it will default to pump 0 (the default address). You cannot change the diameter of the pump while the pump is running.
		>>> pc.dia()
		('Pump 00 says: S11.99', 5ml')
		>>> pc.dia('60ml')
		Pump 00 says: S
	
		"""
		BD = {'1ml':'4.699', 
			  '3ml':'8.585',
			  '5ml':'11.99',
			  '10ml':'14.43',
			  '20ml':'19.05',
			  '60ml':'26.59',
			  }
		BD_lookup = {v: k for k, v in BD.items()}

		if not dia: 
			parsed_out = self.serwrite('%idia\r'%adr)
		elif dia in BD.keys(): 
			parsed_out = self.serwrite('%idia'%adr + BD[dia] + '\r')
		else:
			parsed_out = 'ERROR in interpreting command. Available syringe types: 1ml, 3ml, 5ml, 10ml, 20ml, 60ml.'
			return parsed_out

#		tmp = self._parse_output(output)
#		tmp_splt = tmp.split('says: ')
		# TODO fix this section
		if '?' in parsed_out:
			print(parsed_out)
			parsed_out = 'ERROR in interpreting command. Available syringe types: 1ml, 3ml, 5ml, 10ml, 20ml, 60ml.'
			return parsed_out
		# amend output to have diameter in mL
#		elif tmp_splt[-1][1:] in BD_lookup.keys():
		elif parsed_out[1:] in BD_lookup.keys():
			parsed_out = ' '.join([parsed_out, BD_lookup[parsed_out[1:]]])
		return parsed_out

	def vol(self, vol='', adr=0):
		"""
		This function can be used to query volume to be dispensed, set the volume to be dispensed, or set the units used in this function. If you leave the argument 'vol' blank, the command will query the current volume to be dispensed. After dispensing this volume, the pump will stop automatically. The argument 'vol' can be blank, a float, or a string denoting units ('ul' or 'ml'). If the value for 'vol' is out of range, the pump will return a '?OOR' error. Include the address of the pump if you have more than one pump connected, otherwise it will default to pump 0 (the default address).
		>>> pc.pump_vol()
		Pump 00 says: S14.53ML
		>>> pc.vol(vol='ul') # change units to microliters
		Pump 00 says: S
		>>> pc.vol(vol=3.14) # change volume to be dispensed to 3.14 UL
		Pump 00 says: S
	
		"""
		if not vol: 
			parsed_out = self.serwrite('%ivol\r'%adr)
		elif type(vol) == str and vol in ['ul', 'ml', 'uL', 'mL', 'ML', 'UL']: 
			parsed_out = self.serwrite('%ivol'%adr + vol + '\r')
		elif type(vol) == float or type(vol) == int: 
			parsed_out = self.serwrite('%ivol%.02f\r'%(adr,vol))
		else: 
			parsed_out = 'ERROR: Second argument must be either omitted, units, or a float/int'
		return parsed_out

	def reset_vol(self, dir='inf', adr=0):

		"""
		This function is used to clear the volume dispensed (see pump_querydis). The volumes dispensed in the 'infuse' and 'withdraw' directions are stored separately in memory, and must be cleared individually. The command defaults to clearing the volume dispensed in the 'infuse' direction. Include the address of the pump if you have more than one pump connected, otherwise it will default to pump 0 (the default address).
		>>> pc.reset_vol()
		Pump 00 says: S
	
		"""
		if dir not in ['inf', 'wdr']:
			parsed_out = 'ERROR: First argument must be either \'inf\' or \'wdr\''
			return parsed_out
	#	output = self.pc.write('%icld%s\r'%(adr, dir))
		parsed_out = self.serwrite('%icld'%adr + dir + '\r')
		return parsed_out

	def query_dis(self, adr=0):

		"""
		This function is used only to query the volume that the pump has dispensed since the volume has last been cleared (pump_clearvol). The pump returns the volumes dispensed in both the infuse and withdraw directions. Include the address of the pump if you have more than one pump connected, otherwise it will default to pump 0 (the default address).
		>>> pc.query_dis()
		Pump 00 says: SI1.000W0.000ML
	
		"""
		parsed_out = self.serwrite('%idis\r'%adr)
		return parsed_out
	

if __name__ == "__main__":
	# make test suite
	pc = pump_control()

	# non-moving tests:
	# Rates:
	print('\nTesting Rate function...')
	output = pc.rate()
	print('Querying pump rate:', output) # default rate=0, adr=0, should give you the current rate
	output = pc.rate(rat=1)
	print('Changing pump rate:', output)
	output = pc.rate()
	print('Confirming pump rate change:', output)
	output = pc.rate(rat='100UH')
	print('Changing rate units:', output)

	# Direction:
	print('\nTesting Direction function...')
	output = pc.dir()
	print('Querying pump direction:', output)
	output = pc.dir('WDR')
	print('Changing pump direction to withdraw:', output)
	output = pc.dir('INF')
	print('Changing pump direction to infuse:', output)
	output = pc.dir('inf')
	print('Testing case sensitivity of directions:', output)
	output = pc.query_dir()
	print('Querying pump direction using query_dir():', output)

	# Diameter:
	print('\nTesting Diameter function...')
	output = pc.dia()
	print('Querying pump diameter:', output)
	output = pc.dia(dia='60ml')
	print('Changing diamater to 60ml:', output)
#	output = pc.query_dia()
#	print('Confirming diameter changed via query_dia:', output)

	# Volume:
	print('\nTesting Volume functions...')
	output = pc.vol()
	print('Querying volume dispensed:', output)
	output = pc.vol(vol=3.14)
	print('Changing volume to be dispensed:', output)
	output = pc.vol(vol='uL')
	print('Changing volume to uL:', output)
	output = pc.vol()
	print('Confirming changes to volume dispensed:', output)
	output = pc.query_dis()
	print('Querying volume previously dispensed:', output)
	output = pc.reset_vol(dir='wdr')
	print('Resetting volume previously dispensed (wdr):', output)


	# moving tests:
	print('\nBeginning moving tests, changing parameters for safety')
	output = pc.dia(dia='5ml')
	print('Changing diamter to 5ml:', output)
	output = pc.rate(rat='1000MH')
	print('Changing rate to 1000 M/H:', output)
	output = pc.dir(dir='wdr')
	print('Changing direction to withdraw:', output)

	print('\nMOVING!')
	output = pc.run()
	print('Telling pump to begin moving:', output)
	print('Pausing for 5 seconds:')
	time.sleep(5)
	output = pc.stop()
	print('Telling the pump to stop moving:', output)
	print('STOPPED!')
	output = pc.query_dis()
	print('Querying volume dispensed:', output)
