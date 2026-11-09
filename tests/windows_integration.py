"""Real Windows Firewall round trip. Windows + admin only (CI runs it on windows-latest).

Adds the Asia rules for a stand-in Overwatch.exe, reads them back from the
firewall, checks they are UDP, outbound, block and scoped to that program,
then removes them and checks nothing is left.

    python tests/windows_integration.py
"""

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import firewall  # noqa: E402
import main  # noqa: E402
import ranges  # noqa: E402

FAKE_EXE = r"C:\PingSpaceTest\Overwatch.exe"


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        firewall.run_script(firewall.build_unblock_script())
        sys.exit(1)


def main_():
    if sys.platform != "win32" or not main.is_admin():
        print("SKIP: needs Windows and admin")
        return
    gcp, source = ranges.load_gcp(fetch=False)
    bl = ranges.build_block_list(["asia"], gcp, ranges.load_curated())
    expected = sum(len(v) for v in bl.values())

    ok, out = firewall.run_script(firewall.build_block_script(bl, FAKE_EXE, main.GROUP_LABELS))
    check(ok, "block script ran: " + out[:300])

    active, legacy = main.read_status()
    check(active == {"asia"}, "status reads back Asia as blocked (got %s)" % sorted(active))

    ok, out = firewall.run_script(
        "$r = Get-NetFirewallRule -Group 'PingSpace'\n"
        "$items = foreach ($x in $r) {\n"
        "  $a = $x | Get-NetFirewallAddressFilter; $p = $x | Get-NetFirewallPortFilter; $app = $x | Get-NetFirewallApplicationFilter\n"
        "  [pscustomobject]@{name=$x.DisplayName; dir=[string]$x.Direction; action=[string]$x.Action;"
        " proto=[string]$p.Protocol; program=$app.Program; count=@($a.RemoteAddress).Count; enabled=[string]$x.Enabled}\n"
        "}\n"
        "ConvertTo-Json -InputObject @($items) -Compress\n")
    check(ok, "rules read back")
    rules = json.loads(out)
    check(len(rules) >= 1, "%d rules created" % len(rules))
    check(sum(r["count"] for r in rules) == expected, "all %d ranges present" % expected)
    for r in rules:
        check(r["dir"] == "Outbound" and r["action"] == "Block" and r["enabled"] == "True",
              "%s is an enabled outbound block" % r["name"])
        check(r["proto"] == "UDP", "%s is UDP only" % r["name"])
        check(r["program"].lower() == FAKE_EXE.lower(), "%s is scoped to Overwatch.exe" % r["name"])

    ok, out = firewall.run_script(firewall.build_unblock_script())
    check(ok, "unblock script ran")
    active, legacy = main.read_status()
    check(not active and not legacy, "no rules left after unblock")
    print("windows integration: all good (%s)" % source)


if __name__ == "__main__":
    main_()
