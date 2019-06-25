import sys
from display_sketch import estimate_recent

def main(flows_file_name):
	flows_file = open(flows_file_name, "r")
	
	errors = []
	
	while True:
		line = flows_file.readline().strip("\n").split(" ")
		if line[0] == '':
			break
			
		flow = line[0]
		freq = int(line[1])
		
		estimated = estimate_recent(22222, flow, "flow")
		error = estimated - freq
		if(error < 0):
			continue
		
		errors.append(error) 
	
	errors.sort()
	for e in errors:
		print e

if __name__ == '__main__':
	n_args = len(sys.argv)
	if n_args == 2:
		main(sys.argv[1])
	else:
		print "Usage: calc_flow_error <flows.txt>"
