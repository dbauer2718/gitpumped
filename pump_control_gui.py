import numpy as np
import PyQt5 as qt
from matplotlib.backends.backend_qt5agg import FigureCanvas
from pump_functions import pump_control


class pump_gui(qt.QtWidgets.QDialog):
	def __init__(self, verbose=False, test_gui=False):
		super(pump_gui, self).__init__()
		
		self.pc = pump_control()
		self.verbose = verbose
		self.test_gui = test_gui
		if self.pc.serpump == False and test_gui == False:
			print('Could not establish communication with pump, exiting.')
			self.close()
			return
		elif self.pc.serpump == False and test_gui == True:
			print('Could not establish communication with pump. Disabling button functionality.')
		
		# init GUI
		grid = qt.QtWidgets.QGridLayout()
		grid.setSpacing(7) 

		# layout should be: 
		# pump number (label), size(dropdown), direction (label), rate (text box), reverse_direction (button)
		
		# add labels for the layout
		self.header_pumpNum = qt.QtWidgets.QLabel('Pump Number')
		self.header_syrSize = qt.QtWidgets.QLabel('Syringe Size')
		self.header_pumpRate = qt.QtWidgets.QLabel('Pump Rate (uL/hr)')
		self.header_pumpDir = qt.QtWidgets.QLabel('Pump Direction')
		self.header_pumpStatus = qt.QtWidgets.QLabel('Pump Status')
		grid.addWidget(self.header_pumpNum, 1, 1) # does this start at 0 or 1??
		grid.addWidget(self.header_syrSize, 1, 2)
		grid.addWidget(self.header_pumpRate, 1, 3)
		grid.addWidget(self.header_pumpDir, 1, 4)
		grid.addWidget(self.header_pumpStatus, 1, 6)
		
		# temp
		self.num_pumps = 1 # change this later to be number of pumps found

		# initialize dictionaries containing labels, buttons, etc
		self.pumpNum = {}
		self.syrSize = {}
		self.pumpDir = {}
		self.pumpRate = {}
		self.primebtn = {}
		self.revbtn = {}
		self.pumpStatus = {}

		for row in range(self.num_pumps):
			# add the stuff 
			self.pumpNum[row] = qt.QtWidgets.QLabel(str(row))
			self.syrSize[row] = qt.QtWidgets.QComboBox()
			self.pumpRate[row] = qt.QtWidgets.QLineEdit()
			self.pumpDir[row] = qt.QtWidgets.QLabel('')
			self.revbtn[row] = qt.QtWidgets.QPushButton('Reverse Direction', self)
			self.pumpStatus[row] = qt.QtWidgets.QLabel('')
			# indexing starts at 1, and row 1 is headers, so we add 2 to row to get
			# to first non-header row
			grid.addWidget(self.pumpNum[row], row + 2, 1)
			grid.addWidget(self.syrSize[row], row + 2, 2)
			grid.addWidget(self.pumpRate[row], row + 2, 3)
			grid.addWidget(self.pumpDir[row], row + 2, 4)
			grid.addWidget(self.revbtn[row], row + 2, 5)
			grid.addWidget(self.pumpStatus[row], row + 2, 6)

			# connecting thigns to their appropriate function
			if test_gui == False:
				self.syrSize[row].activated.connect(self.change_dia(row))
				self.pumpRate[row].editingFinished(self.update_rate(row))
				self.revbtn[row].clicked.connect(self.reverse_direction(row))

		self.runbtn = qt.QtWidgets.QPushButton('Run/Update', self)
		self.stopbtn = qt.QtWidgets.QPushButton('Stop', self)

		grid.addWidget(self.runbtn, row + 3, 4)
		grid.addWidget(self.stopbtn, row + 3, 5)

		# connect run and stop
		# TODO: eventually fix these to work with more than 1 pump
		if test_gui == False:
			self.runbtn.clicked.connect(self.run(0)) # will not work with more than 1 pump
			self.stopbtn.clicked.connect(self.stop(0)) # will not work with more than 1 pump
		

		self.setLayout(grid)
		self.setWindowTitle('Pump Control')
		self.show()


	def reverse_direction(self, row):
		''' 
		'''
		self.stopbtn.setChecked(1)
		self.revbtn[row].setChecked(1)
		self.stop()
		# send serial command to reverse
		adr = self.row2adr(row)
		init_dir = self.pc.quer_dir(adr)
		if init_dir == 'INF':
			status = self.pc.dir(dir='wdr', adr=adr)
		elif init_dir == 'wdr':
			status = self.pc.dir(dir='inf', adr=adr)
		else:
			status = 'Error'
		self.pumpDir[row].setText(status)

	def stop(self, row):
		self.stopbtn.setChecked(1)
		self.runbtn.setChecked(0)
#		adr = self.row2adr(row)
		# this will only run once if 1 pump connected
		for adr in self.num_pumps:
			status = self.pc.stop(adr=adr)
		# set status to stopped
		self.pumpStatus[row].setText(status)

	def run(self, row):
		self.runbtn.setChecked(1)
		self.stopbtn.setChecked(0)
		for adr in self.num_pumps:
			status = self.pc.run(adr=adr)
		self.pumpStatus[row].setText(status)

	def change_dia(self, row):
		self.runbtn.setChecked(0)
		self.stopbtn.setChecked(1)
		self.stop(row)
		adr = self.row2adr(row)
		size = self.syrSize[row].currentText()
		status = self.pc.dia(adr=adr, dia=size)
		self.pumpStatus[row].setText(status)

	def update_rate(self, row):
		self.runbtn.setChecked(0)
		self.stopbtn.setChecked(1)
		self.stop(row)
		adr = self.row2adr(row)
		try:
			rate = float(self.pumpRate[row].text())
			status = self.pc.rate(rat=rate, adr=adr)
		except ValueError:
			status = 'Could not convert rate to float. Please give a valid float.'
		self.pumpStatus[row].setText(status)
		

	def row2adr(self, row):
		'''
		Input row, output pump address
		'''
		# since we have never used more than 1 pump, this will do for now
		if self.num_pumps==1:
			return 0 
		# TODO: actually turn row into adr
		


if __name__ == "__main__":
	app = qt.QtWidgets.QApplication([])
	pc = pump_gui(test_gui=False)
	app.exec_()
