# Operational discipline used in these laboratories

All systems, customer descriptions, tickets, rack maps and asset identifiers are fictional. Test outputs and timestamps are actual when attributed to a run. Do not convert this lab into a claim of employment or customer operations.

## Before a change

Identify the exact asset, interface or service and its approved baseline. State the reason, expected impact, authorized scope, dependency, pre-check, change step, validation and rollback trigger. Record who actually performed the work. A lab accelerated timer does not establish a production maintenance window or SLA.

For lab1, a change should preserve the documented policy and be reversible through the container control path. For lab2, syntax validation should precede restart; keep a known-good recoverable configuration. For lab3, maintenance suppression must be bounded and followed by a health check before closure. Suppressing an alert does not repair a service.

## During an incident

Use a chronology containing observed UTC timestamps and references to real evidence. Separate facts from hypotheses. Establish impact from a client or independent probe, compare the recent change and baseline, and select a check that distinguishes competing causes. Make a supported correction rather than changing several unrelated settings at once. A junior escalates beyond approved scope and when the work-order identity, safety condition or cause remains unclear.

Document the fault, evidence, cause, correction and restoration checks. Record prevention that follows from the cause: VLAN/port-map review, address-plan validation, name/IP tests, syntax-before-restart, correct daemon directory ownership, config backups, write-path monitoring or an independently checked monitoring path. Do not label an assumed cause as proven.

## Recovery validation

Repeat the useful client action and policy checks after recovery. In lab1, confirm route/neighbor state and both allowed and denied access. In lab2, confirm restored bytes, permissions and both reads and writes. In lab3, confirm the application independently, monitoring metrics and resolved delivery. Keep failed runs and their errors; never overwrite them with an expected result.

## Handover

State current impact, restored/degraded components, evidence, recent changes, open risks, next action and responsible role. Explain any active silence, temporary workaround or remaining diagnosis. Give a concise factual customer update without an invented restoration promise.

## Candidate assessment

An automated run proves only its actual checks. Arkar's record must identify his own commands, observations, reasoning and assistance. A mentor should verify a packet-path explanation, a changed-fault diagnosis and a useful handover. Private notes and personal contact/academic records belong outside the public project.
