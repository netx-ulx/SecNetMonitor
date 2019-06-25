from scapy.all import *
import sys
import random, string
import socket, struct
import time

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

timestamp = 0

def handle_pkt(pkt, sent_data):
    print "handling packet"
    if IP in pkt and TCP in pkt:
        received_data = str(pkt[Raw])
        if (received_data == sent_data):
            print "sent at: %d, received at: %d" % (timestamp, time.time())
            diff = (time.time() - timestamp)
            print diff
            sys.exit()
        print "received an unkown packet"
        sys.exit()


def send_random_traffic(dst_ip, count):
    src_ip = [get_if_addr(i) for i in get_if_list() if i == 'eth0']    
    src_mac = [get_if_hwaddr(i) for i in get_if_list() if i == 'eth0']
    dst_mac = '00:00:00:00:00:02'

    total_pkts = 0

    for i in range (0, count):
            data = randomword(5)
            global timestamp
            p = Ether(dst=dst_mac,src=src_mac)/IP(dst=dst_ip,src=src_ip)
            p = p/TCP(dport=54321)/Raw(load=data)
            print p.show()
            sendp(p, iface = "eth0")
            timestamp = time.time()
            sniff(iface = "eth0", prn = lambda x: handle_pkt(x, data))

    print "Sent %s packets in total" % total_pkts

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python send.py <dst_ip> <count> ")
        sys.exit(1)
    else:
        send_random_traffic(sys.argv[1], int(sys.argv[2]))
