#!/usr/bin/env python3
"""Small dependency-free CI guard. Not a replacement for GitHub secret scanning."""
from pathlib import Path
import re, sys
ROOT=Path(__file__).resolve().parents[1]
FORBIDDEN_NAMES={'auth.json','.env','rclone.conf','state.db','hermes_state.db','response_store.db'}
PATTERNS=[
 ('private-key',re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----')),
 ('github-pat',re.compile(r'gh[pousr]_[A-Za-z0-9]{30,}')),
 ('openai-key',re.compile(r'sk-[A-Za-z0-9_-]{20,}')),
 ('google-api',re.compile(r'AIza[0-9A-Za-z_-]{30,}')),
 ('aws-key',re.compile(r'AKIA[0-9A-Z]{16}')),
]
skip={'.git','.venv','node_modules'}; bad=[]
for p in ROOT.rglob('*'):
    if not p.is_file() or any(x in p.parts for x in skip): continue
    if p.name in FORBIDDEN_NAMES: bad.append(f'forbidden runtime file: {p.relative_to(ROOT)}'); continue
    try: text=p.read_text(errors='ignore')
    except Exception: continue
    for name,rx in PATTERNS:
        if rx.search(text): bad.append(f'{name}: {p.relative_to(ROOT)}')
if bad:
    print('\n'.join(bad)); sys.exit(1)
print('secret hygiene checks passed')
