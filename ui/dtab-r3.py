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
	datum_x1 = 247.971 #247.331
	datum_y1 = -115.14 #-112.662
	datum_z1 = -322.8000
	#DATUM T2
	datum_x2 = 2589.251 #2593.511 2580.05
	datum_y2 = -115.14
	datum_z2 = -322.8000
	#DATUM o1
	offs_x1 = 0.0
	offs_y1 = 0.0
	offs_z1 = 0.0
	#DATUM o2
	offs_x2 = 0.0
	offs_y2 = 0.0
	offs_z2 = 0.0

	TAB_AB = 0
	TAB_CD = 1

	cstart_ab = False
	cstart_cd = False

	exec_ab = False
	exec_cd = False

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
		self.tick_ab = 0
		self.tick_cd = 0
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
			self.offs_x1 = self.builder.get_object("exOffsABx").get_value()
			self.offs_y1 = self.builder.get_object("exOffsABy").get_value()
			self.offs_z1 = self.builder.get_object("exOffsABz").get_value()
			print ("=================Offsets Table AB==============")
			print ("OffsX = " + str(self.offs_x1))
			print ("OffsY = " + str(self.offs_y1))
			print ("OffsZ = " + str(self.offs_z1))
			print ("===============================================")
			x1 = self.datum_x1 + self.offs_x1
			y1 = self.datum_y1 + self.offs_y1
			z1 = self.datum_z1 + self.offs_z1
			mdi_str = "G10 L2 P1 X" + str(x1) + " Y" + str(y1) + " Z" + str(z1)
			self.c.mode(linuxcnc.MODE_MDI)
			self.c.wait_complete()
#			self.c.mdi("M699") #reset
#			self.c.wait_complete()
			self.c.mdi(mdi_str)
			self.c.mdi("G40G49G64")
			self.c.mdi("G91G28Z0.")
			self.c.mdi("M335")
			self.c.mdi("G54")
			self.c.wait_complete()
		if table == 1:
			self.offs_x2 = self.builder.get_object("exOffsCDx").get_value()
			self.offs_y2 = self.builder.get_object("exOffsCDy").get_value()
			self.offs_z2 = self.builder.get_object("exOffsCDz").get_value()
			print ("=================Offsets Table CD==============")
			print ("OffsX = " + str(self.offs_x2))
			print ("OffsY = " + str(self.offs_y2))
			print ("OffsZ = " + str(self.offs_z2))
			print ("===============================================")
			x2 = self.datum_x2 + self.offs_x2
			y2 = self.datum_y2 + self.offs_y2
			z2 = self.datum_z2 + self.offs_z2
			mdi_str = "G10 L2 P1 X" + str(x2) + " Y" + str(y2) + " Z" + str(z2)
			self.c.mode(linuxcnc.MODE_MDI)
			self.c.wait_complete()
#			self.c.mdi("M699") #reset
#			self.c.wait_complete()
			self.c.mdi(mdi_str)
			self.c.mdi("G40G49G64")
			self.c.mdi("G91G28Z0.")
			self.c.mdi("M335")
			self.c.mdi("G54")
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
	def buttonABon(self):
		return self.halcomp['hal_start_a'] or self.halcomp['hal_start_b']
	def buttonCDon(self):
		return self.halcomp['hal_start_c'] or self.halcomp['hal_start_d']
	def tabABready(self):
		return self.halcomp['hal_tbl_ab_active'] and self.halcomp['hal_led_vp_ab']
	def tabCDready(self):
		return self.halcomp['hal_tbl_cd_active'] and self.halcomp['hal_led_vp_cd']
	def periodic_check(self):

		self.s.poll()
		#check abort signal
		if  self.halcomp['abort_signal'] and self.halcomp['machine-on']:
			self.exec_ab = False
			self.cstart_ab = False
			self.exec_cd = False
			self.cstart_cd = False
			self.c.mode(linuxcnc.MODE_MDI)
                        self.c.wait_complete()
                        self.c.set_digital_output(60,0)
                        self.c.wait_complete()
			print("pembatalan berhasil")

		#UNLOCK VACUUM WHEN STOPED/PAUSED
		if self.s.interp_state == linuxcnc.INTERP_IDLE: 
			if not self.exec_ab:
				self.halcomp['hal_tbl_ab_lock'] = False
			if not self.exec_cd:
				self.halcomp['hal_tbl_cd_lock'] = False
		elif self.s.interp_state == linuxcnc.INTERP_PAUSED:
			if self.exec_ab:
				self.halcomp['hal_tbl_ab_lock'] = False
			else:
				self.halcomp['hal_tbl_ab_lock'] = False
			if self.exec_cd:
				self.halcomp['hal_tbl_cd_lock'] = False
			else:
				self.halcomp['hal_tbl_cd_lock'] = False
		else:
			if self.exec_ab:
				self.halcomp['hal_tbl_ab_lock'] = True
			else:
				self.halcomp['hal_tbl_ab_lock'] = False
			if self.exec_cd:
				self.halcomp['hal_tbl_cd_lock'] = True
			else:
				self.halcomp['hal_tbl_cd_lock'] = False
		
		#active/deactive activate button
		if self.exec_ab:
			self.builder.get_object("togglebutton1").set_sensitive(False)
			self.halcomp['hal_led_run_ab'] = True
		else:
			self.builder.get_object("togglebutton1").set_sensitive(True)
			self.halcomp['hal_led_run_ab'] = False
		if self.exec_cd:
			self.builder.get_object("togglebutton2").set_sensitive(False)
			self.halcomp['hal_led_run_cd'] = True
		else:
			self.builder.get_object("togglebutton2").set_sensitive(True)
			self.halcomp['hal_led_run_cd'] = False
		
		#INTERPRETER STATE SCANNING  
		if self.s.interp_state == linuxcnc.INTERP_IDLE: 
			if self.exec_ab:
				self.cstart_ab = False
				self.exec_ab = False
				self.halcomp['hal_led_rdy_ab'] = False
				print("dtab.py:Program AB Selesai")
				#check other table queue
				if self.cstart_cd:
					self.exec_cd=True
					self.cstart_cd=True
					self.cycleStart(self.TAB_CD,self.cd_filename)
					self.tick_cd = time.time()
					self.halcomp['hal_led_rdy_cd'] = True
					print("dtab.py:Program Antri CD Dieksekusi")
			elif self.exec_cd:
				self.cstart_cd = False
				self.exec_cd = False
				self.halcomp['hal_led_rdy_cd'] = False
				print("dtab.py:Program CD Selesai")
				#check other table queue
				if self.cstart_ab:
					self.exec_ab=True
					self.cstart_ab=True
					self.cycleStart(self.TAB_AB,self.ab_filename)
					self.tick_ab = time.time()
					self.halcomp['hal_led_rdy_ab'] = True
					print("dtab.py:Program Antri AB Dieksekusi")
			if not self.exec_ab and not self.exec_cd:
				if self.buttonABon() and self.tabABready():
					self.exec_ab=True
					self.cstart_ab=True
					self.cycleStart(self.TAB_AB,self.ab_filename)				
					self.tick_ab = time.time()
					self.halcomp['hal_led_rdy_ab'] = True
					print("dtab.py:Program AB Dieksekusi")
				elif self.buttonCDon() and self.tabCDready():
					self.exec_cd=True
					self.cstart_cd=True
					self.cycleStart(self.TAB_CD,self.cd_filename)
					self.tick_cd = time.time()
					self.halcomp['hal_led_rdy_cd'] = True
					print("dtab.py:Program CD Dieksekusi")
		elif self.s.interp_state == linuxcnc.INTERP_PAUSED:
			if self.exec_ab:
				if self.buttonABon() and self.tabABready():
					self.c.auto(linuxcnc.AUTO_RESUME)
					print("dtab.py:Program AB Dilanjutkan")
				if self.buttonCDon() and self.tabCDready():
					print("dtab.py:Program CD Selanjutnya")
					self.halcomp['hal_led_rdy_cd'] = True
					self.cstart_cd=True

			if self.exec_cd:					
				if self.buttonCDon() and self.tabCDready():
					self.c.auto(linuxcnc.AUTO_RESUME)
					print("dtab.py:Program CD Dilanjutkan")
				if self.buttonABon() and self.tabABready():
					self.cstart_ab=True
					self.halcomp['hal_led_rdy_ab'] = True
					print("dtab.py:Program AB Selanjutnya")
		else:
			if self.exec_cd:
				if self.buttonABon() and self.tabABready():
					self.cstart_ab=True
					self.halcomp['hal_led_rdy_ab'] = True
					print("dtab.py:Program AB Selanjutnya")
			if self.exec_ab:
				if self.buttonCDon() and self.tabCDready():
					self.cstart_cd=True
					self.halcomp['hal_led_rdy_cd'] = True
					print("dtab.py:Program CD Selanjutnya")
		
		#TICK T1
		if self.exec_ab:
			currSecAb = time.time() - self.tick_ab
			timeFmtAb = time.strftime('%H:%M:%S',time.gmtime(currSecAb))
			self.builder.get_object("clock1").set_text(timeFmtAb)
		#TICK T2
		if self.exec_cd: 	
			currSecCd = time.time() - self.tick_cd
			timeFmtCd = time.strftime('%H:%M:%S',time.gmtime(currSecCd))
			self.builder.get_object("clock2").set_text(timeFmtCd)

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
		#self.builder.get_object("exOffsABx").set_sensitive(self.ab_active_st)
		#self.builder.get_object("exOffsABy").set_sensitive(self.ab_active_st)
		#self.builder.get_object("exOffsABz").set_sensitive(self.ab_active_st)
		gcode_path = self.builder.get_object("filechooserbutton1").set_sensitive(self.ab_active_st)
		self.ab_active_st = not self.ab_active_st
		#c.set_digital_output(29, self.ab_active_st)
		self.halcomp['hal_tbl_ab_active'] = self.ab_active_st
		if(self.ab_active_st is True):
			gcode_path = self.builder.get_object("filechooserbutton1").get_filename()
			self.ab_filename = gcode_path
			#self.loadMultiProg()
		else:
			self.ab_state = 0			
	def btn_active_cd_state(self,gtkobj,data=None):
		self.builder.get_object("button2").set_sensitive(self.cd_active_st)
		#self.builder.get_object("exOffsCDx").set_sensitive(self.cd_active_st)
		#self.builder.get_object("exOffsCDy").set_sensitive(self.cd_active_st)
		#self.builder.get_object("exOffsCDz").set_sensitive(self.cd_active_st)
		gcode_path = self.builder.get_object("filechooserbutton2").set_sensitive(self.cd_active_st)
                self.cd_active_st = not self.cd_active_st
		#c.set_digital_output(30, self.cd_active_st)
		self.halcomp['hal_tbl_cd_active'] = self.cd_active_st
		if(self.cd_active_st is True):
			gcode_path = self.builder.get_object("filechooserbutton2").get_filename()
			self.cd_filename = gcode_path
			#self.loadMultiProg()
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
	
	
