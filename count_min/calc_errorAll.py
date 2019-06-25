import sys
from display_sketch import estimate_recent

def main(ips, freqs):
	ips_file = open(ips, "r")
	frequencies_file = open(freqs, "r")
	
	errors = []

	while True:
		ip = ips_file.readline().strip("\n")
		if ip == '':
			break
		freq = int(frequencies_file.readline().strip("\n"))
		estimated = estimate_recent(22222, ip, "src_ip")
		error = estimated - freq
		if(error < 0):
			continue
			
		errors.append(error) 
	
	errors.sort()
	for e in errors:
		print e
	

if __name__ == '__main__':
	n_args = len(sys.argv)
	if n_args == 3:
		main(sys.argv[1], sys.argv[2])
	else:
		print "Usage: calc_errorAll <distinct_items.txt> <frequencies.txt>"
