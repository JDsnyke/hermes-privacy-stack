#!/usr/bin/env python3
from __future__ import annotations
import json, shutil, sys, urllib.request

checks=[]
def add(name, ok, detail): checks.append({'name':name,'ok':bool(ok),'detail':detail})
def http(name,url):
    try:
        with urllib.request.urlopen(url,timeout=3) as r: add(name,200 <= r.status < 500,f"HTTP {r.status} {url}")
    except Exception as e: add(name,False,f"{url}: {e}")

def main():
    as_json='--json' in sys.argv
    for cmd in ['git','python','hermes','docker']:
        p=shutil.which(cmd); add(cmd,bool(p),p or 'not found')
    http('Hindsight','http://127.0.0.1:8888/health')
    http('SearXNG','http://127.0.0.1:8088/')
    http('Docling','http://127.0.0.1:5001/docs')
    http('OpenViking','http://127.0.0.1:1933/health')
    if as_json: print(json.dumps(checks,indent=2))
    else:
        for x in checks: print(('✓' if x['ok'] else '✗'),f"{x['name']}: {x['detail']}")
        print(f"\n{sum(x['ok'] for x in checks)}/{len(checks)} checks passed")
    return 0 if all(x['ok'] or x['name'] in {'Docling','OpenViking'} for x in checks) else 1
if __name__=='__main__': raise SystemExit(main())
