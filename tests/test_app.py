import filecmp
import os
import re
import sys
import tempfile
import unittest
from unittest import mock

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import main  # noqa: E402
import ranges  # noqa: E402
from version import __version__  # noqa: E402


class ApiDryRunTests(unittest.TestCase):
    """The bridge the page calls, in dry-run mode (no firewall changes)."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        real_load = ranges.load_gcp
        offline = lambda **kw: real_load(fetch=False)  # noqa: E731
        self.patches = [
            mock.patch.object(main, "DRY_RUN", True),
            mock.patch.object(main, "CONFIG_PATH", os.path.join(self.tmp, "config.json")),
            mock.patch.object(main, "CONFIG_DIR", self.tmp),
            mock.patch.object(main.ranges, "load_gcp", offline),
            mock.patch("builtins.print"),
        ]
        for p in self.patches:
            p.start()
        self.api = main.Api()

    def tearDown(self):
        for p in self.patches:
            p.stop()

    def test_block_then_unblock(self):
        r = self.api.block(["asia"], r"C:\Games\Overwatch\_retail_\Overwatch.exe")
        self.assertTrue(r["ok"], r)
        self.assertEqual(r["active"], ["asia"])
        self.assertEqual(self.api.get_state()["active"], ["asia"])
        r = self.api.unblock()
        self.assertTrue(r["ok"])
        self.assertEqual(r["active"], [])

    def test_block_saves_choices(self):
        self.api.block(["asia", "europe"], r"C:\x\Overwatch.exe")
        state = main.Api().get_state()
        self.assertEqual(state["selected"], ["asia", "europe"])
        self.assertEqual(state["path"], r"C:\x\Overwatch.exe")

    def test_rejects_bad_input(self):
        self.assertFalse(self.api.block([], r"C:\x\Overwatch.exe")["ok"])
        self.assertFalse(self.api.block(["asia"], "")["ok"])
        self.assertFalse(self.api.block(["asia"], r"C:\x\notes.txt")["ok"])
        # unknown group names from the page are ignored, not passed to PowerShell
        self.assertFalse(self.api.block(["'; Remove-Item C:\\ -Recurse #"], r"C:\x\Overwatch.exe")["ok"])

    def test_state_shape(self):
        s = self.api.get_state()
        self.assertEqual(s["version"], __version__)
        self.assertTrue(s["dry_run"])
        for key in ("selected", "path", "active", "legacy", "music"):
            self.assertIn(key, s)

    def test_music_preference_sticks(self):
        self.api.set_music(False)
        self.assertFalse(main.Api().get_state()["music"])

    def test_self_test_passes(self):
        try:
            import webview  # noqa: F401
        except ImportError:
            self.skipTest("pywebview not installed")
        self.assertEqual(main.self_test(), 0)


class PageTests(unittest.TestCase):
    def setUp(self):
        with open(os.path.join(ROOT, "ui", "index.html"), encoding="utf-8") as f:
            self.html = f.read()

    def test_page_is_fully_offline(self):
        # no fonts, scripts or images from the internet: the app must work offline
        self.assertEqual(re.findall(r"""(?:src|href)\s*=\s*["']https?://""", self.html), [])
        self.assertNotIn("@import", self.html)

    def test_demo_copy_matches_app(self):
        for name in ("index.html", "me.jpg", "pinup1.webp", "pinup2.webp"):
            self.assertTrue(filecmp.cmp(os.path.join(ROOT, "ui", name), os.path.join(ROOT, "docs", "demo", name), shallow=False),
                            "docs/demo/%s is out of date: copy ui/%s over it" % (name, name))


if __name__ == "__main__":
    unittest.main()
