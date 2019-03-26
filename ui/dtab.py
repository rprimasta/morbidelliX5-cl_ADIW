import linuxcnc
import thread
import time
import os
import hal
import hal_glib
import gscreen
import json
import gobject

def get_handlers(halcomp,builder,useropts):
        return [multiTable(halcomp,builder, useropts)]

class multiTable:
	Filename = "brokerProg.json"
	lastRun = False

	#DATUM T1
	datum_x1 = 247.331
	datum_y1 = -112.662
	datum_z1 = -304.637
	#DATUM T2
	datum_x2 = 2580.05
	datum_y2 = -112.662
	datum_z2 = -304.637
	#DATUM o1
	offs_x1 = 0.0
	offs_y1 = 0.0
	offs_z1 = 0.0
	#DATUM o2
	offs_x2 = 0.0
	offs_y2 = 0.0
	offs_z2 = 0.0

	ab_active_st = False
	cd_active_st = False

	ab_filename = None
	cd_filename = None

	ab_qty = 0
	cd_qty = 0

        def __init__(self,halcomp,builder,useropts):
                hal_glib.GPin(halcomp.newpin('debug_currProg', hal.HAL_U32, hal.HAL_OUT))
                hal_glib.GPin(halcomp.newpin('debug_numQueue', hal.HAL_U32, hal.HAL_OUT))

                hal_glib.GPin(halcomp.newpin('machine-on', hal.HAL_BIT, hal.HAL_IN))
                hal_glib.GPin(halcomp.newpin('force_unlock_table_ab', hal.HAL_BIT, hal.HAL_IN))
                hal_glib.GPin(halcomp.newpin('force_unlock_table_cd', hal.HAL_BIT, hal.HAL_IN))
                hal_glib.GPin(halcomp.newpin('abort_signal', hal.HAL_BIT, hal.HAL_IN))
                hal_glib.GPin(halcomp.newpin('prog-is-idle', hal.HAL_BIT, hal.HAL_IN))
                hal_glib.GPin(halcomp.newpin('prog-is-run', hal.HAL_BIT, hal.HAL_IN))
                hal_glib.GPin(halcomp.newpin('hal_tbl_ab_active', hal.HAL_BIT, hal.HAL_OUT))
                hal_glib.GPin(halcomp.newpin('hal_tbl_cd_active', hal.HAL_BIT, hal.HAL_OUT))
                hal_glib.GPin(halcomp.newpin('hal_tbl_ab_lock', hal.HAL_BIT, hal.HAL_OUT))
                hal_glib.GPin(halcomp.newpin('hal_tbl_cd_lock', hal.HAL_BIT, hal.HAL_OUT))
                hal_glib.GPin(halcomp.newpin('hal_start_a', hal.HAL_BIT, hal.HAL_IN))
                hal_glib.GPin(halcomp.newpin('hal_start_b', hal.HAL_BIT, hal.HAL_IN))
                hal_glib.GPin(halcomp.newpin('hal_start_c', hal.HAL_BIT, hal.HAL_IN))
                hal_glib.GPin(halcomp.newpin('hal_start_d', hal.HAL_BIT, hal.HAL_IN))
                self.halcomp = halcomp
                self.builder = builder
		self.builder.get_object("togglebutton1").set_sensitive(False)
		self.builder.get_object("togglebutton2").set_sensitive(False)
	        self.builder.get_object("exOffsABx").set_range(-999999.999,999999.999)
	        self.builder.get_object("exOffsABy").set_range(-999999.999,999999.999)
	        self.builder.get_object("exOffsABz").set_range(-999999.999,999999.999)
	        self.builder.get_object("exOffsCDx").set_range(-999999.999,999999.999)
	        self.builder.get_object("exOffsCDy").set_range(-999999.999,999999.999)
	        self.builder.get_object("exOffsCDz").set_range(-999999.999,999999.999)
		gobject.timeout_add(500,self.periodic_check)
#		gobject.timeout_add(1000,self.debug_check)
		self.s = linuxcnc.stat()
		self.c = linuxcnc.command()
		self.holding_btn_ab = False
		self.holding_btn_cd = False
		self.queue = []
		self.currProg = []
		self.ab_state = 0
		self.cd_state = 0
		#self.sawThick = 4.0
		#self.builder.get_object("panelWidthSpin").set_active()
	def program_is_run(self):
		return self.halcomp['prog-is-run']
	
	def cstart(self):
                self.s.poll()
		if self.s.task_mode != linuxcnc.MODE_AUTO:
                    self.c.mode(linuxcnc.MODE_AUTO)
                    self.c.wait_complete()
                self.s.poll()
                if self.s.paused:
                    self.c.auto(linuxcnc.AUTO_STEP)
                    return
                if self.s.interp_state == linuxcnc.INTERP_IDLE:
                        self.c.auto(linuxcnc.AUTO_RUN,0)


	def cycleStart(self,table=0,gcode_path=""):
		
		if table == 0:
			x1 = self.datum_x1 + self.offs_x1
			y1 = self.datum_y1 + self.offs_y1
			z1 = self.datum_z1 + self.offs_z1
			mdi_str = "G10 L2 P1 X" + str(x1) + " Y" + str(y1) + " Z" + str(z1)
			self.c.mode(linuxcnc.MODE_MDI)
			self.c.wait_complete()
#			self.c.mdi("M699") #reset
#			self.c.wait_complete()
			self.c.mdi(mdi_str)
			self.c.mdi("G91G28Z0.")
			self.c.mdi("M335")
			self.c.wait_complete()
		if table == 1:
			x2 = self.datum_x2 + self.offs_x2
			y2 = self.datum_y2 + self.offs_y2
			z2 = self.datum_z2 + self.offs_z2
			mdi_str = "G10 L2 P1 X" + str(x2) + " Y" + str(y2) + " Z" + str(z2)
			self.c.mode(linuxcnc.MODE_MDI)
			self.c.wait_complete()
#			self.c.mdi("M699") #reset
#			self.c.wait_complete()
			self.c.mdi(mdi_str)
			self.c.mdi("G91G28Z0.")
			self.c.mdi("M335")
			self.c.wait_complete()

		self.builder.get_object("vcp_action_open1").load_file(gcode_path)
		self.cstart()

		#self.c.mode(linuxcnc.MODE_AUTO)
		#self.c.wait_complete()
		#self.c.reset_interpreter()
		#self.c.auto(linuxcnc.AUTO_RUN,0)
		#self.lastRun = False			
	def debug_check(self):
		print ("Daftar antri")
		print(self.queue)
		print ("status ab")
		print(self.ab_state)
		print ("status cd")
		print(self.cd_state)
		return True
	def is_exist(self,data=[],val=0):
	        exist = False
        	for x in data:
                	if(x[0] == val):
                        	print ("data sudah ada")
                        	exist = True
        	return exist

	def periodic_check(self):
		#check abort signal
		self.s.poll()

		if  self.halcomp['abort_signal'] == True and self.halcomp['machine-on'] == True:
			self.ab_state = 0
			self.cd_state = 0
			del self.queue[:]
			self.halcomp['hal_led_run_ab'] = False
			self.halcomp['hal_led_run_cd'] = False
			self.c.mode(linuxcnc.MODE_MDI)
                        self.c.wait_complete()
                        self.c.set_digital_output(60,0)
                        self.c.wait_complete()
			print("pembatalan berhasil")

		self.s.poll()
                if self.s.paused == True:
			if self.ab_state == 2:
				if self.halcomp['hal_start_a'] == True or self.halcomp['hal_start_b'] == True:
					self.c.auto(linuxcnc.AUTO_RESUME)
					print("ditekan resume")
			if self.cd_state == 2:
				if self.halcomp['hal_start_c'] == True or self.halcomp['hal_start_d'] == True:
					self.c.auto(linuxcnc.AUTO_RESUME)
					print("ditekan resume")
		
		if self.halcomp['prog-is-idle'] == True and self.program_is_run()==False and self.ab_state == 2:
			self.halcomp['hal_led_run_ab'] = False
			print("program AB berakhir")
			self.ab_state = 0
			self.queue.remove(self.currProg)

		if self.halcomp['prog-is-idle'] == True and self.program_is_run()==False and self.cd_state == 2:
			self.halcomp['hal_led_run_cd'] = False
			print("program CD berakhir")
			self.cd_state = 0
			self.queue.remove(self.currProg)

		#CHECK START BTN 
		if self.halcomp['hal_tbl_ab_active'] is True:
			if self.halcomp['hal_led_vp_ab'] is True and self.ab_state == 0:
				if self.halcomp['hal_start_a'] == True or self.halcomp['hal_start_b'] == True:
					data = [0,self.builder.get_object("filechooserbutton1").get_filename()]
					if self.is_exist(self.queue,0):
						print("Program sudah jalan")
					else:	
						print("Jalankan Program AB")
						self.queue.append(data)
						self.halcomp['hal_led_run_ab'] = True
						self.ab_state = 1
						print(self.queue)


		if self.halcomp['hal_tbl_cd_active'] is True:
			if self.halcomp['hal_led_vp_cd'] is True and self.cd_state == 0:
				if self.halcomp['hal_start_c'] == True or self.halcomp['hal_start_d'] == True:
					data = [1,self.builder.get_object("filechooserbutton2").get_filename()]
					if self.is_exist(self.queue,1):
						print("Program sudah jalan")
					else:	
						print("Jalankan Program CD")
						self.queue.append(data)
						self.halcomp['hal_led_run_cd'] = True
						self.cd_state = 1
						print(self.cd_state)
						print(self.queue)

		#print (self.currProg)
		if len(self.queue) > 0 and self.halcomp['prog-is-idle'] == True and self.ab_state == 1 and self.halcomp['abort_signal'] == False:
			Prog = self.queue[-1]
			self.cycleStart(Prog[0],Prog[1])
			self.currProg = Prog
			self.ab_state = 2
			#self.queue.remove(Prog)
			print("Program AB di eksekusi")

		
		if len(self.queue) > 0 and self.halcomp['prog-is-idle'] == True and self.cd_state == 1  and self.halcomp['abort_signal'] == False:
			Prog = self.queue[-1]
			self.cycleStart(Prog[0],Prog[1])
			self.currProg = Prog
			self.cd_state = 2
			#self.queue.remove(Prog)
			print("Program CD di eksekusi")

		#LOCK TABLE WHEN RUN
		if self.program_is_run():
			if self.currProg == 0:
				self.halcomp['hal_tbl_ab_lock'] = True
				self.builder.get_object("togglebutton1").set_sensitive(False)
			else: 
				self.halcomp['hal_tbl_ab_lock'] = False
				self.builder.get_object("togglebutton1").set_sensitive(True)
			if self.currProg == 1:
				self.halcomp['hal_tbl_cd_lock'] = True
				self.builder.get_object("togglebutton2").set_sensitive(False)
			else:
				self.halcomp['hal_tbl_cd_lock'] = False
				self.builder.get_object("togglebutton2").set_sensitive(True)				
		else:
			self.halcomp['hal_tbl_ab_lock'] = False
			self.halcomp['hal_tbl_cd_lock'] = False
			self.builder.get_object("togglebutton1").set_sensitive(True)
			self.builder.get_object("togglebutton2").set_sensitive(True)
		
		return True
				
	def loadMultiProg(self):	
		data = {
			"table_1_info": {
				"active":self.ab_active_st,
				"filename":self.ab_filename,
				"qty":self.ab_qty,
				"offset":{
					"x":self.builder.get_object("exOffsABx").get_value(),
					"y":self.builder.get_object("exOffsABy").get_value(),
					"z":self.builder.get_object("exOffsABz").get_value()
				}
			},
			"table_2_info": {
				"active":self.cd_active_st,
				"filename":self.cd_filename,
				"qty":self.cd_qty,
				"offset":{
					"x":self.builder.get_object("exOffsCDx").get_value(),
					"y":self.builder.get_object("exOffsCDy").get_value(),
					"z":self.builder.get_object("exOffsCDz").get_value()
				}
			}
		}
		self.jsonWriter(data)

		self.offs_x1 = self.builder.get_object("exOffsABx").get_value()
		self.offs_y1 = self.builder.get_object("exOffsABy").get_value()
		self.offs_z1 = self.builder.get_object("exOffsABz").get_value()

		self.offs_x2 = self.builder.get_object("exOffsCDx").get_value()
		self.offs_y2 = self.builder.get_object("exOffsCDy").get_value()
		self.offs_z2 = self.builder.get_object("exOffsCDz").get_value()


	def jsonWriter(self,data, filename = Filename):
		with open(filename, "w") as f_writer:
			json.dump(data, f_writer)
	
	def filechooser1_file_loaded(self,gtkobj,data=None):
		print("file 1 loaded")
		self.builder.get_object("togglebutton1").set_sensitive(True)

	def filechooser2_file_loaded(self,gtkobj,data=None):
		print("file 2 loaded")
		self.builder.get_object("togglebutton2").set_sensitive(True)

	def btn_active_ab_state(self,gtkobj,data=None):
		self.builder.get_object("button1").set_sensitive(self.ab_active_st)
		self.builder.get_object("exOffsABx").set_sensitive(self.ab_active_st)
		self.builder.get_object("exOffsABy").set_sensitive(self.ab_active_st)
		self.builder.get_object("exOffsABz").set_sensitive(self.ab_active_st)
		gcode_path = self.builder.get_object("filechooserbutton1").set_sensitive(self.ab_active_st)
		self.ab_active_st = not self.ab_active_st
		#c.set_digital_output(29, self.ab_active_st)
		self.halcomp['hal_tbl_ab_active'] = self.ab_active_st
		if(self.ab_active_st is True):
			gcode_path = self.builder.get_object("filechooserbutton1").get_filename()
			self.ab_filename = gcode_path
			self.loadMultiProg()
		else:
			self.ab_state = 0			
	def btn_active_cd_state(self,gtkobj,data=None):
		self.builder.get_object("button2").set_sensitive(self.cd_active_st)
		self.builder.get_object("exOffsCDx").set_sensitive(self.cd_active_st)
		self.builder.get_object("exOffsCDy").set_sensitive(self.cd_active_st)
		self.builder.get_object("exOffsCDz").set_sensitive(self.cd_active_st)
		gcode_path = self.builder.get_object("filechooserbutton2").set_sensitive(self.cd_active_st)
                self.cd_active_st = not self.cd_active_st
		#c.set_digital_output(30, self.cd_active_st)
		self.halcomp['hal_tbl_cd_active'] = self.cd_active_st
		if(self.cd_active_st is True):
			gcode_path = self.builder.get_object("filechooserbutton2").get_filename()
			self.cd_filename = gcode_path
			self.loadMultiProg()
		else:
			self.cd_state = 0			

	def hapus1OnClick(self,gtkobj,data=None):		
		self.builder.get_object("togglebutton1").set_sensitive(False)
		self.builder.get_object("filechooserbutton1").set_filename("None")
		self.ab_active_st = False
        	self.ab_filename = None
        	self.ab_qty = 0
		self.loadMultiProg()


	def hapus2OnClick(self,gtkobj,data=None):
		self.builder.get_object("togglebutton2").set_sensitive(False)
		self.builder.get_object("filechooserbutton2").set_filename("None")
	        self.cd_active_st = False
	        self.cd_filename = None
        	self.cd_qty = 0
		self.loadMultiProg()
	
	
