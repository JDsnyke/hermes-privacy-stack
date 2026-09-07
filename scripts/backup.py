#!/usr/bin/env python3
"""Create a privacy-safe backup bundle of authored config and print Hindsight logical export commands.

This intentionally does not copy live Hindsight/Postgres files.
"""
import argparse, os, tarfile, time
from pathlib import Path
p=argparse.ArgumentParser(); p.add_argument('--output',default='backups'); p.add_argument('--bank',action='append',default=[]); a=p.parse_args()
h=Path(os.environ.get('HERMES_HOME',Path.home()/'.hermes'))
out=Path(a.output); out.mkdir(parents=True,exist_ok=True); stamp=time.strftime('%Y%m%d-%H%M%S'); dest=out/f'hermes-config-{stamp}.tar.gz'
allow=['config.yaml','SOUL.md','AGENTS.md','skills','cron','scripts','hindsight/config.json']
with tarfile.open(dest,'w:gz') as tf:
    for rel in allow:
        q=h/rel
        if q.exists(): tf.add(q,arcname=rel)
print(f'Created {dest}')
if a.bank:
    print('\nLogical Hindsight bank exports should be made on the Hindsight server:')
    for bank in a.bank: print(f"  hindsight-admin export-bank --bank {bank!r} --output {bank}-{stamp}.zip")
    print('Encrypt those archives before cloud upload (age/restic/rclone crypt).')
