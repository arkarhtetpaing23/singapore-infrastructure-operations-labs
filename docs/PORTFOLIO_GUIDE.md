# Technical review guide

This repository contains three software operations laboratories for Arkar Htet Paing's preparation for junior data center and network roles in Singapore. It gives a reviewer a path from the scenario to actual configuration, failure evidence and recovery checks.

## Review the work

1. Open a laboratory README for its scenario, topology, operational fault and limits.
2. Follow the [evidence index](../evidence/INDEX.md) to that run's `metadata.json` and `checks.json`.
3. Inspect `commands.jsonl` for the actual command, return code and output behind a check. A success label alone is insufficient.
4. Compare the relevant source hashes and image ID with the supplied runner and recorded package versions.
5. Inspect recovery evidence and the final traffic/service result. Cleanup records establish what the assistant removed after that run; they are not current host-inventory statements.

## Job relevance and useful evidence

| Laboratory | Junior data center relevance | Junior network relevance | Evidence to inspect |
|---|---|---|---|
| [Network commissioning](../labs/01-network-commissioning/README.md) | Connectivity verification, segment awareness, access policy and escalation evidence | VLANs, DHCP/DNS, IPv4 routes, OSPF and fault isolation | Tagged PCAPs, leases, router configuration, kernel route, firewall counter and useful HTTP after failover |
| [Service recovery](../labs/02-service-recovery/README.md) | Availability checks, log review, rollback and restoration | Distinguishing an application fault from connectivity or name resolution | Startup error, direct-IP client result, permissions log, real ENOSPC response and separate-target restore hashes |
| [Monitoring operations](../labs/03-monitoring-operations/README.md) | Alert triage, maintenance suppression, incident chronology and handover preparation | Distinguishing monitoring-path failure from service failure | Real probe/scrape metrics, firing/resolved webhook delivery, silence observations and final healthy state |

The role mapping is a professional recommendation, not a claim that every employer asks for every technology. Software exercises cannot substitute for physical installation, fiber handling, component replacement or electrical/mechanical facilities competence.

## Evidence and candidate contribution

The selected published runs contain 52 recorded automated checks across three laboratories. All three were executed by the assistant, and raw records retain their real UTC timestamps. There are no fabricated screenshots, production incidents, historical Git activity or candidate-authored commits.

Arkar supplied the preparation requirements and answered an initial networking explain-back. A later local run declared him as operator and passed the Lab 1 automation; that is separate from manual competence. Practical diagnosis and handover are still being assessed. See the [contribution record](CONTRIBUTION.md) and [claim ledger](CLAIM_LEDGER.md) before interpreting a technology in this repository as a candidate skill.

## Reproduction and boundaries

The root [README](../README.md) and [practice guide](CANDIDATE_PRACTICE.md) explain build, execution, inspection and cleanup. Resources have per-run names and ownership labels. The image uses a pinned Debian base digest; package versions are recorded because a future package download can change the resulting image.

The implementation uses Linux bridges and FRRouting, not Cisco IOS. The Packet Tracer worksheet has not been executed. SSH checks establish TCP/banner access, not authenticated administration. Monitoring delivers to a local HTTP receiver. Work-order checks use fictional fixtures. These boundaries are part of the technical evidence.
