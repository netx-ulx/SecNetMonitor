#grep -o '[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}' src_statistics.txt > distinct_ips.txt
#grep -Eo '\s+[0-9]+\s+' src_statistics.txt > frequencies_w.txt
#cat frequencies_w.txt | tr -d " \t\r" > frequencies.txt 

import sys
from display_sketch import estimate_recent

def main(ips, freqs):
	ips_file = open(ips, "r")
	frequencies_file = open(freqs, "r")
	count_ips = 0
	count_error = 0	

	while True:
		ip = ips_file.readline().strip("\n")
		if ip == '':
			break
		freq = int(frequencies_file.readline().strip("\n"))
		estimated = estimate_recent(22222, ip, "src_ip")
		#print "estimated: %d frequency %d" % (estimated, freq)
		error = estimated - freq
		if(error < 0):
			continue
		count_ips += 1
		count_error += error
	
	average_error = count_error/float(count_ips)
	print average_error
	

if __name__ == '__main__':
	n_args = len(sys.argv)
	if n_args == 3:
		main(sys.argv[1], sys.argv[2])
	else:
		print "Usage: calc_error <distinct_items.txt> <frequencies.txt>"
