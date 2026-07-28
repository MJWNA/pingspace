# Overwatch Server Switcher

> A lightweight, transparent Windows desktop tool that locks Overwatch matchmaking to Japan servers by managing outbound firewall rules.

[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Maintenance-brightgreen.svg)]()

---

## Overview

**ow-server-switcher** is a single-file Python application that gives Overwatch players control over their matchmaking region. By automatically creating and removing Windows Outbound Firewall rules, it blocks the IP ranges of unwanted matchmaking servers — forcing the game's matchmaker to place you in the **Japan (TYO/GTK)** region.

This tool is designed to be simple, safe, and fully inspectable: no hidden binaries, no game file modifications, no injections. Just a transparent script that manages your local firewall.

---

## Features

### Current Features

| Feature | Description |
|---|---|
| **Japan Only** | Blocks all non-Japan matchmaking server IP ranges with a single click. |
| **Reset** | Removes all custom firewall rules and restores default Overwatch matchmaking. |
| **Auto-Admin Elevation** | Automatically prompts for Administrator privileges when needed. |
| **Transparent Single-File Script** | The entire tool is one Python file (`ow_switcher.py`) — safe to read, audit, and verify. |
| **Dark Mode GUI** | Clean, minimal Tkinter interface with a dark theme. |

### Limitations

> **Japan-Only Support:** This tool currently **only supports locking to Japan servers (TYO/GTK)**. The firewall rules block IP ranges for Singapore, Korea, Taiwan, Australia, EU, US, and other regions to funnel matchmaking into Japan.
>
> Support for locking to other specific server regions (e.g., US, EU, Korea) may be added in future updates.

---

## How It Works

1. **IP Blocklist:** The script contains a curated list of IP ranges used by Overwatch matchmaking servers outside of Japan (Middle East, Singapore, Taiwan, Korea, Australia, EU, US/Americas).

2. **PowerShell Firewall Rules:** When you click **"Japan Only"**, the script uses PowerShell's `New-NetFirewallRule` cmdlet to create a Windows **Outbound Firewall Rule** that blocks all outbound traffic to those IP ranges.

3. **Matchmaking Effect:** With non-Japan matchmaking servers blocked, Overwatch's matchmaker is forced to search only within the Japan region.

4. **Reset:** The **"Reset"** button runs `Remove-NetFirewallRule` to delete the custom rule, restoring your default network configuration and normal matchmaking.

**What this tool does NOT do:**
- It does not modify any Overwatch game files, memory, or executables.
- It does not intercept, modify, or inject network packets.
- It does not use any third-party drivers or kernel-level hooks.

---

## Requirements

| Requirement | Details |
|---|---|
| **Operating System** | Windows 10 or Windows 11 (64-bit) |
| **Python** | Python 3.x (for running the script directly) |
| **Administrator Rights** | Required — the tool modifies Windows Firewall rules |
| **PowerShell** | PowerShell 5.1+ (included with Windows by default) |

---

## Installation & Usage

### Option 1: Run Directly (No Installation Required)

1. Ensure Python 3.x is installed. Download from [python.org](https://www.python.org/downloads/).
2. Clone or download this repository, then navigate to the folder:
   ```powershell
   cd ow-server-switcher
   ```
3. Run the script:
   ```powershell
   python ow_switcher.py
   ```
4. Accept the UAC prompt if prompted for Administrator privileges.
5. Click **"Japan Only"** to lock to Japan servers, or **"Reset"** to restore default matchmaking.

### Option 2: Compile to Standalone `.exe` (Optional)

If you prefer a standalone executable without requiring Python on your machine:

1. Install PyInstaller:
   ```powershell
   pip install pyinstaller
   ```
2. Compile the script:
   ```powershell
   pyinstaller --onefile --noconsole --name "OW_Server_Switcher" ow_switcher.py
   ```
3. The compiled executable will be in the `dist/` folder:
   ```
   dist\OW_Server_Switcher.exe
   ```
4. Run `OW_Server_Switcher.exe` as needed.

---

## Troubleshooting

### "Failed to connect to server" during matchmaking retry

After applying the Japan-only rules, if you see **"Failed to connect to server"** when retrying matchmaking:

1. **Wait a few seconds** — the firewall rule may take a moment to fully propagate.
2. **Restart Overwatch** completely (close via Task Manager to ensure the process is fully terminated).
3. **Click "Reset"** in the tool, then click **"Japan Only"** again to reapply the rules.
4. If issues persist, temporarily disable Windows Defender Firewall and test to confirm the firewall rules are the cause.

### UAC Prompt Does Not Appear / Admin Rights Error

- Right-click the script (or `.exe`) and select **"Run as administrator"**.
- Ensure your Windows user account has administrator privileges.
- If Group Policy blocks elevation, you may need to run PowerShell manually as Admin and execute:
  ```powershell
  python ow_switcher.py
  ```

### Firewall Rule Already Exists

- Click **"Reset"** first to clear existing rules, then click **"Japan Only"** again.

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

### Terms of Service

Blizzard Entertainment's [Terms of Service](https://www.blizzard.com/legal) govern the use of Overwatch. While modifying local firewall rules is a standard and widely-accepted network management practice, **you use this tool at your own risk**. The developers of this project do not guarantee compatibility with future game updates and are not responsible for any account consequences.

### Unofficial Project

This project is **unofficial and is not affiliated with, endorsed by, or associated with Blizzard Entertainment, Inc. or Overwatch**.

- Overwatch and Blizzard Entertainment are trademarks of Blizzard Entertainment, Inc.
- All game assets, names, and related intellectual property belong to their respective owners.
- This project is provided for educational and personal use only.

---

## Project Structure

```
ow-server-switcher/
├── ow_switcher.py     # Single-file application (main script)
├── README.md          # This file
└── LICENSE            # MIT License
```

---

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

### Suggested Future Enhancements
- [ ] Support for locking to other server regions (US, EU, Korea, etc.)
- [ ] Region selector dropdown in the GUI
- [ ] Auto-detection of current IP ranges via Blizzard API
- [ ] System tray icon and keyboard shortcuts
- [ ] Preset profiles for different server configurations

---

## License

This project is licensed under the [MIT License](LICENSE).

---

*Built with Python, Tkinter, and PowerShell. No game files were harmed in the making of this tool.*
