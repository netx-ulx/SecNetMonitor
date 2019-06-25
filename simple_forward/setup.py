import os
import sys
import subprocess
import time
import signal
import psutil

#from display_sketch import init_key

CONFIG_FILE = "config.txt"
INPUT_FILE = "./p4src/includes/input.p4"
PID_FILE = "pid.txt"

def read_config():
	config_file = open(CONFIG_FILE, "r")
	width = int(config_file.readline().strip("\n").split(" ")[1])
	height = int(config_file.readline().strip("\n").split(" ")[1])
	slot_size = int(config_file.readline().strip("\n").split(" ")[1])
	return width, height, slot_size

def write_input_file():
	width, height, slot_size = read_config()
	input_file = open(INPUT_FILE, "w")
	input_file.write("#define SKETCH_WIDTH %d\n" % width)
	input_file.write("#define SKETCH_HEIGTH %d\n" % height)
	input_file.write("#define SLOT_SIZE %d\n" % slot_size)
	input_file.write("#define LAST_ITERATION %d\n" % ((height - 1) * width))
	input_file.write("#define NUMBER_OF_INSTANCES %d\n" % (height * width))
	 
def setup():
	write_input_file()

	# read topology and start mininet
	os.system('../p4c-bmv2/p4c_bm/__main__.py p4src/forward.p4 --json forward.json')
	os.system('sudo ../bmv2/targets/simple_switch/simple_switch >/dev/null 2>&1')
	
	cmd = "sudo python topo.py \
		--behavioral-exe ../bmv2/targets/simple_switch/simple_switch \
		--json forward.json \
		--cli ../bmv2/tools/runtime_CLI.py"

	mininet = subprocess.Popen(cmd, shell=True) #non-blocking
	time.sleep(1)
	#init_key(22222) #It is now possible to have different keys for different switches
	mininet.wait()

def wrong_args_msg():
	print "Usage: setup.py"

if __name__ == '__main__':
	argc = len(sys.argv)
	if argc == 1:
		setup()
	else:
		wrong_args_msg()