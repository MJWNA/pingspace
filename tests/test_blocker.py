import ipaddress
import itertools
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import firewall  # noqa: E402
import ranges  # noqa: E402

LABELS = {"asia": "Asia", "americas": "Americas", "europe": "Europe-ME"}


def ip(a):
    return ipaddress.ip_address(a)


def blocked(block_list, address):
    return any(ip(address) in n for nets in block_list.values() for n in nets)


class RangeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gcp, _ = ranges.load_gcp(fetch=False)
        cls.curated = ranges.load_curated()
        cls.protected = ranges.protected_networks(cls.gcp, cls.curated)

    def test_no_selection_blocks_nothing(self):
        self.assertEqual(ranges.build_block_list([], self.gcp, self.curated), {})

    def test_australia_never_blocked_in_any_combination(self):
        keys = list(ranges.GROUPS)
        for r in range(1, len(keys) + 1):
            for combo in itertools.combinations(keys, r):
                bl = ranges.build_block_list(combo, self.gcp, self.curated)
                for nets in bl.values():
                    for n in nets:
                        for p in self.protected:
                            if n.version == p.version:
                                self.assertFalse(n.overlaps(p), "%s overlaps Australian %s (%s)" % (n, p, combo))

    def test_original_tool_overlap_bug_is_fixed(self):
        # The original blocked Singapore's 34.124.0.0/16, which contains Sydney's
        # 34.124.40.0/23, and Netherlands' 37.244.0.0/16, which contains 37.244.42.0/24.
        bl = ranges.build_block_list(["asia", "europe"], self.gcp, self.curated)
        self.assertFalse(blocked(bl, "34.124.40.10"))
        self.assertFalse(blocked(bl, "34.124.58.10"))
        self.assertFalse(blocked(bl, "37.244.42.10"))
        # The rest of those broad ranges is still blocked.
        self.assertTrue(blocked(bl, "34.124.0.10"))
        self.assertTrue(blocked(bl, "37.244.0.10"))

    def test_asia_blocks_known_asian_servers(self):
        bl = ranges.build_block_list(["asia"], self.gcp, self.curated)
        self.assertTrue(blocked(bl, "103.4.114.25"))   # Blizzard Singapore (curated)
        self.assertTrue(blocked(bl, "103.4.114.75"))   # Blizzard Japan (curated)
        self.assertTrue(blocked(bl, "117.52.1.1"))     # Korea, not on Google Cloud
        self.assertFalse(blocked(bl, "103.4.114.216"))  # Blizzard Australia
        self.assertNotIn("americas", bl)
        self.assertNotIn("europe", bl)

    def test_every_gcp_asia_range_is_blocked_unless_australian(self):
        bl = ranges.build_block_list(["asia"], self.gcp, self.curated)
        for net, scope in self.gcp:
            if scope.startswith("asia-") and not any(net.overlaps(p) for p in self.protected if p.version == net.version):
                self.assertTrue(blocked(bl, str(net.network_address)), "%s (%s) not blocked" % (net, scope))

    def test_global_scope_left_alone(self):
        bl = ranges.build_block_list(list(ranges.GROUPS), self.gcp, self.curated)
        all_curated = [n for nets in self.curated.values() for n in nets]
        for net, scope in self.gcp:
            if scope == "global" and not any(net.overlaps(c) for c in all_curated if c.version == net.version):
                self.assertFalse(blocked(bl, str(net.network_address)), "global range %s blocked" % net)

    def test_parse_gcp_rejects_garbage(self):
        for bad in ({}, {"prefixes": []}, {"prefixes": [{"ipv4Prefix": "1.2.3.0/24", "scope": "asia-east1"}] * 300}, []):
            with self.assertRaises(ValueError):
                ranges.parse_gcp(bad)

    def test_subtract_splits_ranges(self):
        out = ranges.subtract([ipaddress.ip_network("10.0.0.0/16")], [ipaddress.ip_network("10.0.5.0/24")])
        self.assertFalse(any(n.overlaps(ipaddress.ip_network("10.0.5.0/24")) for n in out))
        self.assertEqual(sum(n.num_addresses for n in out), 65536 - 256)


class FirewallScriptTests(unittest.TestCase):
    def setUp(self):
        self.bl = {"asia": [ipaddress.ip_network("10.%d.0.0/16" % i) for i in range(255)]
                   + [ipaddress.ip_network("2001:db8::/32")]}

    def test_rules_are_chunked_scoped_and_udp_only(self):
        script = firewall.build_block_script(self.bl, r"C:\Games\Overwatch\_retail_\Overwatch.exe", LABELS)
        rule_lines = [l for l in script.splitlines() if "New-NetFirewallRule" in l]
        self.assertEqual(len(rule_lines), 2)  # 256 addresses -> 200 + 56
        for line in rule_lines:
            self.assertLessEqual(line.count("','") + 1, firewall.MAX_ADDRESSES_PER_RULE)
            self.assertIn("-Protocol UDP", line)
            self.assertIn("-Direction Outbound", line)
            self.assertIn(r"-Program 'C:\Games\Overwatch\_retail_\Overwatch.exe'", line)
            self.assertIn("-Group 'PingSpace'", line)
        self.assertIn("'2001:db8::/32'", script)

    def test_program_path_quote_is_escaped(self):
        script = firewall.build_block_script(self.bl, r"C:\Ronnie's Games\Overwatch.exe", LABELS)
        self.assertIn(r"-Program 'C:\Ronnie''s Games\Overwatch.exe'", script)

    def test_program_path_required(self):
        with self.assertRaises(ValueError):
            firewall.build_block_script(self.bl, "", LABELS)

    def test_block_clears_old_rules_and_rolls_back_on_failure(self):
        script = firewall.build_block_script(self.bl, r"C:\x\Overwatch.exe", LABELS)
        self.assertLess(script.index("Remove-NetFirewallRule -Group"), script.index("New-NetFirewallRule"))
        self.assertIn("Remove-NetFirewallRule -DisplayName 'OW_Server_Lock*'", script)
        self.assertIn("} catch {", script)

    def test_unblock_removes_ours_and_legacy(self):
        s = firewall.build_unblock_script()
        self.assertIn("-Group 'PingSpace'", s)
        self.assertIn("'OW_Server_Lock*'", s)

    def test_parse_status(self):
        out = "PingSpace - Asia 1\nPingSpace - Asia 2\nOW_Server_Lock_Australia\n"
        active, legacy = firewall.parse_status(out, LABELS)
        self.assertEqual(active, {"asia"})
        self.assertTrue(legacy)
        self.assertEqual(firewall.parse_status("", LABELS), (set(), False))


if __name__ == "__main__":
    unittest.main()
