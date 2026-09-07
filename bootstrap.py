#!/usr/bin/env python3
"""Privacy-first cross-platform bootstrap for Hermes Privacy Stack.

The bootstrap intentionally delegates Hermes authentication/model selection to
Hermes itself. It never asks for or stores Codex OAuth tokens.
"""
from __future__ import annotations
import argparse, json, os, platform, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
IS_WINDOWS = os.name == "nt"
HERMES_HOME = Path(os.environ.get("HERMES_HOME") or (Path(os.environ.get("LOCALAPPDATA", Path.home())) / "hermes" if IS_WINDOWS else Path.home()/".hermes"))
STATE = Path.home()/".hermes-privacy-stack-state"


def run(cmd, check=True, shell=False):
    print("+", cmd if isinstance(cmd,str) else " ".join(map(str,cmd)))
    return subprocess.run(cmd, check=check, shell=shell)


def command(name): return shutil.which(name)

def yesno(prompt, default=True):
    suffix = " [Y/n] " if default else " [y/N] "
    ans=input(prompt+suffix).strip().lower()
    return default if not ans else ans in {"y","yes"}

def choose(prompt, options, default):
    print(f"\n{prompt}")
    for i,x in enumerate(options,1): print(f"  {i}. {x}")
    raw=input(f"Choice [{default}]: ").strip()
    if not raw: return options[default-1]
    try: return options[int(raw)-1]
    except Exception: raise SystemExit("Invalid choice")

def install_hermes():
    if command("hermes"):
        print("✓ Hermes already installed")
        return
    if not yesno("Hermes is not installed. Install it using the official Nous Research installer?", True):
        print("Skipping Hermes installation.")
        return
    if IS_WINDOWS:
        ps = command("pwsh") or command("powershell")
        if not ps: raise SystemExit("PowerShell is required to install Hermes on Windows.")
        run([ps,"-NoProfile","-Command","iex (irm https://hermes-agent.nousresearch.com/install.ps1)"])
    else:
        run(["bash","-lc","curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash"])

def write_env_var(path:Path,key:str,value:str):
    path.parent.mkdir(parents=True,exist_ok=True)
    lines=path.read_text().splitlines() if path.exists() else []
    out=[]; found=False
    for line in lines:
        if line.startswith(key+"="):
            out.append(f"{key}={value}"); found=True
        else: out.append(line)
    if not found: out.append(f"{key}={value}")
    path.write_text("\n".join(out).rstrip()+"\n")
    if not IS_WINDOWS:
        try: os.chmod(path,0o600)
        except OSError: pass

def configure_hindsight(role:str, host:str|None):
    cfgdir=HERMES_HOME/"hindsight"; cfgdir.mkdir(parents=True,exist_ok=True)
    api = host.rstrip("/") if host else "http://127.0.0.1:8888"
    cfg={
      "mode":"local_external",
      "api_url":api,
      "bank_id":"hermes",
      "bank_id_template":"hermes-{profile}",
      "memory_mode":"hybrid",
      "auto_retain":True,
      "retain_async":True,
      "retain_source":"hermes",
      "retain_indicator":True
    }
    (cfgdir/"config.json").write_text(json.dumps(cfg,indent=2)+"\n")
    write_env_var(HERMES_HOME/".env","HINDSIGHT_API_URL",api)
    if command("hermes"):
        run(["hermes","config","set","memory.provider","hindsight"],check=False)
    print(f"✓ Hindsight configured at {api}")

def start_stack(preset:str, role:str):
    if role == "client":
        print("Client role: no local service stack started.")
        return
    if not command("docker"):
        print("! Docker not found. Hermes can still run; install Docker Desktop/Engine then run:")
        print(f"  docker compose -f {ROOT/'stack/compose.yml'} --profile core up -d")
        return
    profiles=["core"]
    if preset in {"balanced","developer"} and yesno("Start optional Activepieces integration service?", False): profiles.append("automation")
    if preset in {"balanced","developer"} and yesno("Start optional OpenViking knowledge service?", False): profiles.append("knowledge")
    args=["docker","compose","-f",str(ROOT/"stack/compose.yml")]
    for p in profiles: args += ["--profile",p]
    args += ["up","-d"]
    run(args)
    print("✓ Local services started")

def seed_templates():
    HERMES_HOME.mkdir(parents=True,exist_ok=True)
    soul=HERMES_HOME/"SOUL.md"
    if not soul.exists() and yesno("Install the privacy-first starter SOUL.md?", True):
        soul.write_text((ROOT/"profile/SOUL.md").read_text())
        print("✓ SOUL.md installed")
    user=HERMES_HOME/"USER.md"
    if not user.exists():
        user.write_text("# User\n\nThis file is intentionally local and is never sourced from Git. Add only information you want Hermes to retain as durable profile context.\n")
        if not IS_WINDOWS:
            try: os.chmod(user,0o600)
            except OSError: pass
        print("✓ Local USER.md created")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--preset",choices=["strict","balanced","developer","minimal"])
    ap.add_argument("--role",choices=["local","server","client"])
    ap.add_argument("--hindsight-url")
    ap.add_argument("--non-interactive",action="store_true")
    a=ap.parse_args()
    if sys.version_info < (3,10): raise SystemExit("Python 3.10+ required")
    print("\nHermes Privacy Stack — local first, secrets never in Git\n")
    preset=a.preset or ("balanced" if a.non_interactive else choose("Privacy preset",["strict","balanced","developer","minimal"],2))
    role=a.role or ("local" if a.non_interactive else choose("Machine role",["local","server","client"],1))
    install_hermes()
    seed_templates()
    remote=a.hindsight_url
    if role=="client" and not remote:
        if a.non_interactive: raise SystemExit("--hindsight-url is required for client role")
        remote=input("Hindsight private URL (e.g. http://100.x.y.z:8888): ").strip()
    start_stack(preset,role)
    configure_hindsight(role,remote)
    write_env_var(HERMES_HOME/".env","SEARXNG_URL","http://127.0.0.1:8088" if role!="client" else os.environ.get("SEARXNG_URL",""))
    STATE.mkdir(exist_ok=True)
    (STATE/"install.json").write_text(json.dumps({"preset":preset,"role":role,"platform":platform.platform()},indent=2)+"\n")
    print("\nCore bootstrap complete.")
    if command("hermes"):
        print("\nNext: choose OpenAI Codex/ChatGPT OAuth in Hermes' official model wizard:")
        print("  hermes model")
        if not a.non_interactive and yesno("Open Hermes model setup now?", True): run(["hermes","model"],check=False)
    print(f"\nRun diagnostics anytime: python {ROOT/'scripts/doctor.py'}")
    print("Review ROADMAP.md before enabling optional high-authority MCPs.")

if __name__ == '__main__': main()
