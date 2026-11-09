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

    def test_file_picker_filters_are_valid(self):
        try:
            from webview.util import parse_file_type
        except ImportError:
            self.skipTest("pywebview not installed")
        for f in main.FILE_TYPES + main.WAV_TYPES:
            parse_file_type(f)  # raises ValueError for a filter pywebview rejects

    def test_studio_songs_round_trip(self):
        with mock.patch.object(main, "SONGS_DIR", os.path.join(self.tmp, "songs")):
            song = '{"name": "x", "channels": [], "patterns": {"A": []}}'
            r = self.api.save_song("My Beat!!", song)
            self.assertTrue(r["ok"], r)
            self.assertEqual(r["name"], "My Beat")
            self.assertEqual(self.api.list_songs(), ["My Beat"])
            self.assertEqual(self.api.load_song("My Beat"), song)
            self.assertTrue(self.api.delete_song("My Beat"))
            self.assertEqual(self.api.list_songs(), [])

    def test_studio_song_names_cant_escape_the_folder(self):
        songs = os.path.join(self.tmp, "songs")
        with mock.patch.object(main, "SONGS_DIR", songs):
            r = self.api.save_song("../../../evil", '{"channels": [], "patterns": {}}')
            self.assertTrue(r["ok"])
            self.assertEqual(os.listdir(songs), ["evil.json"])
            self.assertFalse(self.api.save_song("../..", "{}")["ok"])           # nothing left after cleaning
            self.assertIsNone(self.api.load_song("../../etc/passwd"))

    def test_studio_rejects_junk(self):
        with mock.patch.object(main, "SONGS_DIR", os.path.join(self.tmp, "songs")):
            self.assertFalse(self.api.save_song("x", "not json")["ok"])
            self.assertFalse(self.api.save_song("x", '{"just": "a dict"}')["ok"])
            self.assertFalse(self.api.save_song("x", "x" * (main.MAX_SONG_BYTES + 1))["ok"])
        self.assertFalse(self.api.save_wav("bm90IGEgd2F2", "x.wav")["ok"])      # base64 of "not a wav"

    def test_browse_without_window_returns_empty(self):
        self.assertEqual(self.api.browse(), "")

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
        for name in ("index.html", "studio.html", "goo.js", "y2k.js"):
            with open(os.path.join(ROOT, "ui", name), encoding="utf-8") as f:
                text = f.read()
            self.assertEqual(re.findall(r"""(?:src|href)\s*=\s*["']https?://""", text), [], name)
            self.assertNotIn("@import", text, name)

    def test_profile_links_to_studio(self):
        self.assertIn('href="studio.html"', self.html)
        with open(os.path.join(ROOT, "ui", "studio.html"), encoding="utf-8") as f:
            self.assertIn('href="index.html"', f.read())

    def test_sausage_cursor_beats_pywebview_injected_css(self):
        # pywebview appends "body {...; cursor: default;}" when text selection is off. Our rule
        # has to be more specific than a bare "body" selector or the cursor reverts to the arrow.
        try:
            import webview
            js = open(os.path.join(os.path.dirname(webview.__file__), "js", "customize.js"), encoding="utf-8").read()
            self.assertIn("cursor: default", js)
        except (ImportError, OSError):
            pass
        self.assertIn("html, html body{cursor:url(sausage-cursor.png)", self.html)
        self.assertNotRegex(self.html, r"(?m)^\s*body\{[^}]*cursor:")

    def test_demo_copy_matches_app(self):
        for name in ("index.html", "me.jpg", "pinup1.webp", "pinup2.webp", "goo.js", "sausage-cursor.png", "y2k.js", "studio.html",
                     "sfx/boing.mp3", "sfx/ooh.mp3", "sfx/ohmy.mp3", "sfx/whistle.mp3"):
            self.assertTrue(filecmp.cmp(os.path.join(ROOT, "ui", name), os.path.join(ROOT, "docs", "demo", name), shallow=False),
                            "docs/demo/%s is out of date: copy ui/%s over it" % (name, name))


if __name__ == "__main__":
    unittest.main()
