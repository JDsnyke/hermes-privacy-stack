#!/usr/bin/env python3
import subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1]
print('Updating repository with fast-forward only...')
subprocess.run(['git','-C',str(root),'pull','--ff-only'],check=True)
print('Repository updated. Review ROADMAP.md and run scripts/doctor.py before changing services.')
