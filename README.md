# Personal infrastructure and networking laboratories — Arkar Htet Paing

I developed this personal laboratory project as part of my preparation for Junior Network Engineer and Junior Data Center Engineer positions in Singapore. It connects network commissioning, service recovery and monitoring with checking connectivity, reviewing failures, verifying recovery and documenting results.

## My completed practical work

I personally executed **Lab 1 in candidate mode and reviewed all 26 successful automated checks**. My work included reviewing VLAN connectivity, DHCP/DNS behavior, OSPF adjacency, firewall restrictions, routing failover and recovery, and saved packet captures. I examined the technical verification results and failure/recovery scenarios to understand how the working environment was validated.

The documented commissioning procedure configures the software topology and automates the listed faults and checks. My completed work is personal execution and review of that procedure. Manual diagnosis of an unfamiliar fault is a separate practice exercise.

My [personal run](evidence/runs/lab1-20261014T200305765964Z/metadata.json), [26-check result](evidence/runs/lab1-20261014T200305765964Z/checks.json), [command journal](evidence/runs/lab1-20261014T200305765964Z/commands.jsonl) and [packet evidence](evidence/runs/lab1-20261014T200305765964Z/captures/) record the actual execution. See [my contribution](docs/CONTRIBUTION.md) for the scope of this work.

## Laboratory portfolio

| Laboratory | Actual functionality | Verification and personal-practice status |
|---|---|---|
| [Network commissioning](labs/01-network-commissioning/README.md) | VLAN/DHCP/DNS, static and OSPF routing, access restrictions, controlled faults and alternate-path recovery | My personal run passed all 26 automated checks; manual changed-fault practice continues |
| [Linux service recovery](labs/02-service-recovery/README.md) | Configuration/startup failures, permissions, bounded ENOSPC, rollback and clean-target backup restore | 15 automated reference checks passed; my hands-on practice continues |
| [Monitoring operations](labs/03-monitoring-operations/README.md) | Prometheus/Alertmanager, service versus exporter faults, firing/resolved delivery and maintenance silence | 11 automated reference checks passed; my hands-on practice continues |

The [evidence index](evidence/INDEX.md) separates my personal network run from reference verification. The original network reference run repeats the same 26-check matrix; it does not add 26 different capabilities. Automated verification and personal troubleshooting competence are distinct findings.

## Reproduce and inspect

Use a Linux host with Python 3 and Docker Engine. Initial image construction requires Debian package-repository access. Package versions, source hashes and the tested image ID are preserved in the run records.

    git clone https://github.com/arkarhtetpaing23/singapore-infrastructure-operations-labs.git
    cd singapore-infrastructure-operations-labs
    python3 scripts/labctl.py build
    python3 scripts/labctl.py lab1 --actor candidate --keep

Use candidate mode when I personally initiate and observe the run. The keep option retains uniquely named resources for inspection. Follow the [practice guide](docs/CANDIDATE_PRACTICE.md) for commands and label-checked cleanup. Omit that option for automatic cleanup. Run lab2 or lab3 for the other environments; record the actual operator and scope when interpreting results.

Resources use internal Docker networks, memory/CPU/PID limits and ownership labels. The controller uses no privileged containers, host networking/PID namespace, published ports, socket mounts or host bind mounts. Network nodes use NET_ADMIN/NET_RAW; the three FRR routers additionally require SYS_ADMIN for the tested package. IP forwarding is container-scoped. Read the scripts before execution: Docker access is an administrative host capability.

## Technical review and scope

The [review guide](docs/PORTFOLIO_GUIDE.md), [claim ledger](docs/CLAIM_LEDGER.md) and [operations guide](docs/OPERATIONS.md) connect configurations, observations, fault recovery and handover practice. Original run metadata, source provenance and Git history are preserved. Dependency licenses and vendor references remain in place.

These are isolated software laboratories and simulated incidents. Packet Tracer practice is separately pending; no physical rack/cable work, commercial deployment or engineering employment is represented. Academic credentials and application documents are supplied privately.
