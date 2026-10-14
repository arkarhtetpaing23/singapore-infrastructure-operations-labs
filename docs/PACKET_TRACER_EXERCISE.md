# Packet Tracer switching exercise — execution pending

Arkar reports that he needs to create a Cisco Networking Academy account. Packet Tracer was not found in the workspace checks. This document is an exercise specification and configuration starting point; no `.pkt` file, screenshot, successful simulator result or candidate execution is claimed.

Use [Cisco's official download instructions](https://www.netacad.com/skillsforall/files/Cisco_Packet_Tracer_Download_and_Installation_Instructions.pdf) and [official downloads page](https://www.netacad.com/resources/lab-downloads). Create your own account and sign in privately. Keep passwords and verification codes private. The installer and GUI launch must be verified on your actual operating system.

## Small initial topology

- Two simulated Catalyst 2960 switches: SW1 and SW2.
- Client PC on SW1 FastEthernet0/1; management PC on SW1 FastEthernet0/2.
- SW1 GigabitEthernet0/1 to SW2 GigabitEthernet0/1 as the trunk.
- Router 2911 GigabitEthernet0/0 to SW2 GigabitEthernet0/2 as a trunk.
- VLAN 10 management: 10.10.0.50/24, gateway 10.10.0.1.
- VLAN 20 client: 10.20.0.50/24, gateway 10.20.0.1.

Use the actual simulator's available model/interface names; check the device before copying a command. Preserve all error messages and adaptations.

SW1 starting configuration:

```text
enable
configure terminal
hostname SW1
vlan 10
 name MANAGEMENT
vlan 20
 name CLIENT
interface FastEthernet0/1
 switchport mode access
 switchport access vlan 20
 spanning-tree portfast
interface FastEthernet0/2
 switchport mode access
 switchport access vlan 10
 spanning-tree portfast
interface GigabitEthernet0/1
 switchport mode trunk
 switchport trunk allowed vlan 10,20
end
copy running-config startup-config
```

On SW2 create VLANs 10 and 20, and configure GigabitEthernet0/1 and 0/2 as trunks allowing both VLANs. On the router:

```text
enable
configure terminal
hostname R1
interface GigabitEthernet0/0
 no shutdown
interface GigabitEthernet0/0.10
 encapsulation dot1Q 10
 ip address 10.10.0.1 255.255.255.0
interface GigabitEthernet0/0.20
 encapsulation dot1Q 20
 ip address 10.20.0.1 255.255.255.0
end
copy running-config startup-config
```

This simple stage permits routed communication between the two VLANs; VLANs alone do not implement the Linux lab's firewall policy. Explain that distinction. Never describe these snippets as executed IOS evidence until the simulator output exists.

## Required observations

Save the real `.pkt` file, device configurations and outputs of `show vlan brief`, `show interfaces trunk`, `show spanning-tree`, `show ip interface brief` and actual endpoint tests. Record the installed Packet Tracer version. Explain how ARP, tagging and routing support the observed traffic.

Fault 1: allow only VLAN 10 on SW2's SW1-facing trunk. Compare management and client connectivity, inspect the trunk and correct it.

Fault 2: move the client access port to VLAN 10 while leaving the client address in 10.20.0.0/24. Explain the mismatch using port state and endpoint addressing, then restore it.

Optional STP extension: add a second simulated switch-to-switch trunk only after the initial topology passes. Verify which port blocks and why; shut the active path, observe an actual simulator reconvergence and restore it. Record the actual spanning-tree mode. The Linux bridge lab uses an acyclic topology with STP disabled; it supplies no RSTP result.

Candidate explain-back and changed-fault diagnosis are required in addition to screenshots. Packet Tracer output is simulation evidence, not physical cable certification or production-switch administration.
