import sys
sys.path.append('../bmv2/tools')
sys.path.append('../bmv2/targets/simple_switch')
import runtime_CLI
import sswitch_CLI
from sswitch_runtime import SimpleSwitch
import time

import numpy as np
import hashlib
import struct
import binascii
import pickle
import os
from random import SystemRandom

CONFIG_FILE = "config.txt"
OLD_COUNTERS = "old_counters.txt"
OLD_KEYS = "old_keys_file.txt"

################################# common utils ################################

def connect_to_switch(switch_port):
	standard_client, mc_client = runtime_CLI.thrift_connect("127.0.0.1", int(switch_port), runtime_CLI.RuntimeAPI.get_thrift_services(1))
	return standard_client, mc_client

def read_config(filename):
	config_file = open(filename, "r")
	width = int(config_file.readline().strip("\n").split(" ")[1])
	height = int(config_file.readline().strip("\n").split(" ")[1])
	config_file.close()
	return width, height

###############################################################################
################################### key utils #################################

def generate_key():
	"""
	Get a random number from urandom between 0 and (2^128)-1
	"""
	r = SystemRandom()
	limit = pow(2, 128) - 1
	return r.randrange(limit)

def set_new_key(standard_client, mc_client):
	"""
	Set a new key
	"""
	key = generate_key()

	format_pattern = "{0:0%db}" % 128
	formated_key = (format_pattern.format(key))
	fragments_32bits = [formated_key[i:i+32] for i in range(0, len(formated_key), 32)]
	
	runtime_CLI.RuntimeAPI(1, standard_client, mc_client).client.bm_register_write(0, "key_register", 0, int(fragments_32bits[0], 2))
	runtime_CLI.RuntimeAPI(1, standard_client, mc_client).client.bm_register_write(0, "key_register", 1, int(fragments_32bits[1], 2))
	runtime_CLI.RuntimeAPI(1, standard_client, mc_client).client.bm_register_write(0, "key_register", 2, int(fragments_32bits[2], 2))
	runtime_CLI.RuntimeAPI(1, standard_client, mc_client).client.bm_register_write(0, "key_register", 3, int(fragments_32bits[3], 2))

def reset_sketch(standard_client, mc_client):
	"""
	Reset all counters of the sketch
	"""
	runtime_CLI.RuntimeAPI(1, standard_client, mc_client).client.bm_counter_reset_all(0, "counters")

def get_key(switch_port):
	"""
	Get the key being used by the algorithm 
	"""
	standard_client, mc_client = connect_to_switch(switch_port)

	value_fragment = runtime_CLI.RuntimeAPI(1, standard_client, mc_client).client.bm_register_read(0, "key_register", 0)
	value = (value_fragment << 96)

	value_fragment = runtime_CLI.RuntimeAPI(1, standard_client, mc_client).client.bm_register_read(0, "key_register", 1)
	value = value | (value_fragment << 64)

	value_fragment = runtime_CLI.RuntimeAPI(1, standard_client, mc_client).client.bm_register_read(0, "key_register", 2)
	value = value | (value_fragment << 32)

	value_fragment = runtime_CLI.RuntimeAPI(1, standard_client, mc_client).client.bm_register_read(0, "key_register", 3)
	value = value | value_fragment
		
	return value

def init_key(switch_port):
	"""
	Set the key to be used by the algorithm
	"""
	standard_client, mc_client = connect_to_switch(switch_port)
	set_new_key(standard_client, mc_client)

def change_key(switch_port):
	"""
	Change the key being used by the algorithm and reset all counters
	"""
	standard_client, mc_client = connect_to_switch(switch_port)
	set_new_key(standard_client, mc_client)
	reset_sketch(standard_client, mc_client)

def save_n_reset(switch_port):
	"""
	Save the current data structure,
	Reset it and
	Change the key to be used 
	"""
	sketch = get_parsed_counters_packets(switch_port)
	dump_sketch_to_file(sketch)
	
	key = get_key(switch_port)
	#format_pattern = "{0:0%db}" % 128
	#password = "%s" % (format_pattern.format(int(key)))
	write_key_to_file(key)

	change_key(switch_port)

def dump_sketch_to_file(sketch):
	old_counters_file = open(OLD_COUNTERS, "ab")
	pickle.dump(sketch, old_counters_file)
	old_counters_file.close()

def write_key_to_file(key):
	old_keys_file = open(OLD_KEYS, "a")
	old_keys_file.write('{}'.format(key))
	old_keys_file.write("\n")
	old_keys_file.close()

def hard_reset(switch_port):
	try:
		os.remove(OLD_COUNTERS)
		os.remove(OLD_KEYS)
	except OSError:
		pass
	standard_client, mc_client = connect_to_switch(switch_port)
	reset_sketch(standard_client, mc_client)
	change_key(switch_port)

def get_N(switch_port):
	sketch = get_parsed_counters_packets(switch_port)
	count_n = 0
	for i in range(len(sketch[0])):
		count_n += int(sketch[0][i])
	return count_n

###############################################################################
################################ counters utils ###############################

def parse_counters_bytes(sketch):
	"""
	Parse all counters to get the number of bytes
	"""
	parsed_sketch = []
	for i in range(len(sketch)):
		parsed_sketch.append([])
		for j in range(len(sketch[i])):
			parsed_sketch[i].append(str(sketch[i][j]).split("=")[2].split(")")[0])
	return parsed_sketch

def parse_counters_packets(sketch):
	"""
	Parse all counters to get the number of packets
	"""
	parsed_sketch = []
	for i in range(len(sketch)):
		parsed_sketch.append([])
		for j in range(len(sketch[i])):
			parsed_sketch[i].append(str(sketch[i][j]).split("=")[1].split(",")[0])
	return parsed_sketch

def parse_counter_bytes(item):
	"""
	Parse a counter to get the number of bytes
	"""
	return str(item).split("=")[2].split(")")[0]

def parse_counter_packets(item):
	"""
	Parse a counter to get the number of packets
	"""
	return str(item).split("=")[1].split(",")[0]

def get_counter(switch_port, row, column):
	"""
	Get a specific counter given row and column
	"""
	index = row + column
	standard_client, mc_client = connect_to_switch(switch_port)
	return runtime_CLI.RuntimeAPI(1, standard_client, mc_client).client.bm_counter_read(0, "counters", index)

def get_counters(switch_port):
	"""
	Get all counters
	"""
	width, height = read_config(CONFIG_FILE)
	standard_client, mc_client = connect_to_switch(switch_port)
	sketch = []
	index = 0;
	for i in range(0, height):
		sketch.append([])
		for j in range(0, width):
			value = runtime_CLI.RuntimeAPI(1, standard_client, mc_client).client.bm_counter_read(0, "counters", index)
			sketch[i].append(value)
			index = index + 1
	return sketch

def get_parsed_counter_packets(switch_port, row, column):
	"""
	Get a representation of a specific packets counter given row and column 
	"""
	return parse_counter_packets(get_counter(switch_port, row, column))

def get_parsed_counter_bytes(switch_port, row, column):
	"""
	Get a representation of a specific bytes counter given row and column 
	"""
	return parse_counter_bytes(get_counter(switch_port, row, column))

def get_parsed_counters_packets(switch_port):
	"""
	Get a representation of all counters parsed for packets
	"""
	return parse_counters_packets(get_counters(switch_port))

def get_parsed_counters_bytes(switch_port):
	"""
	Get a representation of all counters parsed for bytes
	"""
	return parse_counters_bytes(get_counters(switch_port))

def print_counters_packets(switch_port):
	"""
	Print a representation of all counters parsed for packets
	"""
	sketch = get_parsed_counters_packets(switch_port)
	print(np.matrix(sketch))

def print_counters_bytes(switch_port):
	"""
	Print a representation of all counters parsed for bytes
	"""
	sketch = get_parsed_counters_bytes(switch_port)
	print(np.matrix(sketch))

###############################################################################
################################ estimate utils ###############################

def estimate_all(switch_port, item, flag):
	"""
	Estimate the number of packets sent by item since the switch started 
	"""
	estimated = 0
	try:
		old_counters_file = open(OLD_COUNTERS, "rb")
		old_keys_file = open(OLD_KEYS, "r")
		while True: 
			try:
				sketch = pickle.load(old_counters_file)
			except EOFError:
				break

			key = old_keys_file.readline().strip("\n")
			estimated += estimate(switch_port, item, sketch, key, flag)
		old_counters_file.close()
		old_keys_file.close()
	except IOError:
		pass

	estimated += estimate_recent(switch_port, item, flag)
	return estimated

def estimate_recent(switch_port, item, flag):
	"""
	Estimate the number of packets sent by item since the last key change
	"""
	key = get_key(switch_port)
	estimated = estimate(switch_port, item, None, key, flag)
	return estimated 

def estimate(switch_port, item, sketch, key, flag):
	"""
	Estimate the number of packets sent by item
	"""
	config_file = open(CONFIG_FILE, "r")	
	width = int(config_file.readline().strip("\n").split(" ")[1])
	height = int(config_file.readline().strip("\n").split(" ")[1])
	slot_size = int(config_file.readline().strip("\n").split(" ")[1])
	config_file.close()

	estimated = float('inf')

	format_pattern = "{0:0%db}" % 128
	password = "%s" % (format_pattern.format(int(key)))

	octets = [password[i:i+8] for i in range(0, len(password), 8)]
	password = "%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s" % (chr(int(octets[0], 2)), chr(int(octets[1], 2)), chr(int(octets[2], 2)), 
		chr(int(octets[3], 2)),	chr(int(octets[4], 2)), chr(int(octets[5], 2)), chr(int(octets[6], 2)), chr(int(octets[7], 2)), 
		chr(int(octets[8], 2)), chr(int(octets[9], 2)), chr(int(octets[10], 2)), chr(int(octets[11], 2)), chr(int(octets[12], 2)), 
		chr(int(octets[13], 2)), chr(int(octets[14], 2)), chr(int(octets[15], 2)))

	row = 0
	last_row = width * (height - 1)
	while (row <= last_row):
		h = hashlib.new('md5')
		
		items_list = []
		
		if flag == "src_ip":
			raw_ip = item.split(".")
			items_list.append("%s%s%s%s" % (chr(int(raw_ip[0])), chr(int(raw_ip[1])), chr(int(raw_ip[2])), chr(int(raw_ip[3]))))
		elif flag == "flow":
			item.replace(" ", "")
			
			src_dst = item.split("-")
			src = src_dst[0].split(":")
			dst = src_dst[1].split(":")
			
			raw_ip_src = src[0].split(".")
			raw_ip_dst = dst[0].split(".")
			
			raw_ip = []
			for i in range(0, 4):
				if len(raw_ip_src) == len(raw_ip_dst): 
					raw_ip.append([])
					raw_ip[i] = int(raw_ip_src[i]) ^ int(raw_ip_dst[i])
				
			items_list.append("%s%s%s%s" % (chr(raw_ip[0]), chr(raw_ip[1]), chr(raw_ip[2]), chr(raw_ip[3])))
			
			
			format_pattern = "{0:0%db}" % 16
			raw_port_src = int(src[1])
			raw_port_dst = int(dst[1])
			raw_port = raw_port_src ^ raw_port_dst
			
			port = "%s" % (format_pattern.format(raw_port))
			octets = [port[i:i+8] for i in range(0, len(port), 8)]
			
			items_list.append("%s%s" % (chr(int(octets[0], 2)), chr(int(octets[1], 2))))
			
			       

		format_pattern = "{0:0%db}" % slot_size
		row_to_find = "%s" % (format_pattern.format(row))
		octets = [row_to_find[i:i+8] for i in range(0, len(row_to_find), 8)]
		row_to_find = "%s%s%s%s" % (chr(int(octets[0], 2)), chr(int(octets[1], 2)), chr(int(octets[2], 2)), chr(int(octets[3], 2)))
		
		
		for i in items_list:
		    h.update(i)
		h.update(row_to_find)
		h.update(password)
		
		hashed_binary = h.digest()
		buf_long = struct.unpack('2Q', hashed_binary)

		full_hash = (buf_long[0] << 64) | buf_long[1]
		column = full_hash % width

		if(sketch is None):
			estimated = min(estimated, int(get_parsed_counter_packets(switch_port, row, column)))
		else:
			estimated = min(estimated, int(sketch[row//width][column]))
		
		row += width
		
	return estimated

def print_estimate(value):
	"""
	Print the estimated value given
	"""
	print "estimated: %d" % value

def wrong_args_msg():
	print "Usage: display_sketch switch_port [-r | -R | -e item | -E item] [--flow]"
	print "\t -R: change key"
	print "\t -r: change key and save data"
	print "\t -n: get the sum of the values of all the counters in a row"
	print "\t -E item: estimate the total number of packets sent by item"
	print "\t -e item: estimate the number of packets recently sent by item"
	print "\t --flow: estimate the packets exchanged within a flow with the format: <src_ip>:<src_port>-<dst_ip>:<dst_port>"
	print "\t item: IP address by default. It defines what is going to be estimated"
 
if __name__ == '__main__':
	n_args = len(sys.argv)
	if n_args == 2:
		print_counters_packets(sys.argv[1])
	elif n_args == 3 and sys.argv[2] == "-R":
		hard_reset(sys.argv[1])
	elif n_args == 3 and sys.argv[2] == "-r":
		save_n_reset(sys.argv[1])
	elif n_args == 3 and sys.argv[2] == "-n":
		n = get_N(sys.argv[1])
		print "N = %d" % n
	elif n_args == 4 and sys.argv[2] == "-E":
		print_estimate(estimate_all(sys.argv[1], sys.argv[3], "src_ip"))
	elif n_args == 4 and sys.argv[2] == "-e":
		print_estimate(estimate_recent(sys.argv[1], sys.argv[3], "src_ip"))
	elif n_args == 5 and sys.argv[2] == "-E" and sys.argv[4] == "--flow":
		print_estimate(estimate_all(sys.argv[1], sys.argv[3], "flow"))
	elif n_args == 5 and sys.argv[2] == "-e" and sys.argv[4] == "--flow":
		print_estimate(estimate_recent(sys.argv[1], sys.argv[3], "flow"))
	else :
		wrong_args_msg()
