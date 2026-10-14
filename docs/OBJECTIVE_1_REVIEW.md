# Objective 1 engineering review and remaining candidate validation

Review scope: the three executable Linux software laboratories, their actual assistant-run evidence, reproduction materials and claim boundaries. The candidate's initial written understanding has been partially assessed; practical understanding is not yet established. Objective 1 remains in progress until the agreed personal/simulator work is addressed. The candidate subsequently issued NEXT, authorizing portfolio publication work without treating the outstanding practice as complete.

## Verified implementation

| Project | Actual successful run, UTC | Recorded checks | Outcome |
|---|---|---:|---|
| Network | lab1-20261014T193910216722Z | 26 | VLAN/DHCP/DNS, static then OSPF forwarding, management policy, four configuration faults, primary-path failure/recovery, daemon configuration restart and actual captures |
| Service recovery | lab2-20261014T194249743051Z | 15 | Service/data persistence, rejected syntax, actual startup outage, rollback, permission fault, bounded ENOSPC and clean-target restore |
| Monitoring operations | lab3-20261014T194415047830Z | 11 | Rule tests plus actual pending/firing/resolved delivery, exporter-only failure, bounded silence and fictional work-order review |

All three successful runs used image ID `sha256:871d0b1b187dbdc53ec6f4918c97c6dc3c35d20edc3cd2f2f4d812537fd560d6`. The Debian base digest is pinned in the Dockerfile; tested package versions are recorded in each run. A future APT build can resolve different package versions, so this is functional reproduction with recorded dependencies, not a claim of permanently byte-identical rebuilds. A changed build requires appropriate verification.

Successful runs recorded their source hashes, and relevant runner/runtime/configuration hashes were compared to the delivered source. Actual isolation settings were checked, including capped memory, internal networks, absence of privileged mode/host networking/host mounts/published ports and the restricted FRR capability exception. Cleanup completed without recorded errors.

## Evidence reviewed

Network evidence includes genuine VLAN 10/20 frame headers, DHCP options, route/neighbor state and firewall counters. The explicit SSH-deny rule counted two baseline packets and the management allow rule counted traffic. The SSH check establishes TCP/protocol-banner access, not authenticated administration. Primary-path loss restored useful HTTP via r3 in an observed 3.765 seconds including command/poll latency. This is one accelerated software-lab observation.

Service evidence contains the unknown-directive startup error, direct-IP timeout and Docker-alias DNS withdrawal while the container was stopped. Treating that DNS withdrawal as an unexpected runner error was corrected; direct-IP and process/log evidence now distinguish the actual startup failure. Real writes returned HTTP 507/errno 28 on the bounded filesystem. The separate restore target served version 2 with matching configuration/data hashes and modes; actual restore/validation observation was 0.627 seconds. It is not a production RTO. Ephemeral journal data is excluded and not restored.

Monitoring evidence contains actual local webhook deliveries: application firing and resolution, then exporter firing and resolution. The first firing delivery was observed after 8.592 seconds including control/poll latency, with one-second scrapes and a five-second alert hold. Actual Alertmanager suppression was observed during maintenance and no new firing delivery reached the receiver during that silence. The final application and scrape metrics were healthy. No external messaging integration or physical environmental monitoring is claimed.

Eight failed implementation runs were retained locally. They exposed Docker network-mode constraints, container sysctl handling, version-specific FRR options/capabilities/runtime ownership, sticky-directory log behavior, capture display/filter scope and stopped-container DNS behavior. Their records were not rewritten as successes. Earlier broad captures admitted host-bridge multicast; those raw runs are excluded from Git staging. Successful capture scope was narrowed and reviewed separately.

## Remaining requirements

1. Arkar personally runs and inspects the labs, records his actual contribution and answers the explain-back exercises.
2. A changed-fault challenge and a useful incident/shift-handover explanation are assessed with evidence.
3. Packet Tracer account, installation and switching exercise are executed if retaining that simulator component. No `.pkt` artifact exists yet. GNS3/EVE-NG and VM/systemd execution are not established.
4. Review the actual personal records and update the claim ledger before treating skills as candidate-demonstrated or publishing an employer-facing portfolio.

There is no physical hardware budget. Rack/stack, copper/fiber certification, transceiver handling, component replacement, RAID work and UPS/HVAC maintenance remain training gaps. Fictional work-order consistency checks are correctly labelled tabletop documentation.

## Navigation status

Engineering implementation and assistant verification: completed for the three Linux labs. Initial networking answers: reviewed with follow-up requirements. A separate local candidate-declared Lab 1 run passed 26 automated checks, with resources retained for practice. Candidate practical validation and simulator component: pending. Objective 1 overall: in progress. Objective 2 publication/review: authorized by the subsequent NEXT command. Objective 3 CV production: not activated. Live publication status is recorded separately in the private portfolio review; this engineering review does not certify candidate mastery. FINISH AND COMPLETE is not warranted.
