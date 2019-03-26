#!/usr/bin/python
import time
import usb
import hal
from ctypes import c_int8

# pip install --index-url=https://pypi.python.org/simple/ libusb1
#find device
class mpg:
	def __init__(self,idVendor=0x10CE, idProduct=0xEB93):
		self.hal_init()
		self.idVendor = idVendor
		self.idProduct = idProduct
		self.connected = True
		# find our device
		self.dev = usb.core.find(idVendor=self.idVendor, idProduct=self.idProduct)

		# was it found?
		if self.dev is None:
    			raise ValueError('Device not found')
		reattach = False
		if self.dev.is_kernel_driver_active(0):
    			reattach = True
    			self.dev.detach_kernel_driver(0)
		# set the active configuration. With no arguments, the first
		# configuration will be the active one
		self.dev.set_configuration()
		# get an endpoint instance
		self.cfg = self.dev.get_active_configuration()
		self.intf = self.cfg[(0,0)]
		self.endpoint = self.intf[0]		
		#print self.endpoint.bEndpointAddress
		self.wheel_count = 0
	def poll(self):
		try:
			data = None#[]*32
			data = mpg.dev.read(
				mpg.endpoint.bEndpointAddress,
				mpg.endpoint.wMaxPacketSize
				)
			self.decode_input(data)
		except usb.core.USBError as e:
			data = None
			if e.args == ('Operation time out',):
				return False
		return True		
	def hal_init(self):
		self.halcomp = hal.component("hal_mpg")
		self.halcomp.newpin("button-reset",hal.HAL_BIT,hal.HAL_OUT)
		self.halcomp.newpin("button-stop",hal.HAL_BIT,hal.HAL_OUT)
		self.halcomp.newpin("button-rewind",hal.HAL_BIT,hal.HAL_OUT)
		self.halcomp.newpin("button-feed-inc",hal.HAL_BIT,hal.HAL_OUT)
		self.halcomp.newpin("button-feed-dec",hal.HAL_BIT,hal.HAL_OUT)
		self.halcomp.newpin("button-spindle-inc",hal.HAL_BIT,hal.HAL_OUT)
		self.halcomp.newpin("button-spindle-dec",hal.HAL_BIT,hal.HAL_OUT)
		self.halcomp.newpin("button-home",hal.HAL_BIT,hal.HAL_OUT)
		self.halcomp.newpin("button-safe-z",hal.HAL_BIT,hal.HAL_OUT)
		self.halcomp.newpin("button-origin",hal.HAL_BIT,hal.HAL_OUT)
		self.halcomp.newpin("button-spindle-on",hal.HAL_BIT,hal.HAL_OUT)
		self.halcomp.newpin("button-probe-z",hal.HAL_BIT,hal.HAL_OUT)

		self.halcomp.newpin("button-macro1",hal.HAL_BIT,hal.HAL_OUT)
		self.halcomp.newpin("button-macro2",hal.HAL_BIT,hal.HAL_OUT)
		self.halcomp.newpin("button-macro3",hal.HAL_BIT,hal.HAL_OUT)
		self.halcomp.newpin("button-macro4",hal.HAL_BIT,hal.HAL_OUT)
		self.halcomp.newpin("button-macro5",hal.HAL_BIT,hal.HAL_OUT)
		self.halcomp.newpin("button-macro6",hal.HAL_BIT,hal.HAL_OUT)
		self.halcomp.newpin("button-macro7",hal.HAL_BIT,hal.HAL_OUT)
		self.halcomp.newpin("button-macro8",hal.HAL_BIT,hal.HAL_OUT)
		self.halcomp.newpin("button-macro9",hal.HAL_BIT,hal.HAL_OUT)
		self.halcomp.newpin("button-macro10",hal.HAL_BIT,hal.HAL_OUT)

		self.halcomp.newpin("button-continuous",hal.HAL_BIT,hal.HAL_OUT)
		self.halcomp.newpin("button-step",hal.HAL_BIT,hal.HAL_OUT)
		
		self.halcomp.newpin("jog-scale",hal.HAL_FLOAT,hal.HAL_OUT)
		self.halcomp.newpin("gen-scale",hal.HAL_FLOAT,hal.HAL_OUT)
		self.halcomp.newpin("wheel-count",hal.HAL_S32,hal.HAL_OUT)
		
		self.halcomp.newpin("select-x",hal.HAL_BIT,hal.HAL_OUT)
		self.halcomp.newpin("select-y",hal.HAL_BIT,hal.HAL_OUT)
		self.halcomp.newpin("select-z",hal.HAL_BIT,hal.HAL_OUT)
		self.halcomp.newpin("select-a",hal.HAL_BIT,hal.HAL_OUT)
		self.halcomp.newpin("select-b",hal.HAL_BIT,hal.HAL_OUT)
		self.halcomp.newpin("select-c",hal.HAL_BIT,hal.HAL_OUT)
		self.halcomp.ready()
		

	def decode_input(self, data=None):
		header = data[0]
		random = data[1]
		button1 = data[2]
		button2 = data[3]
		override = data[4]
		axis = data[5]
		pulse = data[6]
		crc = data[7]
		
		if header == 0x04:
			#print axis
			#axis rotary switch
			if axis == 17:
				self.halcomp["select-x"] = True			
				self.halcomp["select-y"] = False			
				self.halcomp["select-z"] = False		
				self.halcomp["select-a"] = False		
				self.halcomp["select-b"] = False		
				self.halcomp["select-c"] = False		
			elif axis == 18:
				self.halcomp["select-x"] = False			
				self.halcomp["select-y"] = True			
				self.halcomp["select-z"] = False		
				self.halcomp["select-a"] = False		
				self.halcomp["select-b"] = False		
				self.halcomp["select-c"] = False		
			elif axis == 19:
				self.halcomp["select-x"] = False			
				self.halcomp["select-y"] = False			
				self.halcomp["select-z"] = True		
				self.halcomp["select-a"] = False		
				self.halcomp["select-b"] = False		
				self.halcomp["select-c"] = False		
			elif axis == 20:
				self.halcomp["select-x"] = False			
				self.halcomp["select-y"] = False			
				self.halcomp["select-z"] = False		
				self.halcomp["select-a"] = True		
				self.halcomp["select-b"] = False		
				self.halcomp["select-c"] = False		
			elif axis == 21:
				self.halcomp["select-x"] = False			
				self.halcomp["select-y"] = False			
				self.halcomp["select-z"] = False		
				self.halcomp["select-a"] = False		
				self.halcomp["select-b"] = True		
				self.halcomp["select-c"] = False		
			elif axis == 22:
				self.halcomp["select-x"] = False			
				self.halcomp["select-y"] = False			
				self.halcomp["select-z"] = False		
				self.halcomp["select-a"] = False		
				self.halcomp["select-b"] = False		
				self.halcomp["select-c"] = True		
			else:
				self.halcomp["select-x"] = False			
				self.halcomp["select-y"] = False			
				self.halcomp["select-z"] = False		
				self.halcomp["select-a"] = False		
				self.halcomp["select-b"] = False		
				self.halcomp["select-c"] = False

			#scale rotary switch
			if override == 13:
				self.halcomp["jog-scale"] = 0.001
				self.halcomp["gen-scale"] = 0.02
			if override == 14:
				self.halcomp["jog-scale"] = 0.01
				self.halcomp["gen-scale"] = 0.05
			if override == 15:
				self.halcomp["jog-scale"] = 0.1
				self.halcomp["gen-scale"] = 0.1
			if override == 16:
				self.halcomp["jog-scale"] = 1
				self.halcomp["gen-scale"] = 0.3
			if override == 26:
				self.halcomp["gen-scale"] = 0.6
			if override == 27:
				self.halcomp["gen-scale"] = 1
			if override == 28:
				self.halcomp["gen-scale"] = 1.5
			#wheel 
			self.wheel_count = self.wheel_count + c_int8(data[6]).value
			self.halcomp["wheel-count"] =  self.wheel_count
						
			#button  mapping
			if button1 == 1:
				self.halcomp["button-reset"] = True
			else :
				self.halcomp["button-reset"] = False
			if button1 == 2:
				self.halcomp["button-stop"] = True
			else :
				self.halcomp["button-stop"] = False
			if button1 == 3:
				self.halcomp["button-rewind"] = True
			else :
				self.halcomp["button-rewind"] = False
			if button1 == 4:
				self.halcomp["button-feed-inc"] = True
			else :
				self.halcomp["button-feed-inc"] = False
			if button1 == 5:
				self.halcomp["button-feed-dec"] = True
			else :
				self.halcomp["button-feed-dec"] = False
			if button1 == 6:
				self.halcomp["button-spindle-inc"] = True
			else :
				self.halcomp["button-spindle-inc"] = False
			if button1 == 7:
				self.halcomp["button-spindle-dec"] = True
			else :
				self.halcomp["button-spindle-dec"] = False
			if button1 == 8:
				self.halcomp["button-home"] = True
			else :
				self.halcomp["button-home"] = False
			if button1 == 9:
				self.halcomp["button-safe-z"] = True
			else :
				self.halcomp["button-safe-z"] = False
			if button1 == 10:
				self.halcomp["button-origin"] = True
			else :
				self.halcomp["button-origin"] = False
			if button1 == 11:
				self.halcomp["button-spindle-on"] = True
			else :
				self.halcomp["button-spindle-on"] = False
			if button1 == 13:
				self.halcomp["button-probe-z"] = True
			else :
				self.halcomp["button-probe-z"] = False
			if button1 == 14:
				self.halcomp["button-continuous"] = True
			else :
				self.halcomp["button-continuous"] = False
			if button1 == 15:
				self.halcomp["button-step"] = True
			else :
				self.halcomp["button-step"] = False
			if button1 == 16:
				self.halcomp["button-macro10"] = True
			else :
				self.halcomp["button-macro10"] = False
			if button1 == 12:
				if button2 == 4:
					self.halcomp["button-macro1"] = True
				else :
					self.halcomp["button-macro1"] = False
				if button2 == 5:
					self.halcomp["button-macro2"] = True
				else :
					self.halcomp["button-macro2"] = False
				if button2 == 6:
					self.halcomp["button-macro3"] = True
				else :
					self.halcomp["button-macro3"] = False
				if button2 == 7:
					self.halcomp["button-macro4"] = True
				else :
					self.halcomp["button-macro4"] = False
				if button2 == 8:
					self.halcomp["button-macro5"] = True
				else :
					self.halcomp["button-macro5"] = False
				if button2 == 9:
					self.halcomp["button-macro6"] = True
				else :
					self.halcomp["button-macro6"] = False
				if button2 == 10:
					self.halcomp["button-macro7"] = True
				else :
					self.halcomp["button-macro7"] = False
				if button2 == 11:
					self.halcomp["button-macro8"] = True
				else :
					self.halcomp["button-macro8"] = False
				if button2 == 13:
					self.halcomp["button-macro9"] = True
				else :
					self.halcomp["button-macro9"] = False
				if button2 == 16:
					self.halcomp["button-macro10"] = True
				else :
					self.halcomp["button-macro10"] = False
			else:
				self.halcomp["button-macro1"] = False
				self.halcomp["button-macro2"] = False
				self.halcomp["button-macro3"] = False
				self.halcomp["button-macro4"] = False
				self.halcomp["button-macro5"] = False
				self.halcomp["button-macro6"] = False
				self.halcomp["button-macro7"] = False
				self.halcomp["button-macro8"] = False
				self.halcomp["button-macro9"] = False
				self.halcomp["button-macro10"] = False
			
			
if __name__=="__main__":
	buffer  = []*32		
	mpg = mpg()
	#print mpg.connected
	try:
		while True:
			if not mpg.poll():
				continue
	except KeyboardInterrupt:
		raise SystemExit
