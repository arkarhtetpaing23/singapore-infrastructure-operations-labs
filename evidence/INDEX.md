# Actual execution evidence

My personal Lab 1 run passed all 26 automated checks, and I confirmed executing and reviewing it. The reference runs below remain separately identified. All timestamps are actual UTC records.

## My personal Lab 1 commissioning run

Run: [lab1-20261014T200305765964Z](runs/lab1-20261014T200305765964Z/metadata.json).

[All 26 checks](runs/lab1-20261014T200305765964Z/checks.json), [command journal](runs/lab1-20261014T200305765964Z/commands.jsonl), [versions](runs/lab1-20261014T200305765964Z/versions.txt), [isolation](runs/lab1-20261014T200305765964Z/isolation.json), [retained resources](runs/lab1-20261014T200305765964Z/retained_resources.json), [VLAN capture](runs/lab1-20261014T200305765964Z/captures/vlan.pcap) and [OSPF capture](runs/lab1-20261014T200305765964Z/captures/ospf.pcap).

I personally executed this procedure and reviewed the network failure/recovery results. Configuration, fault injection and checks were automated. Resources were intentionally retained for practice at the end of the run; no cleanup record is claimed for it. The packet endpoint/DNS review found only laboratory addresses and the app.lab fixture. Manual unfamiliar-fault diagnosis remains separate.

This repeats the 26-check network matrix in the reference run below. There are 52 distinct runner checks across the three labs, with a separate personal repeat of the network matrix.

## Reference verification runs

| Lab | Run | Recorded checks | Status |
|---|---|---:|---|
| lab1 | [lab1-20261014T193910216722Z](runs/lab1-20261014T193910216722Z/metadata.json) | 26 | Passed; cleanup checked |
| lab2 | [lab2-20261014T194249743051Z](runs/lab2-20261014T194249743051Z/metadata.json) | 15 | Passed; cleanup checked |
| lab3 | [lab3-20261014T194415047830Z](runs/lab3-20261014T194415047830Z/metadata.json) | 11 | Passed; cleanup checked |

There are 52 recorded checks across these three runs, including runtime isolation checks. Counts describe the saved runner checks; they are not certifications or measures of candidate mastery.

## Inspect the evidence

### lab1

[Checks](runs/lab1-20261014T193910216722Z/checks.json), [command journal](runs/lab1-20261014T193910216722Z/commands.jsonl), [versions](runs/lab1-20261014T193910216722Z/versions.txt), [isolation](runs/lab1-20261014T193910216722Z/isolation.json), [cleanup](runs/lab1-20261014T193910216722Z/cleanup.json).

[VLAN capture](runs/lab1-20261014T193910216722Z/captures/vlan.pcap), [OSPF capture](runs/lab1-20261014T193910216722Z/captures/ospf.pcap), [VLAN 10 excerpt](runs/lab1-20261014T193910216722Z/captures/vlan10-excerpt.txt), [VLAN 20 excerpt](runs/lab1-20261014T193910216722Z/captures/vlan20-excerpt.txt), [DHCP lease](runs/lab1-20261014T193910216722Z/dhcp-lease-and-route.txt), [failover observation](runs/lab1-20261014T193910216722Z/failover.json).

### lab2

[Checks](runs/lab2-20261014T194249743051Z/checks.json), [command journal](runs/lab2-20261014T194249743051Z/commands.jsonl), [versions](runs/lab2-20261014T194249743051Z/versions.txt), [isolation](runs/lab2-20261014T194249743051Z/isolation.json), [cleanup](runs/lab2-20261014T194249743051Z/cleanup.json).

[Startup fault](runs/lab2-20261014T194249743051Z/restart-fault.json), [permission fault](runs/lab2-20261014T194249743051Z/permission-fault.json), [actual ENOSPC response](runs/lab2-20261014T194249743051Z/storage-fault-response.json), [backup manifest](runs/lab2-20261014T194249743051Z/backup/manifest.json), [restore](runs/lab2-20261014T194249743051Z/restore.json).

### lab3

[Checks](runs/lab3-20261014T194415047830Z/checks.json), [command journal](runs/lab3-20261014T194415047830Z/commands.jsonl), [versions](runs/lab3-20261014T194415047830Z/versions.txt), [isolation](runs/lab3-20261014T194415047830Z/isolation.json), [cleanup](runs/lab3-20261014T194415047830Z/cleanup.json).

[Rule-unit tests](runs/lab3-20261014T194415047830Z/promtool-tests.txt), [pending alert](runs/lab3-20261014T194415047830Z/service-alert-pending.json), [firing delivery](runs/lab3-20261014T194415047830Z/service-alert-firing.json), [resolved delivery](runs/lab3-20261014T194415047830Z/service-alert-resolved.json), [monitor-only failure](runs/lab3-20261014T194415047830Z/monitor-only-fault.json), [silence](runs/lab3-20261014T194415047830Z/maintenance-silence.json), [chronology/deliveries](runs/lab3-20261014T194415047830Z/incident-observations.json), [fictional work-order review](runs/lab3-20261014T194415047830Z/tabletop-review.json).

## Preserved failed implementations

The failures below are real development runs. Their raw records remain local and are not staged for publication. Successful results were not substituted into their original records.

| Run | Failure area | Checks completed before failure |
|---|---|---:|
| `lab1-20261014T192501112860Z` | Docker network-mode restriction | 0 |
| `lab1-20261014T192539198172Z` | Read-only runtime sysctl | 0 |
| `lab1-20261014T192855311917Z` | Unsupported daemon flag | 8 |
| `lab1-20261014T193028997458Z` | FRR startup capability requirement | 8 |
| `lab1-20261014T193121227440Z` | Runtime-directory ownership | 8 |
| `lab1-20261014T193345715217Z` | Sticky-directory log reopening | 16 |
| `lab1-20261014T193503155165Z` | Capture display/filter verification | 24 |
| `lab2-20261014T194122887998Z` | Stopped container Docker DNS behavior | 4 |

Earlier broad captures admitted multicast from host-created Docker bridge interfaces. They remain private. Successful captures were scoped more narrowly and independently reviewed.

See [contribution boundaries](../docs/CONTRIBUTION.md) and [candidate practice](../docs/CANDIDATE_PRACTICE.md). No credential images, private keys or application CVs belong in this evidence tree.
