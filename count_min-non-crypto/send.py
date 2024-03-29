#!/usr/bin/python

# Copyright 2013-present Barefoot Networks, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from scapy.all import Ether, IP, sendp, get_if_hwaddr, get_if_list, TCP, Raw
import sys
import random, string

def randomword(max_length):
    length = random.randint(1, max_length)
    return ''.join(random.choice(string.lowercase) for i in range(length))

def read_topo():
    nb_hosts = 0
    nb_switches = 0
    links = []
    with open("topo.txt", "r") as f:
        line = f.readline()[:-1]
        w, nb_switches = line.split()
        assert(w == "switches")
        line = f.readline()[:-1]
        w, nb_hosts = line.split()
        assert(w == "hosts")
        for line in f:
            if not f: break
            a, b = line.split()
            links.append( (a, b) )
    return int(nb_hosts), int(nb_switches), links

def send_random_traffic(dst):
    dst_mac = None
    dst_ip = None
    src_mac = [get_if_hwaddr(i) for i in get_if_list() if i == 'eth0']
    if len(src_mac) < 1:
        print ("No interface for output")
        sys.exit(1)
    src_mac = src_mac[0]
    src_ip = None
    if src_mac =="00:00:00:00:00:01":
        src_ip = "10.0.0.1"
    elif src_mac =="00:00:00:00:00:02":
        src_ip = "10.0.0.2"
    elif src_mac =="00:00:00:00:00:03":
        src_ip = "10.0.0.3"
    else:
        print ("Invalid source host")
        sys.exit(1)

    if dst == 'h1':
        dst_mac = "00:00:00:00:00:01"
        dst_ip = "10.0.0.1"
    elif dst == 'h2':
        dst_mac = "00:00:00:00:00:02"
        dst_ip = "10.0.0.2"
    elif dst == 'h3':
        dst_mac = "00:00:00:00:00:03"
        dst_ip = "10.0.0.3"
    else:
        print ("Invalid host to send to")
        sys.exit(1)

    total_pkts = 0
    #random_ports = random.sample(xrange(1024, 65535), 10)
    #for port in random_ports:
	#um_packets = random.randint(50, 250)
        #for i in range(num_packets):
	
    for i in range (0,10):
            #data = randomword(100)
            data = "abcd"
            p = Ether(dst=dst_mac,src=src_mac)/IP(dst=dst_ip,src="10.1.1.2")
            p = p/TCP(dport=54321)/Raw(load=data)
            print p.show()
            sendp(p, iface = "eth0")
            total_pkts += 1
    print "Sent %s packets in total" % total_pkts

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python send.py dst_host_name")
        sys.exit(1)
    else:
        dst_name = sys.argv[1]
        send_random_traffic(dst_name)
