# Personal practice and interview evidence

Current status: candidate execution and understanding have not been verified for these new projects. Assistant runs are useful implementation evidence, not evidence that Arkar personally operated the environment.

## Start with one project

First read the [network foundations lesson](FIRST_PRACTICE_LESSON.md). It explains the implemented packet path, subnet/VLAN/DHCP/DNS/OSPF relationships and what each diagnostic command can prove.

Open a terminal in this project folder. Inspect `Dockerfile`, `scripts/labctl.py`, `scripts/labcore.py` and the relevant lab script. A Docker-capable account is required. The normal run automatically removes its own lab resources and preserves evidence. A retained run stays available for the manual commands below.

```sh
python3 scripts/labctl.py lab1 --actor candidate --keep
```

Record the printed `EVIDENCE` directory. Substitute that actual relative directory for `RUN_DIR` in the examples. Do not use an assistant run that was already cleaned. The actor switch records your declaration; it does not prove identity or mastery. No score or competency is automatically awarded for launching the script.

```sh
python3 scripts/practice.py list --run RUN_DIR
python3 scripts/practice.py exec --run RUN_DIR --node c20 --command 'ip -br addr; ip route; dig +short app.lab'
python3 scripts/practice.py exec --run RUN_DIR --node sw2 --command 'bridge vlan show'
python3 scripts/practice.py exec --run RUN_DIR --node r1 --command 'vtysh -c "show ip ospf neighbor" -c "show ip route"'
python3 scripts/practice.py exec --run RUN_DIR --node r1 --command 'nft list ruleset'
```

Each manual command and actual output are retained in `manual-practice.jsonl`. Commands execute inside the chosen lab container, after ownership checks. Keep personal notes separately if they contain private information. Never add real account passwords or production configurations to this environment.

## Lab 1 — explain before changing

1. Calculate the network address, usable range and broadcast address for 10.20.0.50/24 and the /30 router links. Explain why 10.20.0.254 is inside the client subnet but is not the configured router.
2. Trace a client request to `app.lab`: DHCP lease/options, DNS answer, VLAN 20, r1 routing/firewall, OSPF route to r2, service response and return path.
3. Explain the different proof provided by `show ip ospf neighbor`, `ip route get 10.30.0.10`, a captured OSPF hello and a successful HTTP request.
4. Explain why the management host reaches the SSH TCP listener while the client host is rejected. The automated test does not prove an authenticated SSH login.
5. Inspect `captures/vlan.pcap` and `captures/ospf.pcap` from your actual run using Wireshark or `tcpdump -nn -r FILE`. Identify VLAN IDs and actual protocol messages. Describe capture-interface scope and avoid calling a synthetic Packet Tracer PDU a real Linux packet capture.

Guided fault: remove VLAN 20 from only sw2's trunk, predict the affected segment, collect observations, correct it and repeat the application/policy tests.

```sh
python3 scripts/practice.py exec --run RUN_DIR --node sw2 --command 'bridge vlan del dev p-trunk vid 20'
python3 scripts/practice.py exec --run RUN_DIR --node c20 --command 'ping -c 2 -W 1 10.20.0.1'
python3 scripts/practice.py exec --run RUN_DIR --node m10 --command 'ping -c 2 -W 1 10.10.0.1'
python3 scripts/practice.py exec --run RUN_DIR --node sw2 --command 'bridge vlan show'
python3 scripts/practice.py exec --run RUN_DIR --node sw2 --command 'bridge vlan add dev p-trunk vid 20'
python3 scripts/practice.py exec --run RUN_DIR --node c20 --command 'curl --noproxy "*" -fsS http://app.lab/'
```

Changed-fault challenge: another authorized person selects a wrong route, an access-port VLAN or an OSPF area fault inside this retained lab without giving you the correction command. State the observed impact, list competing causes, choose a discriminating check, repair the evidenced fault and show restoration. The mentor must record which fault was used and the assistance required; do not claim unaided diagnosis from the guided example alone.

## Lab 2 — change and recovery

Run `python3 scripts/labctl.py lab2 --actor candidate --keep`. Inspect the actual backup manifest, nginx syntax failure, restart failure, permission denial and HTTP 507 response. Explain why a bad config on disk can coexist with a still-running healthy worker until restart, and why a frontend health response alone can miss a failed write path.

Manually inspect `nginx -t`, `ss -lntp`, `/var/log/nginx/error.log`, file mode and both `df -h /srv/pressure` and `df -i /srv/pressure` using `practice.py`. The full-filesystem test is confined to an 8 MiB tmpfs. Do not fill the host disk.

Restore the recorded `backup/service-backup.tar` only in a retained lab node after inspecting its member list. Compare expected configuration/data hashes, permissions and actual client requests. Explain which data is excluded: the pressure journal is ephemeral and not restored. This is container startup/persistence, not systemd or physical-server boot evidence. Discuss what additional data and retention a production backup design would require.

Changed-fault challenge: a different file permission or invalid nginx directive, followed by a recovery to the approved baseline. State the rollback trigger before making the change.

## Lab 3 — incident and handover

Run `python3 scripts/labctl.py lab3 --actor candidate --keep`. Review the actual pending/firing/resolved observations and webhook journal. Explain the chain: real HTTP probe -> exporter metric -> Prometheus rule -> Alertmanager routing/silence -> local receiver.

Explain `up` versus application probe success. Demonstrate the HTTP service independently when the exporter fails. Explain why missing metrics are not proof that the service is healthy. Distinguish notification suppression from alert evaluation. One-second scrape and five-second holds are accelerated lab settings, not production recommendations.

Write your own incident report from your run: impact, timestamps, facts, hypotheses, diagnostic checks, cause, corrective action, restoration checks and prevention. Give a 60–90 second handover stating open issues, next action and owner/escalation. Review the fictional work order and explain the SW01/SW02 conflict; do not claim physical cross-connect work.

## Record what you actually did

Create a Markdown record with your real run ID, date/time, commands performed, faults diagnosed, assistance used, corrections, useful output references, remaining questions and explain-back answers. Do not fill this record with invented past-tense outcomes. The assessor records whether the explanation is accurate and whether a changed fault was resolved, with evidence. A request to run the lab and an automated pass do not establish those facts.

## End the session

```sh
python3 scripts/practice.py cleanup --run RUN_DIR
```

This deletes only labelled containers/networks of that retained run. Source files, original documents and saved evidence remain. Repeat a lab only to address a learning need, a change or a failure; do not manufacture GitHub activity.
