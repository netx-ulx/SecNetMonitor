import sys
from display_sketch import estimate_recent

def main(flows_file_name):
	flows_file = open(flows_file_name, "r")
	count_flows = 0
	count_error = 0
	
	while True:
		line = flows_file.readline().strip("\n").split(" ")
		#print line
		if line[0] == '':
			break
			
		flow = line[0]
		freq = int(line[1])
		
		estimated = estimate_recent(22222, flow, "flow")
		#print "estimated: %d frequency %d" % (estimated, freq)
		error = estimated - freq
		if(error < 0):
			continue
		count_flows += 1
		count_error += error
		
	average_error = count_error/float(count_flows)
	print average_error
	

if __name__ == '__main__':
	n_args = len(sys.argv)
	if n_args == 2:
		main(sys.argv[1])
	else:
		print "Usage: calc_flow_error <flows.txt>"
