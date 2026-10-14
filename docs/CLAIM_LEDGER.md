# Claim-to-evidence ledger

I personally executed and reviewed Lab 1, with 26 successful automated checks. The table separates that commissioning work from manual diagnosis and ongoing practice. Reference verification for Labs 2 and 3 remains separate from my personal network run.

| Capability | Actual implementation evidence | Candidate validation | Boundary |
|---|---|---|---|
| VLAN configuration/trunk fault isolation | Lab1 bridge tables, tagged captures, affected/unaffected checks | Personal automated commissioning reviewed; manual diagnosis pending | Linux bridges; Cisco/Packet Tracer execution pending |
| IPv4/DHCP/DNS diagnosis | Lab1 lease/options, address/routes, direct-IP versus named requests | Personal commissioning/result review completed; manual diagnosis pending | Isolated fictional network |
| OSPF routing and recovery | Lab1 Full neighbors, installed routes, area fault, alternate forwarding and config restart | Personal commissioning/result review completed; manual diagnosis pending | FRR 8.4; accelerated lab timers |
| Management access policy | Actual nftables counters and SSH TCP/banner checks | Personal automated policy checks reviewed | Authenticated SSH administration not tested |
| Linux service/log troubleshooting | Lab2 syntax failure, startup log, process/socket evidence and rollback | Pending | Container supervisor; no systemd/VM boot claim |
| Permissions and storage faults | Lab2 403/log evidence and real HTTP 507/ENOSPC response | Pending | Bounded disposable filesystem, no physical disk fault |
| Backup restoration | Real archive/manifest, clean-target hashes/modes and useful response | Pending | Config/data backup; ephemeral events excluded |
| Monitoring and alert delivery | Lab3 real probe/scrape metrics and actual Alertmanager webhook journal | Pending | Local HTTP receiver; no email/SMS/Slack or physical metrics |
| Incident/change/handover | Recorded verification observations plus operations/practice guide | Pending | Candidate-authored report and verbal handover still required |
| Rack/cable work-order awareness | Executed consistency check on fictional fixture | Pending | Tabletop; no physical installation/testing |

The NCC academic record is separately verified against the private supplied documents. It supports academic foundations and does not automatically satisfy these practical validation rows. This ledger does not add certification, engineering employment or production responsibility.
