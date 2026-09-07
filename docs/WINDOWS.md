# Windows

Hermes supports native Windows installation through PowerShell. Docker-backed services require Docker Desktop; WSL2 is also a valid environment.

```powershell
iex (irm https://hermes-agent.nousresearch.com/install.ps1)
```

For this repository use the one-line command in README. The bootstrap places Hermes profile data according to Hermes' Windows home behavior and does not store OAuth data in the repository.

If Docker networking or file permissions become problematic, prefer running the stack inside WSL2 while keeping the Hermes client native only if you have a specific reason to split them.
