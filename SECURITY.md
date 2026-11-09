# Security

PingSpace runs with administrator rights because it edits Windows Firewall rules, so security reports are taken seriously.

## What it does with those rights

- Creates, reads and removes Windows Firewall rules in its own `PingSpace` rule group, and removes rules named `OW_Server_Lock*` left by the original ow-server-switcher.
- Writes a short PowerShell script to a private temp file, runs it with `-File` and deletes it.
- Reads the Windows uninstall registry keys to find Overwatch.exe.
- Downloads Google's public IP range list from `https://www.gstatic.com/ipranges/cloud.json` and validates it before use.
- Stores settings in `%APPDATA%\PingSpace`.

It does not touch game files or memory, open any network port, or collect or send any data about you.

## Hardening

- The interface talks to Python through pywebview's in-process bridge, not a local web server, so websites can't call it.
- Values from the interface are checked against fixed lists before they reach PowerShell, and every string in the script is single-quote escaped.
- Release executables are built in public GitHub Actions from tagged source and published with a SHA-256 checksum.

## Reporting a vulnerability

Please use [GitHub private vulnerability reporting](https://github.com/MJWNA/pingspace/security/advisories/new) rather than a public issue. Expect a reply within a week.

## Supported versions

Only the latest release gets fixes.
