"""Actual Prometheus -> Alertmanager -> local webhook path and outage drills."""
import datetime as dt
import json
import time
from labcore import ROOT

def get(lab,url,ok=(0,)):
    return lab.ex('receiver',f"curl --noproxy '*' -fsS --max-time 2 '{url}'",ok=ok)

def metric(lab,query):
    p=lab.ex('receiver',f"curl --noproxy '*' -fsS --max-time 2 --get --data-urlencode 'query={query}' http://prom:9090/api/v1/query")
    obj=json.loads(p.stdout)
    rows=obj['data']['result']
    return float(rows[0]['value'][1]) if rows else None

def events(lab): return json.loads(get(lab,'http://receiver:8080/events').stdout)

def delivery(lab,name,status,after=0):
    for event in events(lab)[after:]:
        for alert in event['payload'].get('alerts',[]):
            if alert.get('labels',{}).get('alertname')==name and alert.get('status')==status:
                return event
    return None

def rule_state(lab,name,state):
    rows=json.loads(get(lab,'http://prom:9090/api/v1/alerts').stdout)['data']['alerts']
    return any(a['labels'].get('alertname')==name and a['state']==state for a in rows)

def run(lab):
    lab.network('monitoring')
    lab.node('svc',network='monitoring',cmd=['python3','-u','/lab/monitored_service.py'],memory='64m')
    lab.node('probe',network='monitoring',cmd=['python3','-u','/lab/probe_exporter.py'],memory='64m')
    lab.node('receiver',network='monitoring',cmd=['python3','-u','/lab/alert_receiver.py'],memory='64m')
    lab.node('prom',network='monitoring',memory='256m')
    lab.node('am',network='monitoring',memory='128m')
    lab.versions()
    for src,target in [('prometheus.yml','lab.yml'),('rules.yml','lab-rules.yml'),('rule-tests.yml','rule-tests.yml')]:
        lab.copy_in('prom',ROOT/'configs/lab3'/src,'/etc/prometheus/'+target)
    lab.copy_in('am',ROOT/'configs/lab3/alertmanager.yml','/etc/prometheus/alertmanager-lab.yml')
    unit=lab.ex('prom','promtool check config /etc/prometheus/lab.yml; promtool test rules /etc/prometheus/rule-tests.yml')
    lab.write('promtool-tests.txt',unit.stdout+unit.stderr)
    lab.check('Alert rule duration/recovery/missing-metric unit cases',unit.returncode==0,unit.stdout)
    lab.docker('exec','-d',lab.nodes['am'],'sh','-c','exec prometheus-alertmanager --config.file=/etc/prometheus/alertmanager-lab.yml --storage.path=/tmp/amdata --web.listen-address=:9093 --cluster.listen-address= >/tmp/alertmanager.log 2>&1')
    lab.docker('exec','-d',lab.nodes['prom'],'sh','-c','exec prometheus --config.file=/etc/prometheus/lab.yml --storage.tsdb.path=/tmp/promdata --storage.tsdb.retention.time=1h --web.listen-address=:9090 >/tmp/prometheus.log 2>&1')
    lab.wait('healthy real scrape and probe',lambda:metric(lab,'up{job="service-probe"}')==1 and metric(lab,'lab_probe_success{service="demo"}')==1)
    lab.check('Healthy exporter and actual application probe',True,{'up':1,'probe_success':1})
    lab.write('baseline-targets.json',json.loads(get(lab,'http://prom:9090/api/v1/targets').stdout))
    lab.write('baseline-alerts.json',json.loads(get(lab,'http://prom:9090/api/v1/alerts').stdout))
    before=len(events(lab)); fault_at=dt.datetime.now(dt.timezone.utc).isoformat(); start=time.monotonic()
    lab.docker('stop','-t','1',lab.nodes['svc'])
    lab.wait('application rule pending',lambda:rule_state(lab,'LabServiceUnavailable','pending'),seconds=8)
    pending=json.loads(get(lab,'http://prom:9090/api/v1/alerts').stdout)
    lab.write('service-alert-pending.json',pending)
    lab.check('Actual outage enters pending while exporter still scrapes',metric(lab,'up{job="service-probe"}')==1 and metric(lab,'lab_probe_success{service="demo"}')==0,pending)
    fired=lab.wait('service firing webhook delivery',lambda:delivery(lab,'LabServiceUnavailable','firing',before),seconds=25)
    detect=time.monotonic()-start
    lab.write('service-alert-firing.json',fired)
    lab.check('Prometheus service alert delivered through actual Alertmanager',True,fired)
    lab.docker('start',lab.nodes['svc'])
    resolved=lab.wait('service resolved webhook',lambda:delivery(lab,'LabServiceUnavailable','resolved',before),seconds=25)
    lab.write('service-alert-resolved.json',resolved)
    lab.check('Service recovery produces actual resolved delivery',metric(lab,'lab_probe_success{service="demo"}')==1,resolved)
    # Monitoring path outage: application is independently checked, not inferred from up.
    before=len(events(lab)); monitor_fault_at=dt.datetime.now(dt.timezone.utc).isoformat()
    lab.docker('stop','-t','1',lab.nodes['probe'])
    independent=json.loads(get(lab,'http://svc:8080/health').stdout)
    lab.wait('exporter scrape failure',lambda:metric(lab,'up{job="service-probe"}')==0)
    fired=lab.wait('exporter alert delivery',lambda:delivery(lab,'LabProbeExporterDown','firing',before),seconds=25)
    lab.write('monitor-only-fault.json',{'independent_service_response':independent,'delivery':fired,'alerts':json.loads(get(lab,'http://prom:9090/api/v1/alerts').stdout)})
    lab.check('Exporter failure distinguished from application outage',independent.get('healthy') is True and not rule_state(lab,'LabServiceUnavailable','firing'),fired)
    lab.docker('start',lab.nodes['probe'])
    resolved=lab.wait('exporter resolved delivery',lambda:delivery(lab,'LabProbeExporterDown','resolved',before),seconds=25)
    lab.check('Exporter recovery produces resolved delivery',metric(lab,'up{job="service-probe"}')==1,resolved)
    # Controlled maintenance uses a real bounded Alertmanager silence.
    before=len(events(lab))
    begin=dt.datetime.now(dt.timezone.utc)
    silence={'matchers':[{'name':'alertname','value':'LabServiceUnavailable','isRegex':False}],
             'startsAt':begin.isoformat(),'endsAt':(begin+dt.timedelta(seconds=90)).isoformat(),
             'createdBy':lab.actor,'comment':'Approved isolated-lab maintenance; restore and verify before closing'}
    lab.put('receiver','/tmp/silence.json',json.dumps(silence))
    result=lab.ex('receiver',"curl --noproxy '*' -fsS -H 'Content-Type: application/json' --data-binary @/tmp/silence.json http://am:9093/api/v2/silences")
    sid=json.loads(result.stdout)['silenceID']
    lab.docker('stop','-t','1',lab.nodes['svc'])
    lab.wait('silenced rule still fires',lambda:rule_state(lab,'LabServiceUnavailable','firing'),seconds=20)
    am=lab.wait('Alertmanager suppression applied',lambda: next((a for a in json.loads(get(lab,'http://am:9093/api/v2/alerts').stdout) if a['labels'].get('alertname')=='LabServiceUnavailable' and sid in a['status'].get('silencedBy',[])),None),seconds=15)
    time.sleep(2)
    lab.write('maintenance-silence.json',{'requested':silence,'silence_id':sid,'observed_alertmanager_status':am,'receiver_events_since_start':events(lab)[before:]})
    lab.check('Maintenance silence suppresses notification, not alert evaluation',delivery(lab,'LabServiceUnavailable','firing',before) is None,am)
    lab.docker('start',lab.nodes['svc'])
    lab.wait('maintenance application restored',lambda:metric(lab,'lab_probe_success{service="demo"}')==1 and not rule_state(lab,'LabServiceUnavailable','firing'))
    lab.ex('receiver',f"curl --noproxy '*' -fsS -X DELETE http://am:9093/api/v2/silence/{sid}")
    final=json.loads(get(lab,'http://prom:9090/api/v1/alerts').stdout)
    lab.check('Maintenance ends with service and monitoring healthy',metric(lab,'up{job="service-probe"}')==1 and metric(lab,'lab_probe_success{service="demo"}')==1 and not final['data']['alerts'],final)
    lab.write('final-alerts.json',final)
    lab.write('incident-observations.json',{'service_fault_utc':fault_at,'observed_firing_delivery_seconds':round(detect,3),'monitor_fault_utc':monitor_fault_at,'measurement_scope':'Actual lab receiver/poll observations with accelerated 1s scrape and 5s alert hold; not a production SLA','delivered_events':events(lab)})
    lab.copy_out('receiver','/tmp/deliveries.jsonl','webhook-deliveries.jsonl')
    lab.write('prometheus-log.txt',lab.ex('prom','cat /tmp/prometheus.log').stdout)
    lab.write('alertmanager-log.txt',lab.ex('am','cat /tmp/alertmanager.log').stdout)
    # Fictional physical-document workflow: an actual consistency check, not hardware testing.
    fixture=json.loads((ROOT/'configs/lab3/tabletop.json').read_text())
    occupied=set(); collisions=[]
    for asset in fixture['assets']:
        for u in range(asset['start_u'],asset['start_u']+asset['height_u']):
            if u in occupied or not 1<=u<=fixture['rack']['height_u']: collisions.append(u)
            occupied.add(u)
    approved=fixture['approved_cross_connect']; observed=fixture['observed_label_fixture']
    mismatches={k:{'approved':approved[k],'observed_fixture':observed[k]} for k in ['asset','port','panel','panel_port','media','optic'] if approved[k]!=observed[k]}
    lab.write('tabletop-review.json',{'classification':fixture['classification'],'rack_collisions':collisions,'endpoint_mismatches':mismatches,'decision':'Stop work and escalate endpoint conflict; do not patch SW02 against a SW01 work order','physical_testing_performed':False})
    lab.check('Fictional rack placement consistent and cross-connect endpoint conflict detected',not collisions and set(mismatches)=={'asset'},mismatches)
