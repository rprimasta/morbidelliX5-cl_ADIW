#!/usr/bin/python
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.register_read_message import ReadInputRegistersResponse
from pprint import pprint
import time
import linuxcnc, hal
import json



paramx5 = hal.component("paramx5")
#TOOLCHANGE
paramx5.newpin("tc_poc_y", hal.HAL_FLOAT,hal.HAL_IN)
paramx5.newpin("tc_poc_z", hal.HAL_FLOAT,hal.HAL_IN)
paramx5.newpin("tc_retract_z", hal.HAL_FLOAT,hal.HAL_IN)
paramx5.newpin("tc_feedrate", hal.HAL_FLOAT,hal.HAL_IN)
paramx5.newpin("tc_unclamp_maxretry", hal.HAL_U32,hal.HAL_IN)
paramx5.newpin("tc_clamp_maxretry", hal.HAL_U32,hal.HAL_IN)
paramx5.newpin("tc_numslot", hal.HAL_U32,hal.HAL_IN)

paramx5.newpin("tc_currtool", hal.HAL_U32,hal.HAL_IN)
paramx5.newpin("tc_magpusher", hal.HAL_U32,hal.HAL_IN)
paramx5.newpin("tc_last_tool_error", hal.HAL_U32,hal.HAL_IN)

paramx5.newpin("tc_mag_poc01", hal.HAL_U32,hal.HAL_IN)
paramx5.newpin("tc_mag_poc02", hal.HAL_U32,hal.HAL_IN)
paramx5.newpin("tc_mag_poc03", hal.HAL_U32,hal.HAL_IN)
paramx5.newpin("tc_mag_poc04", hal.HAL_U32,hal.HAL_IN)
paramx5.newpin("tc_mag_poc05", hal.HAL_U32,hal.HAL_IN)
paramx5.newpin("tc_mag_poc06", hal.HAL_U32,hal.HAL_IN)
paramx5.newpin("tc_mag_poc07", hal.HAL_U32,hal.HAL_IN)
paramx5.newpin("tc_mag_poc08", hal.HAL_U32,hal.HAL_IN)
paramx5.newpin("tc_mag_poc09", hal.HAL_U32,hal.HAL_IN)
paramx5.newpin("tc_mag_poc10", hal.HAL_U32,hal.HAL_IN)
paramx5.newpin("tc_mag_poc11", hal.HAL_U32,hal.HAL_IN)
paramx5.newpin("tc_mag_poc12", hal.HAL_U32,hal.HAL_IN)

#WORKTABLE
paramx5.newpin("tbl_datum_x_ab", hal.HAL_FLOAT,hal.HAL_IN)
paramx5.newpin("tbl_datum_y_ab", hal.HAL_FLOAT,hal.HAL_IN)
paramx5.newpin("tbl_datum_z_ab", hal.HAL_FLOAT,hal.HAL_IN)
paramx5.newpin("tbl_datum_x_cd", hal.HAL_FLOAT,hal.HAL_IN)
paramx5.newpin("tbl_datum_y_cd", hal.HAL_FLOAT,hal.HAL_IN)
paramx5.newpin("tbl_datum_z_cd", hal.HAL_FLOAT,hal.HAL_IN)

#DUSTHOOD
paramx5.newpin("dhood_enable", hal.HAL_BIT,hal.HAL_IN)
paramx5.newpin("dhood_free_pos", hal.HAL_FLOAT,hal.HAL_IN)
paramx5.newpin("dhood_ret_pos", hal.HAL_FLOAT,hal.HAL_IN)


def save_var(filename='hvar.var',vars=dict()):
        if vars:
                outfile = open(filename,'wb')
                pickle.dump(vars,outfile)
                outfile.close()

def load_var(filename='hvar.var'):
        if os.path.isfile(filename):    # True
                infile = open(filename,'rb')
                newd = pickle.load(infile)
                infile.close()
                return newd
        else:
                save_var(filename=filename,vars=dict())
                return dict()
	
def var_init():
	default_vars = dict()
	default_vars['tc_currtool'] = 1
	default_vars['tc_magpusher'] = 0
	default_vars['tc_last_tool_error'] = 0

	vars = load_var()
	if not vars:
		vars=default_vars
		save_var(vars=vars)

	paramx5['tc_currtool'] = vars['tc_currtool']    
	paramx5['tc_magpusher'] = vars['tc_magpusher']    
	paramx5['tc_last_tool_error'] = vars['tc_last_tool_error']    


if __name__=='__main__' :
	try:
		paramx5.ready()
		#var_init()
		while True:
			pass
	except KeyboardInterrupt:
		print("Saving parameter")