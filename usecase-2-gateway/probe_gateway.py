#!/usr/bin/env python3
import requests, json, sys
from pathlib import Path
requests.packages.urllib3.disable_warnings()
base='https://demo-azure-gateway-u91fgurm4n.gateway.bedrock-agentcore.us-east-1.amazonaws.com'
paths=[
    '/mcp','/mcp/','/invoke','/invoke-model','/invokeModel','/v1/invoke','/v1/models/anthropic.claude-3-haiku-20240307-v1:0/invoke','/v1/chat/completions','/converse','/converse/']
headers={'Content-Type':'application/json','Accept':'application/json'}
body_candidates=[
    {'modelId':'anthropic.claude-3-haiku-20240307-v1:0','body':'hello'},
    {'modelId':'anthropic.claude-3-haiku-20240307-v1:0','input':{'text':'hello'}},
    {'system':[{'text':'hi'}],'messages':[{'role':'user','content':[{'text':'hello'}]}]},
    {'modelId':'anthropic.claude-3-haiku-20240307-v1:0','messages':[{'role':'user','content':[{'text':'hello'}]}],'toolConfig':{'tools':[]}},
]

out = []
for p in paths:
    url = base + p
    try:
        r = requests.options(url, timeout=10, verify=False)
        out.append({'url':url,'method':'OPTIONS','status':r.status_code,'ctype':r.headers.get('content-type'),'body':r.text[:200]})
    except Exception as e:
        out.append({'url':url,'method':'OPTIONS','error':str(e)})
    try:
        r = requests.get(url, timeout=10, verify=False)
        out.append({'url':url,'method':'GET','status':r.status_code,'ctype':r.headers.get('content-type'),'body':r.text[:200]})
    except Exception as e:
        out.append({'url':url,'method':'GET','error':str(e)})
    for i,body in enumerate(body_candidates,1):
        try:
            r = requests.post(url, json=body, headers=headers, timeout=15, verify=False)
            out.append({'url':url,'method':f'POST#{i}','status':r.status_code,'ctype':r.headers.get('content-type'),'body':r.text[:1000]})
        except Exception as e:
            out.append({'url':url,'method':f'POST#{i}','error':str(e)})

p = Path('/tmp/gateway_probe.json')
p.write_text(json.dumps(out, indent=2))
print('Wrote /tmp/gateway_probe.json')
print(json.dumps(out[:10], indent=2))
