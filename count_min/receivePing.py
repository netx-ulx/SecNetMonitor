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

from scapy.all import *

def handle_pkt(pkt):

    dst_mac = '00:00:00:00:00:01'
    src_mac = '00:00:00:00:00:02'

    if IP in pkt and TCP in pkt:
        src_ip = pkt[IP].src
        dst_ip = pkt[IP].dst
        proto = pkt[IP].proto
        sport = pkt[TCP].sport
        dport = pkt[TCP].dport
        data = pkt[Raw]
        
        p = Ether(dst=dst_mac,src=src_mac)/IP(dst=src_ip,src=dst_ip)
        p = p/TCP(dport=54321)/Raw(load=data)
        sendp(p, iface = "eth0")
        print "sent"

def main():
    sniff(iface = "eth0",
          prn = lambda x: handle_pkt(x))

if __name__ == '__main__':
    main()
