# First practice lesson — understand the network before running it

Read this before your first personal Lab 1 session. The addresses below describe the implemented lab. Commands are examples for your own retained session, not a claim that you personally executed them.

## What each part does

The client `c20` needs to request a service on `srv`. `sw1` and `sw2` carry the local Ethernet traffic. `r1`, `r2` and `r3` move IP packets between different networks. `r1` also supplies client DHCP/DNS and filters forwarded traffic. The server provides an actual HTTP response and an SSH TCP listener.

An IPv4 address identifies an interface at the network layer; an Ethernet MAC address identifies an endpoint on the current Ethernet link. A switch learns MAC locations and forwards Ethernet frames. A router selects the next hop from an IP routing table, removes the received link-layer frame and sends the packet in a new frame for the next link. In this lab, client/server IP addresses remain unchanged because lab forwarding does not apply NAT; link-layer addresses change along the routed path.

Do not confuse three different observations: an interface can be up, a route can exist, and an application can still fail. Each needs its own evidence.

## Subnets and the gateway

`10.20.0.50/24` belongs to `10.20.0.0/24`. The mask is `255.255.255.0`, the broadcast is `10.20.0.255`, and ordinary usable host addresses run from `.1` through `.254`. The chosen gateway is `10.20.0.1`. Being inside that usable range does not make `.254` a router: the lab has not assigned it to a forwarding device.

The server `10.30.0.10` is outside the client's /24. The client therefore sends the frame to its configured gateway's MAC address, discovered through ARP, rather than trying to ARP directly for the remote server. The IP packet still names the server as its destination.

A `/30` router link contains four addresses. For `10.255.12.0/30`, `.0` is the network, `.1` and `.2` are the two ordinary usable endpoints, and `.3` is the broadcast. That is why r1 and r2 use `.1` and `.2` on this link. Explain the other two /30 links yourself before changing them.

## VLANs and trunks

VLAN 20 is the client's Ethernet broadcast domain; VLAN 10 is management. The access ports accept untagged endpoint frames and classify them into the assigned VLAN. The inter-switch and gateway trunks carry the corresponding 802.1Q VLAN tags. Linux bridge port membership determines which tagged frames can pass.

VLAN separation is layer 2 separation. Once a router connects VLANs, routed communication depends on the routing and firewall policy. This lab intentionally permits ICMP diagnostics and specified server traffic; it does not claim that all traffic between every segment is blocked. The server segment is routed behind r2.

Deleting VLAN 20 from only sw2's trunk should affect the client path while preserving VLAN 10. That contrast is useful evidence: it narrows the fault from a whole-switch or whole-router failure to a segment-specific path. A single failed ping without the comparison would not prove a VLAN error.

The Linux topology has no redundant layer-2 path, so STP is disabled. STP/RSTP practice belongs to the separate simulator exercise. OSPF's triangle provides routed alternatives and is not a layer-2 loop.

## DHCP and DNS solve different problems

DHCP supplies the client's address, subnet mask, gateway and DNS-server option. Read the actual saved lease rather than assuming that receiving any address means all options are correct. The lab reserves `10.20.0.50` for this client's current MAC address.

DNS maps `app.lab` to `10.30.0.10`. Here the DNS server is also r1 at `10.20.0.1`. This local lab DNS fixture has no general Internet resolver requirement. A correct address/gateway does not establish a correct name record.

Compare `dig +short app.lab`, direct-IP HTTP and named HTTP. If direct-IP HTTP succeeds while the DNS answer points to `.99` and named HTTP fails, the result supports a name-record problem rather than a broken service or route. If both forms fail, investigate further instead of concluding that everything is DNS.

## Static routing, OSPF and the return path

The first stage uses explicitly configured static routes. The runner then removes those routes and starts actual FRR OSPF. OSPF exchanges link-state information and installs a route based on the configured topology/costs. The direct r1-r2 path has a lower configured cost than the path through r3.

Router IDs `10.255.0.1`, `.2` and `.3` are unique OSPF identifiers here. They are not configured loopback interfaces, so do not assume you can ping a router ID as an assigned address.

A Full neighbor state means the adjacency has completed its database synchronization. It does not by itself prove that the desired server route exists, that a firewall allows the request or that the application responds. Verify all three: neighbor, selected route and useful client request.

`ip route get 10.30.0.10` on r1 shows a kernel lookup from that router. Its displayed `src` is the source address chosen for a locally originated router packet; it is not evidence that the forwarded client's address was translated. Inspect the actual client packets to establish their source.

Replies also need a return path: srv sends remote replies to r2, r2 routes toward the client network through r1, and r1 forwards to VLAN 20. One-way reachability can fail when the forward route is correct but the reply route or policy is wrong.

Changing the spare r1-r3 adjacency's area can leave the primary application path healthy while redundancy is lost. A green application check therefore does not establish that every resilience component is healthy. Read the neighbor/interface records and explain the affected capability.

## Forwarding policy and the service request

The r1 nftables `forward` chain governs transit packets. Its policy permits established/related return traffic, permits management-origin server SSH TCP traffic, explicitly rejects client-origin server SSH TCP traffic, permits the HTTP service and lab ICMP diagnostics, and drops other forwarding. DNS/DHCP addressed to r1 itself are local services; they are not the same forwarding case.

The SSH test reads an actual protocol banner after a TCP connection. It does not authenticate a user, demonstrate key management or establish successful shell administration. Explain that boundary accurately in an interview.

A firewall rejection is meaningful when the intended service is confirmed healthy from an allowed source and the appropriate rule counter increases. A failed connection to an already-dead server would not prove that the policy caused the denial.

The full client request is: receive DHCP options; resolve `app.lab`; select the gateway because the server is remote; use ARP and VLAN 20 forwarding; reach r1; pass the HTTP forwarding rule; follow the selected route through r2; receive the real server response; follow the return route and established-connection rule back to the client.

## Choose a check that answers a question

| Question | Useful command in the appropriate lab node | What the evidence establishes |
|---|---|---|
| Which address/interface is in use? | `ip -br addr` | Actual assigned addresses/interface state |
| Where will traffic go? | `ip route`, `ip route get 10.30.0.10` | Route/default/next-hop selection |
| Which VLAN can this port carry? | `bridge vlan show` | Linux port VLAN membership/tagging |
| What name answer is returned? | `dig +short app.lab` | DNS response from the configured resolver |
| Did adjacency form? | `vtysh -c 'show ip ospf neighbor'` | Actual neighbor states |
| Which policy processed traffic? | `nft list ruleset` | Rules and observed counters |
| Is a service listening? | `ss -lntp` | Listening sockets; not complete client availability |
| Does the client receive useful service? | `curl --noproxy '*' -fsS http://app.lab/` | Actual HTTP outcome along the client path |

## Carry the same reasoning into the other labs

In Lab 2, config on disk and a running worker can differ. Syntax checking rejects an invalid change; a restart can expose an actual outage. A 403 plus a permission-denied log supports an access problem. HTTP health can remain green while the journal write fails with ENOSPC. A backup's existence is weaker evidence than restored bytes, permissions and useful service on a clean target.

In Lab 3, Prometheus `up` describes the scrape connection to the exporter. The separate application-probe metric describes a real service check. When the exporter fails, independently test the service and identify the monitoring gap. A maintenance silence suppresses notification; it does not fix the service or stop Prometheus from evaluating the alert.

Your first personal objective is to explain these relationships using your actual run, then diagnose one changed fault with appropriate assistance recorded. Use the [practice guide](CANDIDATE_PRACTICE.md), retain evidence, and ask about any command whose purpose you cannot explain. This is preparation for supervised junior work, not a claim of production experience.
