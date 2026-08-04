# Overwatch Server Switcher

> A lightweight Windows desktop tool that locks Overwatch matchmaking to your chosen region by creating outbound Windows Firewall rules that block every other region's server IP ranges.

[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Maintenance-brightgreen.svg)]()

---

## Overview

**ow-server-switcher** is a single-file Python application that gives Overwatch players control over their matchmaking region. By automatically creating and removing Windows Outbound Firewall rules, it blocks the IP ranges of unwanted matchmaking servers — forcing the game's matchmaker to place you in the **region you select** (Japan, Singapore, Korea, Taiwan, Australia, Americas, or Netherlands).

This tool is designed to be simple, safe, and fully inspectable: no hidden binaries, no game file modifications, no injections. Just a transparent script that manages your local firewall.

---

## How It Works

1. **IP Blocklist:** The script reads a curated list of IP ranges (`ips.json`) used by Overwatch matchmaking servers across every supported region.

2. **PowerShell Firewall Rules:** When you click a region button, the script uses PowerShell's `New-NetFirewallRule` cmdlet to create a Windows **Outbound Firewall Rule** that blocks all outbound traffic to the IP ranges of **every other region** (except `Blizzard_Global`).

3. **Matchmaking Effect:** With all non-selected regions' servers blocked, Overwatch's matchmaker is forced to search only within your chosen region.

4. **Default / Reset:** The **"Default"** button runs `Remove-NetFirewallRule` to delete all custom rules and restores your normal network configuration.

**What this tool does NOT do:**

- It does not modify any Overwatch game files, memory, or executables.
- It does not intercept, modify, or inject network packets.
- It does not use any third-party drivers or kernel-level hooks.

---

## Supported Regions

| Region | Description |
|---|---|
| **Japan** | TYO / GTK data centers |
| **Singapore** | Southeast Asia data centers |
| **Korea** | KR data centers |
| **Taiwan** | TW data centers |
| **Australia** | AU data centers |
| **Americas** | US / NA data centers |
| **Netherlands** | EU data centers |

Click **Default** at any time to remove all rules and return to normal matchmaking.

---

## Requirements

| Requirement | Details |
|---|---|
| **Operating System** | Windows 10 or Windows 11 (64-bit) |
| **Python** | Python 3.x (for running the script directly) |
| **Administrator Rights** | Required — the tool modifies Windows Firewall rules |
| **PowerShell** | PowerShell 5.1+ (included with Windows by default) |
| **Dependencies** | `customtkinter` (`pip install customtkinter`) |

---

## Installation & Usage

### Option 1: Run Directly (No Installation Required)

1. Ensure Python 3.x is installed. Download from [python.org](https://www.python.org/downloads/).
2. Install the required dependency:
   ```powershell
   pip install customtkinter
   ```
3. Clone or download this repository, then navigate to the folder:
   ```powershell
   cd ow-server-switcher
   ```
4. Run the script:
   ```powershell
   python main.py
   ```
5. Accept the UAC prompt if prompted for Administrator privileges.
6. Click any region button (e.g. **Japan**) to lock matchmaking to that region, or click **Default** to restore normal matchmaking.

### Option 2: Compile to Standalone `.exe` (Optional)

If you prefer a standalone executable without requiring Python on your machine:

1. Install PyInstaller:
   ```powershell
   pip install pyinstaller
   ```
2. Compile the script:
   ```powershell
   pyinstaller --onefile --noconsole --name "OW_Server_Switcher" main.py
   ```
3. The compiled executable will be in the `dist/` folder:
   ```
   dist\OW_Server_Switcher.exe
   ```
4. Run `OW_Server_Switcher.exe` as needed.

---

## ⚠️ Important: How Reliable Is This?

This tool works by manipulating Windows Firewall outbound rules, which is a **trial-and-error approach**:

- It is **not guaranteed** to lock you to a region every single time.
- Depending on your network, current game session state, and Blizzard's server routing, the matchmaker may sometimes still connect you to a blocked region.
- If it doesn't work the first time, **retry**: click **Default**, then click your desired region again, and restart Overwatch.
- Results can vary between runs — you may need a few attempts (apply rule → restart game → retry matchmaking) before it reliably keeps you on the target region.

The IP ranges are based on publicly gathered data and may become outdated as Blizzard rotates or changes their server infrastructure. If the tool stops working, the IP ranges in `ips.json` likely need updating.

---

## Troubleshooting

### "Failed to connect to server" during matchmaking

After applying the rules, if you see **"Failed to connect to server"** when retrying matchmaking:

1. **Wait a few seconds** — the firewall rule may take a moment to fully take effect.
2. **Restart Overwatch** completely (close via Task Manager to ensure the process is fully terminated).
3. Click **Default** in the tool, then click your region again to reapply the rules.
4. If issues persist, temporarily disable Windows Defender Firewall and test to confirm the firewall rules are the cause.

### UAC Prompt Does Not Appear / Admin Rights Error

- Right-click the script (or `.exe`) and select **"Run as administrator"**.
- Ensure your Windows user account has administrator privileges.
- If Group Policy blocks elevation, you may need to run PowerShell manually as Admin and execute:
  ```powershell
  python main.py
  ```

### Firewall Rule Already Exists

- Click **Default** first to clear existing rules, then click your region again.

### PowerShell Execution Policy Error

- Run PowerShell as Administrator and execute:
  ```powershell
  Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
  ```

---

## Disclaimer & Legal Notice

### Important: Read Before Using

**This tool ONLY modifies local Windows Firewall outbound rules.** It does not:

- Modify, inject into, or alter any Overwatch game files, memory, or executables.
- Intercept, modify, spoof, or inject network packets.
- Use any form of game modding, cheating, or exploitation techniques.

This is a network management utility that blocks outbound connections at the OS level — the same way any firewall application (e.g., Windows Defender Firewall, third-party firewalls) operates.

### No Ban Guarantee

The author has used this tool for extended periods without any reported account suspensions or bans. **However, there is no guarantee that Blizzard will not consider this a violation of their Terms of Service.** Account security and integrity are ultimately determined by Blizzard's automated systems, which may flag unusual networking behavior.

**Use this tool at your own risk.** The developers of this project are not responsible for any account consequences, game updates that break functionality, or any other issues arising from its use.

### Terms of Service

Blizzard Entertainment's [Terms of Service](https://www.blizzard.com/legal) govern the use of Overwatch. While modifying local firewall rules is a standard and widely-accepted network management practice, **you use this tool at your own risk**.

### Unofficial Project

This project is **unofficial and is not affiliated with, endorsed by, or associated with Blizzard Entertainment, Inc. or Overwatch**.

- Overwatch and Blizzard Entertainment are trademarks of Blizzard Entertainment, Inc.
- All game assets, names, and related intellectual property belong to their respective owners.
- This project is provided for educational and personal use only.

---

## Project Structure

```
ow-server-switcher/
├── main.py        # Single-file application (main script)
├── ips.json       # Overwatch server IP ranges by region
├── README.md      # This file
└── LICENSE        # MIT License
```

---

## Contributing

Contributions are welcome! Please feel free to open issues and submit pull requests.

Areas where help is especially appreciated:

- Updating `ips.json` with current server IP ranges.
- Adding support for additional regions.
- Improving the GUI layout or error handling.

---

## License

This project is licensed under the [MIT License](LICENSE).

---

*Built with Python, CustomTkinter, and PowerShell. No game files were harmed in the making of this tool.*
