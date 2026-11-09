"""Builds and runs the PowerShell that adds or removes the Windows Firewall rules.

The script builders are pure (and tested on any OS). Only run_script() and
find_overwatch() touch Windows.
"""

import os
import subprocess
import sys
import tempfile

RULE_GROUP = "PingSpace"
RULE_NAME_PREFIX = "PingSpace"
# Rules the original ow-server-switcher created. Cleared too, so the two
# tools can't leave conflicting rules behind.
LEGACY_RULE_PREFIX = "OW_Server_Lock"
# Addresses per rule. Windows accepts long lists, but smaller rules keep each
# one well inside any limit and make failures easier to read.
MAX_ADDRESSES_PER_RULE = 200

COMMON_INSTALL_PATHS = (
    r"C:\Program Files (x86)\Overwatch\_retail_\Overwatch.exe",
    r"C:\Program Files\Overwatch\_retail_\Overwatch.exe",
    r"C:\Program Files (x86)\Steam\steamapps\common\Overwatch\Overwatch.exe",
    r"C:\Program Files\Steam\steamapps\common\Overwatch\Overwatch.exe",
)


def ps_quote(value):
    """Quote a string as a PowerShell single-quoted literal."""
    return "'" + str(value).replace("'", "''") + "'"


def chunks(items, size):
    for i in range(0, len(items), size):
        yield items[i:i + size]


def _remove_lines():
    return [
        "Remove-NetFirewallRule -Group " + ps_quote(RULE_GROUP) + " -ErrorAction SilentlyContinue",
        "Remove-NetFirewallRule -DisplayName " + ps_quote(LEGACY_RULE_PREFIX + "*") + " -ErrorAction SilentlyContinue",
    ]


def build_block_script(block_list, program_path, group_labels):
    """PowerShell that replaces any existing rules with fresh ones.

    block_list: {group_key: [ip_network]} from ranges.build_block_list.
    If adding any rule fails, every rule in the group is removed again, so
    you're never left half-blocked.
    """
    if not program_path:
        raise ValueError("Overwatch.exe path is required")
    lines = ["$ErrorActionPreference = 'Stop'"] + _remove_lines() + ["try {"]
    for key, nets in block_list.items():
        addresses = [str(n) for n in nets]
        for i, part in enumerate(chunks(addresses, MAX_ADDRESSES_PER_RULE), start=1):
            name = "%s - %s %d" % (RULE_NAME_PREFIX, group_labels.get(key, key), i)
            lines.append(
                "  New-NetFirewallRule"
                " -DisplayName " + ps_quote(name) +
                " -Group " + ps_quote(RULE_GROUP) +
                " -Description " + ps_quote("Blocks Overwatch game traffic to these servers. Remove with the app's Unblock button.") +
                " -Direction Outbound -Action Block -Protocol UDP"
                " -Program " + ps_quote(program_path) +
                " -RemoteAddress @(" + ",".join(ps_quote(a) for a in part) + ")"
                " | Out-Null"
            )
    lines += [
        "} catch {",
        "  Remove-NetFirewallRule -Group " + ps_quote(RULE_GROUP) + " -ErrorAction SilentlyContinue",
        "  throw",
        "}",
    ]
    return "\n".join(lines) + "\n"


def build_unblock_script():
    return "\n".join(_remove_lines()) + "\n"


def build_status_script():
    """Prints one rule display name per line (ours and legacy)."""
    return (
        "Get-NetFirewallRule -Group " + ps_quote(RULE_GROUP) + " -ErrorAction SilentlyContinue"
        " | ForEach-Object { $_.DisplayName }\n"
        "Get-NetFirewallRule -DisplayName " + ps_quote(LEGACY_RULE_PREFIX + "*") + " -ErrorAction SilentlyContinue"
        " | ForEach-Object { $_.DisplayName }\n"
    )


def parse_status(output, group_labels):
    """Return (active_group_keys, legacy_rules_found) from build_status_script output."""
    names = [line.strip() for line in output.splitlines() if line.strip()]
    active = {key for key, label in group_labels.items()
              if any(n.startswith("%s - %s " % (RULE_NAME_PREFIX, label)) for n in names)}
    legacy = any(n.startswith(LEGACY_RULE_PREFIX) for n in names)
    return active, legacy


def run_script(script):
    """Run a PowerShell script on Windows. Returns (ok, output_or_error)."""
    fd, path = tempfile.mkstemp(suffix=".ps1", prefix="pingspace_")
    try:
        with os.fdopen(fd, "w", encoding="utf-8-sig") as f:
            f.write(script)
        res = subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-File", path],
            capture_output=True, text=True,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        if res.returncode == 0:
            return True, res.stdout
        return False, (res.stderr or res.stdout).strip()
    except Exception as e:
        return False, str(e)
    finally:
        try:
            os.remove(path)
        except OSError:
            pass


def _registry_candidates():
    """Install folders from Windows' uninstall list whose name mentions Overwatch."""
    if sys.platform != "win32":
        return []
    import winreg
    found = []
    roots = (
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
    )
    for hive, path in roots:
        try:
            with winreg.OpenKey(hive, path) as key:
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        with winreg.OpenKey(key, winreg.EnumKey(key, i)) as sub:
                            name = winreg.QueryValueEx(sub, "DisplayName")[0]
                            if "overwatch" not in str(name).lower():
                                continue
                            folder = winreg.QueryValueEx(sub, "InstallLocation")[0]
                            found += [os.path.join(folder, "_retail_", "Overwatch.exe"),
                                      os.path.join(folder, "Overwatch.exe")]
                    except OSError:
                        continue
        except OSError:
            continue
    return found


def find_overwatch():
    """Best guess at Overwatch.exe: running process, then the registry, then common folders."""
    if sys.platform == "win32":
        ok, out = run_script(
            "Get-Process -Name Overwatch -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty Path\n")
        if ok and out.strip() and os.path.exists(out.strip()):
            return out.strip()
    for path in _registry_candidates() + list(COMMON_INSTALL_PATHS):
        if os.path.exists(path):
            return path
    return ""
