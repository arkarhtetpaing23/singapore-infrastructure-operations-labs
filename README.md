# Infrastructure operations laboratories — Arkar Htet Paing

Software laboratories supporting preparation for Junior Data Center Engineer and Junior Network Engineer roles in Singapore. The projects connect networking, service recovery and monitoring to practical operations: commissioning a service, isolating faults, restoring availability and documenting evidence.

The three executable Linux laboratories have passed assistant-run verification: **26 network checks, 15 service-recovery checks and 11 monitoring/operations checks**. The [evidence index](evidence/INDEX.md) links the actual commands, results, configurations and captures. These counts describe automated laboratory checks; they do not establish candidate mastery.

This portfolio was developed with AI assistance. Arkar's initial networking explain-back has been reviewed; manual diagnosis, handover and the remaining personal practice are still in progress. Packet Tracer execution is pending. See [contribution boundaries](docs/CONTRIBUTION.md) and the [claim ledger](docs/CLAIM_LEDGER.md) for the distinction between implemented capabilities and demonstrated candidate skills.

The three projects are network commissioning/fault isolation, Linux service recovery, and monitoring/incident handover. Packet Tracer switching practice is a separate candidate exercise requiring an official Cisco account/installation. No `.pkt` file or simulator result is fabricated.

| Project | Practical evidence | Read next |
|---|---|---|
| [Network commissioning](labs/01-network-commissioning/README.md) | Actual VLAN packets, DHCP/DNS, access policy, OSPF faults and alternate-path recovery | Scenario, topology and saved CLI/packet evidence |
| [Service recovery](labs/02-service-recovery/README.md) | Configuration/startup failure, permissions, ENOSPC and clean-target restore | Backup manifest, actual client responses and recovery checks |
| [Monitoring operations](labs/03-monitoring-operations/README.md) | Prometheus/Alertmanager firing/resolved deliveries, exporter failure, silence and fictional work-order review | Actual incident chronology and local delivery journal |

For a quick technical review, start with the [portfolio guide](docs/PORTFOLIO_GUIDE.md). For personal development, use the [network foundations lesson](docs/FIRST_PRACTICE_LESSON.md) and [practice guide](docs/CANDIDATE_PRACTICE.md). The [operations guide](docs/OPERATIONS.md) explains change, rollback, escalation and handover. The [engineering review](docs/OBJECTIVE_1_REVIEW.md) records verified results and remaining work.

## Reproduce a laboratory

Use a Linux host with Python 3 and Docker Engine. Initial image construction needs access to Debian package repositories. The lab nodes use Debian Bookworm; exact tested package versions and image ID are preserved in each evidence run. The host controller currently runs on Python 3.13.14. Future package resolution can differ and should be verified.

```sh
git clone https://github.com/arkarhtetpaing23/singapore-infrastructure-operations-labs.git
cd singapore-infrastructure-operations-labs
python3 scripts/labctl.py build
python3 scripts/labctl.py lab1 --actor candidate --keep
```

Use `--actor candidate` only when Arkar personally initiates and observes a run. The actor field is a declaration, not identity authentication. `--keep` retains that run for inspection; follow the [practice guide](docs/CANDIDATE_PRACTICE.md) for commands and label-checked cleanup. Omit `--keep` for automatic cleanup. Generated runs remain local by default until their evidence and claims have been reviewed for publication.

Run `lab2` or `lab3` with the same controller for service recovery and monitoring. The [evidence index](evidence/INDEX.md) contains the selected verification runs. A successful run requires its recorded checks and final status; cleanup status must also be checked unless resources were intentionally retained.

## Execution scope

`scripts/labctl.py` builds one Debian-based lab image and creates uniquely named, labelled Docker resources. Links use internal Docker networks. The runner does not use privileged containers, host networking/PID namespaces, published ports, Docker-socket mounts, or host bind mounts. NET_ADMIN is granted only to network-lab nodes. The installed FRR 8.4 Zebra package requires SYS_ADMIN at startup; that added capability is restricted to the three disposable lab1 routers. Container-scoped IP forwarding is supplied at creation. Cleanup verifies the project/run labels before removing resources. Memory, CPU and PID limits apply. Docker remains an administrative host capability; inspect the scripts before using it. This is an authorized learning environment, not a hardened sandbox for hostile code.

```sh
python3 scripts/labctl.py build
python3 scripts/labctl.py lab1 --actor assistant
python3 scripts/labctl.py lab2 --actor assistant
python3 scripts/labctl.py lab3 --actor assistant
```

## Scope and supporting material

These are isolated software exercises, with simulated operational incidents. They do not demonstrate production employment, physical rack/cable work, authenticated SSH administration or certification. The [Packet Tracer exercise](docs/PACKET_TRACER_EXERCISE.md) is a separate, unexecuted learning component; no `.pkt` artifact is claimed. Academic certificates, transcripts, contact details and application documents are kept outside this repository.

Platform references are listed in each laboratory README. Dependency packages retain their own licenses. No proprietary network-appliance image or copied third-party portfolio is supplied.
