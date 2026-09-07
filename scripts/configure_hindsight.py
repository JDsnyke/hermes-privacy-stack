#!/usr/bin/env python3
import argparse, json, os
from pathlib import Path

def home():
    if os.name=='nt': return Path(os.environ.get('LOCALAPPDATA',Path.home()))/'hermes'
    return Path(os.environ.get('HERMES_HOME',Path.home()/'.hermes'))

p=argparse.ArgumentParser(); p.add_argument('--url',default='http://127.0.0.1:8888'); p.add_argument('--bank-template',default='hermes-{profile}'); a=p.parse_args()
h=home(); d=h/'hindsight'; d.mkdir(parents=True,exist_ok=True)
cfg={'mode':'local_external','api_url':a.url.rstrip('/'),'bank_id':'hermes','bank_id_template':a.bank_template,'memory_mode':'hybrid','auto_retain':True,'retain_async':True,'retain_source':'hermes'}
(d/'config.json').write_text(json.dumps(cfg,indent=2)+'\n')
print(d/'config.json')
