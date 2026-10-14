# Singapore infrastructure operations laboratories

AI-assisted engineering practice for Arkar Htet Paing's junior data center and network career preparation. These are isolated software laboratories. Current candidate personal validation is pending. No production employment, physical installation, certification or unaided authorship is claimed.

The three executable Linux laboratories have passed assistant-run verification: 26 network checks, 15 service-recovery checks and 11 monitoring/operations checks. See the [evidence index](evidence/INDEX.md) and actual run records. Candidate personal validation and Packet Tracer execution remain pending. Publication has not yet been performed.

The three projects are network commissioning/fault isolation, Linux service recovery, and monitoring/incident handover. Packet Tracer switching practice is a separate candidate exercise requiring an official Cisco account/installation. No `.pkt` file or simulator result is fabricated.

| Project | Practical evidence | Read next |
|---|---|---|
| [Network commissioning](labs/01-network-commissioning/README.md) | Actual VLAN packets, DHCP/DNS, access policy, OSPF faults and alternate-path recovery | Scenario, topology and saved CLI/packet evidence |
| [Service recovery](labs/02-service-recovery/README.md) | Configuration/startup failure, permissions, ENOSPC and clean-target restore | Backup manifest, actual client responses and recovery checks |
| [Monitoring operations](labs/03-monitoring-operations/README.md) | Prometheus/Alertmanager firing/resolved deliveries, exporter failure, silence and fictional work-order review | Actual incident chronology and local delivery journal |

Start personal development with the [practice guide](docs/CANDIDATE_PRACTICE.md). Read [contribution boundaries](docs/CONTRIBUTION.md), [operations discipline](docs/OPERATIONS.md), [verification review](docs/OBJECTIVE_1_REVIEW.md) and [Packet Tracer exercise](docs/PACKET_TRACER_EXERCISE.md). These projects support learning; they do not establish professional employment, physical hardware competence or unaided candidate mastery.

## Execution scope

`scripts/labctl.py` builds one Debian-based lab image and creates uniquely named, labelled Docker resources. Links use internal Docker networks. The runner does not use privileged containers, host networking/PID namespaces, published ports, Docker-socket mounts, or host bind mounts. NET_ADMIN is granted only to network-lab nodes. The installed FRR 8.4 Zebra package requires SYS_ADMIN at startup; that added capability is restricted to the three disposable lab1 routers. Container-scoped IP forwarding is supplied at creation. Cleanup verifies the project/run labels before removing resources. Memory, CPU and PID limits apply. Docker remains an administrative host capability; inspect the scripts before using it. This is an authorized learning environment, not a hardened sandbox for hostile code.

```sh
python3 scripts/labctl.py build
python3 scripts/labctl.py lab1 --actor assistant
python3 scripts/labctl.py lab2 --actor assistant
python3 scripts/labctl.py lab3 --actor assistant
```

Use `--actor candidate` only when the candidate actually initiates and observes the run. That option is a record of the declared operator, not authentication or proof of understanding. `--keep` retains that run for manual practice; resource names are saved with its evidence. Candidate explain-back and changed-fault practice are separate requirements.
