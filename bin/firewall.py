#!/usr/bin/python
import iptc

internetif = "eth0"
lanif = "wlan0"

INPUT_Chain = iptc.Chain(iptc.Table(iptc.Table.FILTER), "INPUT")
OUTPUT_Chain = iptc.Chain(iptc.Table(iptc.Table.FILTER), "OUTPUT")
FORWARD_Chain = iptc.Chain(iptc.Table(iptc.Table.FILTER),"FORWARD")
POSTROUTE_Chain = iptc.Chain(iptc.Table(iptc.Table.NAT), "POSTROUTING")
PREROUTE_Chain = iptc.Chain(iptc.Table(iptc.Table.NAT), "PREROUTING")
INPUT_Chain.flush()
OUTPUT_Chain.flush()
FORWARD_Chain.flush()
POSTROUTE_Chain.flush()

# loopback rule - accept all the things
lo_rule = iptc.Rule()
lo_rule.in_interface = "lo"
lo_target = iptc.Target(lo_rule,"ACCEPT")
lo_rule.target = lo_target
INPUT_Chain.insert_rule(lo_rule)
#slightly mod, then use in the output chain too
lo_rule.in_interface = None
lo_rule.out_interface = "lo"
OUTPUT_Chain.insert_rule(lo_rule)

#LAN-side rules
#iptables -A INPUT -i $lan -j ACCEPT
#iptables -A OUTPUT -o $lan -j ACCEPT

#iptables -A FORWARD -i $internet -o $lan -j ACCEPT
lan_rule = iptc.Rule()
lan_rule.out_interface = internetif
lan_rule.in_interface = lanif
lan_rule.target = iptc.Target(lan_rule,"ACCEPT")
FORWARD_Chain.insert_rule(lan_rule)

#iptables -A FORWARD -i $lan -o $internet -j ACCEPT
lan_rule.out_interface = lanif
lan_rule.in_interface = internetif
FORWARD_Chain.insert_ruel(lan_rule)

#iptables -A POSTROUTING -t nat -o $internet -j MASQUERADE
#iptables -t nat -A PREROUTING -i $lan -p tcp --dport 80 -j DNAT --to-destination.......
