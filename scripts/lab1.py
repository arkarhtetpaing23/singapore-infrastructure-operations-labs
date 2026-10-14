"""Real Linux bridge/VLAN, DHCP/DNS, nftables and FRR forwarding exercises."""
import json
import re
import time
from labcore import ROOT

APP='ARKAR LAB1 SERVICE'
NETS={
 'client':('c20','sw1'), 'management':('m10','sw1'),
 'trunk':('sw1','sw2'), 'gateway':('sw2','r1'),
 'r12':('r1','r2'), 'r13':('r1','r3'), 'r23':('r2','r3'),
 'server':('r2','srv')}
IFACES={
 ('c20','client'):('lan',None), ('m10','management'):('lan','10.10.0.50/24'),
 ('sw1','client'):('p-client',None), ('sw1','management'):('p-mgmt',None),
 ('sw1','trunk'):('p-trunk',None), ('sw2','trunk'):('p-trunk',None),
 ('sw2','gateway'):('p-gw',None), ('r1','gateway'):('lan',None),
 ('r1','r12'):('p-r2','10.255.12.1/30'), ('r2','r12'):('p-r1','10.255.12.2/30'),
 ('r1','r13'):('p-r3','10.255.13.1/30'), ('r3','r13'):('p-r1','10.255.13.2/30'),
 ('r2','r23'):('p-r3','10.255.23.1/30'), ('r3','r23'):('p-r2','10.255.23.2/30'),
 ('r2','server'):('lan','10.30.0.1/24'), ('srv','server'):('lan','10.30.0.10/24')}

def http(lab,node='c20',host='app.lab'):
    return lab.ex(node,f"curl --noproxy '*' --connect-timeout 1 --max-time 2 -fsS http://{host}/",ok=(0,6,7,22,28)).stdout.strip()

def ssh_banner(lab,node):
    script="python3 - <<'PY'\nimport socket\ntry:\n s=socket.create_connection(('10.30.0.10',22),1)\n print(s.recv(100).decode().strip()); s.close()\nexcept OSError as e: print(type(e).__name__,str(e))\nPY"
    return lab.ex(node,script).stdout

def dnsconf(mac,ip='10.30.0.10'):
    return f'''interface=lan.20
bind-interfaces
no-resolv
no-hosts
domain-needed
address=/app.lab/{ip}
dhcp-range=10.20.0.50,10.20.0.60,255.255.255.0,5m
dhcp-host={mac},10.20.0.50
dhcp-option=option:router,10.20.0.1
dhcp-option=option:dns-server,10.20.0.1
log-dhcp
log-queries
log-facility=/var/log/lab/dnsmasq.log
pid-file=/run/dnsmasq-lab.pid
'''

def ospfconf(router):
    rid={'r1':'10.255.0.1','r2':'10.255.0.2','r3':'10.255.0.3'}[router]
    ports={'r1':[('p-r2',10),('p-r3',50)],'r2':[('p-r1',10),('p-r3',10)],'r3':[('p-r1',50),('p-r2',10)]}[router]
    s=f'hostname {router}\nlog file /tmp/frr.log\n'
    for iface,cost in ports:
        s+=f'interface {iface}\n ip ospf network point-to-point\n ip ospf area 0\n ip ospf cost {cost}\n ip ospf hello-interval 1\n ip ospf dead-interval 4\n!\n'
    if router=='r1':
        for iface in ['lan.10','lan.20']: s+=f'interface {iface}\n ip ospf area 0\n ip ospf passive\n!\n'
    if router=='r2': s+='interface lan\n ip ospf area 0\n ip ospf passive\n!\n'
    s+=f'router ospf\n ospf router-id {rid}\n!\n'
    return s

def run(lab):
    for net in NETS: lab.network(net)
    for node in ['c20','m10','sw1','sw2','r1','r2','r3','srv']:
        first=next(net for net,pair in NETS.items() if node in pair)
        lab.node(node,caps=True,network=first,sysctls={'net.ipv4.ip_forward':'1'} if node in ['r1','r2','r3'] else None,frr=node in ['r1','r2','r3'])
    lab.versions()
    for net,(a,b) in NETS.items(): lab.link(net,a,b)
    for (node,net),(iface,addr) in IFACES.items(): lab.configure_interface(node,net,iface,addr)
    lab.write('topology.json',{'links':NETS,'interfaces':{f'{n}/{net}':{'name':v[0],'address':v[1]} for (n,net),v in IFACES.items()},'vlans':{'10':'management','20':'client'},'service':'10.30.0.10'})
    for node in ['sw1','sw2']:
        lab.ex(node,'ip link add br0 type bridge vlan_filtering 1 stp_state 0; ip link set br0 up')
        ports=['p-client','p-mgmt','p-trunk'] if node=='sw1' else ['p-trunk','p-gw']
        for p in ports: lab.ex(node,f'ip link set {p} master br0; bridge vlan del dev {p} vid 1')
    lab.ex('sw1','bridge vlan add dev p-client vid 20 pvid untagged; bridge vlan add dev p-mgmt vid 10 pvid untagged; bridge vlan add dev p-trunk vid 10; bridge vlan add dev p-trunk vid 20')
    lab.ex('sw2','bridge vlan add dev p-trunk vid 10; bridge vlan add dev p-trunk vid 20; bridge vlan add dev p-gw vid 10; bridge vlan add dev p-gw vid 20')
    lab.ex('r1','ip link add link lan name lan.10 type vlan id 10; ip link add link lan name lan.20 type vlan id 20; ip addr add 10.10.0.1/24 dev lan.10; ip addr add 10.20.0.1/24 dev lan.20; ip link set lan.10 up; ip link set lan.20 up')
    for n in ['r1','r2','r3']:
        value=lab.ex(n,'cat /proc/sys/net/ipv4/ip_forward').stdout.strip()
        lab.check(f'{n} container-scoped forwarding enabled',value=='1',value)
    lab.ex('m10','ip route add default via 10.10.0.1')
    lab.ex('srv','ip route add default via 10.30.0.1; mkdir -p /srv/http /run/sshd; ssh-keygen -A; /usr/sbin/sshd -o PasswordAuthentication=no -o PermitRootLogin=no')
    lab.put('srv','/etc/nginx/nginx.conf',f"events {{}}\nhttp {{ server {{ listen 80; location / {{ default_type text/plain; return 200 '{APP}\\n'; }} }} }}\n")
    lab.ex('srv','nginx -t; nginx')
    nft=(ROOT/'configs/lab1/firewall.nft').read_text()
    lab.put('r1','/tmp/firewall.nft',nft)
    lab.ex('r1','nft -f /tmp/firewall.nft')
    mac=json.loads(lab.ex('c20','ip -j link show lan').stdout)[0]['address']
    lab.put('r1','/etc/dnsmasq-lab.conf',dnsconf(mac))
    lab.ex('r1','mkdir -p /var/log/lab; dnsmasq --conf-file=/etc/dnsmasq-lab.conf')
    lab.docker('exec','-d',lab.nodes['sw2'],'sh','-c',"tcpdump -U -i p-gw -w /tmp/vlan.pcap 'vlan and (net 10.10.0.0/24 or net 10.20.0.0/24 or net 10.30.0.0/24 or udp port 67 or udp port 68)' >/tmp/capture.log 2>&1")
    lab.docker('exec','-d',lab.nodes['r1'],'sh','-c',"tcpdump -U -i p-r2 -w /tmp/ospf.pcap 'ip proto 89 or icmp' >/tmp/capture.log 2>&1")
    lab.ex('c20','dhclient -4 -1 -v -pf /tmp/dhclient.pid -lf /tmp/dhclient.leases lan',timeout=20)
    lease=lab.ex('c20','cat /tmp/dhclient.leases; ip -j addr show lan; ip route').stdout
    lab.write('dhcp-lease-and-route.txt',lease)
    lab.check('DHCP address, router and DNS options',all(x in lease for x in ['10.20.0.50','10.20.0.1','domain-name-servers']),lease)
    lab.ex('c20',"printf 'nameserver 10.20.0.1\n' > /etc/resolv.conf")
    lab.ex('r1','ip route add 10.30.0.0/24 via 10.255.12.2')
    lab.ex('r2','ip route add 10.10.0.0/24 via 10.255.12.1; ip route add 10.20.0.0/24 via 10.255.12.1')
    lab.check('Static-routing application commissioning',http(lab)==APP,http(lab))
    b=ssh_banner(lab,'m10')
    lab.check('Management segment reaches actual SSH listener',b.startswith('SSH-2.0-'),b)
    lab.check('Client segment denied SSH while HTTP works',not ssh_banner(lab,'c20').startswith('SSH-2.0-') and http(lab)==APP,ssh_banner(lab,'c20'))
    counters=lab.ex('r1','nft -a list ruleset').stdout
    lab.write('firewall-baseline.txt',counters)
    deny_line=next(x for x in counters.splitlines() if 'client-ssh-denied' in x)
    denied_packets=int(re.search(r'counter packets (\d+)',deny_line).group(1))
    lab.check('Explicit SSH deny rule counted traffic',denied_packets>0,deny_line)
    lab.ex('r1','ip route del 10.30.0.0/24')
    lab.ex('r2','ip route del 10.10.0.0/24; ip route del 10.20.0.0/24')
    for n in ['r1','r2','r3']:
        lab.put(n,'/etc/frr/zebra.conf',f'hostname {n}\nlog file /tmp/zebra.log\n')
        lab.put(n,'/etc/frr/ospfd.conf',ospfconf(n))
        lab.put(n,'/etc/frr/vtysh.conf','no service integrated-vtysh-config\n')
        lab.ex(n,'mkdir -p /run/frr; chown frr:frr /run/frr; /usr/lib/frr/zebra -d -f /etc/frr/zebra.conf; /usr/lib/frr/ospfd -d -f /etc/frr/ospfd.conf')
    lab.wait('OSPF baseline forwarding',lambda: 'p-r2' in lab.ex('r1','ip route get 10.30.0.10').stdout and http(lab)==APP,seconds=30)
    for n in ['r1','r2','r3']:
        out=lab.ex(n,"vtysh -c 'show ip ospf neighbor' -c 'show ip route' -c 'show ip ospf interface' ").stdout
        lab.write(f'ospf-baseline-{n}.txt',out)
        lab.check(f'{n} two Full OSPF adjacencies',out.count('Full/')>=2,out)
    lab.check('OSPF installed route and application forwarding',http(lab)==APP,lab.ex('r1','ip route get 10.30.0.10').stdout)
    lab.write('vlans-baseline.txt',lab.ex('sw1','bridge vlan show').stdout+lab.ex('sw2','bridge vlan show').stdout)
    lab.ex('sw2','bridge vlan del dev p-trunk vid 20')
    fault=lab.ex('c20','ping -c 1 -W 1 10.20.0.1',ok=(0,1)).returncode
    unaffected=lab.ex('m10','ping -c 1 -W 1 10.10.0.1',ok=(0,1)).returncode
    lab.write('vlan-fault.txt',lab.ex('sw2','bridge vlan show').stdout)
    lab.check('VLAN fault affects VLAN 20 while VLAN 10 works',fault==1 and unaffected==0,{'client_ping_rc':fault,'management_ping_rc':unaffected})
    lab.ex('sw2','bridge vlan add dev p-trunk vid 20')
    lab.check('VLAN recovery restores application',http(lab)==APP,http(lab))
    lab.ex('c20','ip route replace default via 10.20.0.254')
    gateway=lab.ex('c20','ping -c 1 -W 1 10.20.0.1',ok=(0,1)).returncode
    lab.check('Wrong gateway: local gateway reachable, remote app fails',gateway==0 and http(lab,host='10.30.0.10')!=APP,lab.ex('c20','ip route').stdout)
    lab.ex('c20','ip route replace default via 10.20.0.1')
    lab.check('Gateway recovery',http(lab)==APP,http(lab))
    lab.ex('r1','kill "$(cat /run/dnsmasq-lab.pid)"; sleep 0.2')
    lab.put('r1','/etc/dnsmasq-lab.conf',dnsconf(mac,'10.30.0.99'))
    lab.ex('r1','dnsmasq --conf-file=/etc/dnsmasq-lab.conf')
    answer=lab.ex('c20','dig +short app.lab').stdout.strip()
    lab.check('DNS fault: wrong record, direct-IP service healthy',answer=='10.30.0.99' and http(lab,host='10.30.0.10')==APP and http(lab)!=APP,answer)
    lab.ex('r1','kill "$(cat /run/dnsmasq-lab.pid)"; sleep 0.2')
    lab.put('r1','/etc/dnsmasq-lab.conf',dnsconf(mac))
    lab.ex('r1','dnsmasq --conf-file=/etc/dnsmasq-lab.conf')
    lab.check('DNS recovery',http(lab)==APP,http(lab))
    # Single area mismatch on the spare link: the preferred path still serves traffic.
    lab.ex('r3',"vtysh -c 'configure terminal' -c 'interface p-r1' -c 'no ip ospf area 0' -c 'ip ospf area 1'")
    lab.wait('Spare adjacency removed',lambda:'10.255.0.3' not in lab.ex('r1',"vtysh -c 'show ip ospf neighbor'").stdout,seconds=15)
    lab.write('ospf-area-fault.txt',lab.ex('r1',"vtysh -c 'show ip ospf neighbor' -c 'show ip ospf interface'").stdout+lab.ex('r3',"vtysh -c 'show ip ospf interface'").stdout)
    lab.check('OSPF area mismatch removes spare adjacency but app remains available',http(lab)==APP,http(lab))
    lab.ex('r3',"vtysh -c 'configure terminal' -c 'interface p-r1' -c 'no ip ospf area 1' -c 'ip ospf area 0'")
    lab.wait('Spare adjacency recovery',lambda:lab.ex('r1',"vtysh -c 'show ip ospf neighbor'").stdout.count('Full/')==2)
    lab.check('OSPF area correction restores spare adjacency',True,lab.ex('r1',"vtysh -c 'show ip ospf neighbor'").stdout)
    lab.docker('exec','-d',lab.nodes['c20'],'sh','-c','ping -D -i 0.2 -c 60 10.30.0.10 >/tmp/failover-ping.txt 2>&1')
    time.sleep(0.5)
    start=time.monotonic()
    lab.ex('r1','ip link set p-r2 down')
    lab.wait('Alternate forwarding path',lambda:'p-r3' in lab.ex('r1','ip route get 10.30.0.10').stdout and http(lab)==APP,seconds=20)
    elapsed=time.monotonic()-start
    route=lab.ex('r1','ip route get 10.30.0.10').stdout
    lab.write('failover.json',{'observed_restoration_seconds':round(elapsed,3),'measurement':'Controller observation includes command/poll latency; not a production convergence benchmark','route':route})
    lab.check('Primary-link loss forwards via r3 and restores HTTP',True,{'seconds':elapsed,'route':route})
    lab.ex('r1','ip link set p-r2 up')
    lab.wait('Preferred path returns',lambda:'p-r2' in lab.ex('r1','ip route get 10.30.0.10').stdout and http(lab)==APP)
    lab.check('Primary-link recovery returns preferred path',True,lab.ex('r1','ip route get 10.30.0.10').stdout)
    # Restart FRR from the actual saved configuration, not generated expected output.
    for n in ['r1','r2','r3']:
        lab.ex(n,"vtysh -c 'write memory'; pkill ospfd; /usr/lib/frr/ospfd -d -f /etc/frr/ospfd.conf")
    lab.wait('Saved FRR configuration restart',lambda: http(lab)==APP and 'p-r2' in lab.ex('r1','ip route get 10.30.0.10').stdout and all(lab.ex(n,"vtysh -c 'show ip ospf neighbor'").stdout.count('Full/')==2 for n in ['r1','r2','r3']))
    lab.check('Saved OSPF configuration restores forwarding after daemon restart',True,http(lab))
    for n in ['r1','r2','r3']:
        lab.copy_out(n,'/etc/frr/ospfd.conf',f'actual-configs/{n}-ospfd.conf')
        lab.write(f'ospf-final-{n}.txt',lab.ex(n,"vtysh -c 'show ip ospf neighbor' -c 'show ip route'").stdout)
    for n in ['sw2','r1']: lab.ex(n,'pkill -INT tcpdump || true')
    time.sleep(0.3)
    lab.copy_out('sw2','/tmp/vlan.pcap','captures/vlan.pcap')
    lab.copy_out('r1','/tmp/ospf.pcap','captures/ospf.pcap')
    vl=lab.ex('sw2','tcpdump -e -nn -r /tmp/vlan.pcap -c 25').stdout
    v10=lab.ex('sw2',"tcpdump -e -nn -r /tmp/vlan.pcap -c 5 'vlan 10'").stdout
    v20=lab.ex('sw2',"tcpdump -e -nn -r /tmp/vlan.pcap -c 5 'vlan 20'").stdout
    op=lab.ex('r1','tcpdump -nn -r /tmp/ospf.pcap -c 25').stdout
    lab.write('captures/vlan-excerpt.txt',vl)
    lab.write('captures/vlan10-excerpt.txt',v10)
    lab.write('captures/vlan20-excerpt.txt',v20)
    lab.write('captures/ospf-excerpt.txt',op)
    lab.check('Actual tagged VLAN and OSPF packets captured','vlan 10' in v10 and 'vlan 20' in v20 and 'OSPF' in op,{'vlan10_excerpt':v10,'vlan20_excerpt':v20,'ospf_excerpt':op})
    lab.ex('c20','pkill -INT ping || true')
    lab.write('failover-ping.txt',lab.ex('c20','cat /tmp/failover-ping.txt').stdout)
    lab.write('dnsmasq-log.txt',lab.ex('r1','cat /var/log/lab/dnsmasq.log').stdout)
    lab.write('firewall-final.txt',lab.ex('r1','nft -a list ruleset').stdout)
    lab.check('Final allowed/denied traffic matrix',http(lab)==APP and ssh_banner(lab,'m10').startswith('SSH-2.0-') and not ssh_banner(lab,'c20').startswith('SSH-2.0-'),'HTTP allowed; management SSH TCP/banner allowed; client SSH TCP denied. SSH authentication not tested.')

