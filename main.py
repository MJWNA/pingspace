"""PingSpace: stop Overwatch putting Australian players on Asian servers.

Adds Windows Firewall rules that block Overwatch.exe's game traffic (UDP) to the
regions you pick. Australian servers are never blocked. The interface is an HTML
page (ui/index.html) shown in a native window by pywebview; the page talks to
the Api class below through pywebview's JavaScript bridge, so there is no local
web server with an open port.

Flags:
  --dry-run    print the PowerShell instead of running it (default off Windows)
  --self-test  check the bundled files and range maths, then exit (used by CI)
"""

import ctypes
import json
import os
import sys
import threading
import traceback

import firewall
import ranges
from version import __version__

IS_WINDOWS = sys.platform == "win32"
DRY_RUN = "--dry-run" in sys.argv or not IS_WINDOWS
CONFIG_DIR = os.path.join(os.environ.get("APPDATA") or os.path.expanduser("~"), "PingSpace")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")
GCP_CACHE_PATH = os.path.join(CONFIG_DIR, "gcp_ranges_cache.json")
GROUP_LABELS = {"asia": "Asia", "americas": "Americas", "europe": "Europe-ME"}
DEFAULT_GROUPS = ["asia"]
WEBVIEW2_URL = "https://developer.microsoft.com/microsoft-edge/webview2/"
# pywebview only accepts wildcard filters: "Description (*.ext)". A literal file
# name like "(Overwatch.exe)" raises and the picker never opens.
FILE_TYPES = ("Programs (*.exe)",)


# --- Admin ---------------------------------------------------------------

def is_admin():
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def relaunch_as_admin():
    """Restart elevated via the UAC prompt, then exit this copy."""
    args = sys.argv[1:]
    if getattr(sys, "frozen", False):
        params = " ".join('"%s"' % a for a in args)  # packaged exe: sys.executable is the app
    else:
        params = " ".join('"%s"' % a for a in [os.path.abspath(sys.argv[0])] + args)
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
    sys.exit(0)


def message_box(text, title="PingSpace"):
    if IS_WINDOWS:
        ctypes.windll.user32.MessageBoxW(0, text, title, 0x10)
    else:
        print(title + ": " + text, file=sys.stderr)


# --- Config --------------------------------------------------------------

def load_config():
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_config(cfg):
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except OSError:
        pass


# --- Firewall actions ----------------------------------------------------------

def do_block(selected, program_path):
    gcp, source = ranges.load_gcp(cache_path=GCP_CACHE_PATH)
    curated = ranges.load_curated()
    block_list = ranges.build_block_list(selected, gcp, curated)
    script = firewall.build_block_script(block_list, program_path, GROUP_LABELS)
    total = sum(len(v) for v in block_list.values())
    if DRY_RUN:
        print(script)
        return True, "dry run: would block %d ranges (IP list: %s). nothing changed" % (total, source)
    ok, out = firewall.run_script(script)
    if not ok:
        return False, out
    return True, "blocked %d server ranges. IP list: %s" % (total, source)


def do_unblock():
    if DRY_RUN:
        print(firewall.build_unblock_script())
        return True, "dry run: would remove every rule. nothing changed"
    ok, out = firewall.run_script(firewall.build_unblock_script())
    return ok, ("unblocked everything. normal matchmaking is back" if ok else out)


def read_status():
    if DRY_RUN:
        return set(), False
    ok, out = firewall.run_script(firewall.build_status_script())
    return firewall.parse_status(out if ok else "", GROUP_LABELS)


# --- Bridge exposed to the page as window.pywebview.api ----------------------

class Api:
    """Every public method is callable from JavaScript and returns plain data."""

    def __init__(self):
        self._window = None
        self._lock = threading.Lock()
        self._cfg = load_config()
        self._dry_active = set()  # pretend state, so dry runs still look right

    def _active(self):
        if DRY_RUN:
            return set(self._dry_active), False
        return read_status()

    def get_state(self):
        path = self._cfg.get("overwatch_path", "")
        if not (path and (DRY_RUN or os.path.exists(path))):
            path = firewall.find_overwatch()
        active, legacy = self._active()
        return {
            "version": __version__,
            "selected": [g for g in self._cfg.get("groups", DEFAULT_GROUPS) if g in ranges.GROUPS],
            "path": path,
            "active": sorted(active),
            "legacy": legacy,
            "dry_run": DRY_RUN,
            "music": self._cfg.get("music", True),
        }

    def block(self, selected, path):
        selected = [g for g in (selected or []) if g in ranges.GROUPS]
        path = (path or "").strip()
        if not selected:
            return {"ok": False, "message": "pick at least one region to block"}
        if not path.lower().endswith(".exe") or (not DRY_RUN and not os.path.exists(path)):
            return {"ok": False, "message": "that isn't Overwatch.exe. click 'find it' and pick the game"}
        with self._lock:
            try:
                ok, msg = do_block(selected, path)
            except Exception as e:
                ok, msg = False, str(e)
            if ok:
                self._cfg.update({"groups": selected, "overwatch_path": path})
                save_config(self._cfg)
                if DRY_RUN:
                    self._dry_active = set(selected)
            active, _ = self._active()
        return {"ok": ok, "message": msg, "active": sorted(active)}

    def unblock(self):
        with self._lock:
            try:
                ok, msg = do_unblock()
            except Exception as e:
                ok, msg = False, str(e)
            if ok and DRY_RUN:
                self._dry_active = set()
            active, _ = self._active()
        return {"ok": ok, "message": msg, "active": sorted(active)}

    def browse(self, current=""):
        """Open a file picker for Overwatch.exe. Returns the chosen path, or "" if cancelled."""
        if not self._window:
            return ""
        import webview
        dialog = getattr(getattr(webview, "FileDialog", None), "OPEN", None)
        if dialog is None:
            dialog = webview.OPEN_DIALOG  # pywebview < 5
        start = ""
        for candidate in [os.path.dirname(current or "")] + [os.path.dirname(p) for p in firewall.COMMON_INSTALL_PATHS]:
            if candidate and os.path.isdir(candidate):
                start = candidate
                break
        result = self._window.create_file_dialog(dialog, directory=start, file_types=FILE_TYPES)
        if not result:
            return ""
        return os.path.normpath(result[0] if isinstance(result, (list, tuple)) else result)

    def set_music(self, on):
        self._cfg["music"] = bool(on)
        save_config(self._cfg)
        return True


# --- Entry points ------------------------------------------------------------------

def self_test():
    """Checks the packaged app has everything it needs. Exit code 0 means OK."""
    problems = []
    for parts in (("ui", "index.html"), ("ui", "me.jpg"), ("ui", "pinup1.webp"), ("ui", "pinup2.webp"),
                  ("ui", "sfx", "boing.mp3"), ("ui", "sfx", "ooh.mp3"), ("ui", "sfx", "ohmy.mp3"), ("ui", "sfx", "whistle.mp3"),
                  ("ips.json",), ("data", "gcp_ranges_snapshot.json")):
        if not os.path.exists(ranges.resource_path(*parts)):
            problems.append("missing " + "/".join(parts))
    try:
        import webview  # noqa: F401
    except Exception as e:
        problems.append("pywebview: %s" % e)
    gcp, _ = ranges.load_gcp(fetch=False)
    curated = ranges.load_curated()
    bl = ranges.build_block_list(["asia"], gcp, curated)
    if len(bl.get("asia", [])) < 100:
        problems.append("asia block list too small")
    firewall.build_block_script(bl, r"C:\x\Overwatch.exe", GROUP_LABELS)
    out = "PingSpace %s self-test: %s" % (__version__, "; ".join(problems) or "OK")
    print(out)
    if getattr(sys, "frozen", False):
        # Windowed exes have no console, so leave the result next to the exe too.
        try:
            with open(os.path.join(os.path.dirname(sys.executable), "self-test.txt"), "w") as f:
                f.write(out + "\n")
        except OSError:
            pass
    return 0 if not problems else 1


def run():
    import webview

    # MySpace pages played music as soon as they loaded. WebView2 blocks that
    # by default; this lets the song start (it can be paused, and that sticks).
    os.environ.setdefault("WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS", "--autoplay-policy=no-user-gesture-required")
    api = Api()
    window = webview.create_window(
        "~*PingSpace*~  v" + __version__,
        url=ranges.resource_path("ui", "index.html"),
        js_api=api, width=960, height=820, min_size=(720, 560), background_color="#000000",
    )
    api._window = window
    try:
        # Edge WebView2 only: the old IE engine can't run the page.
        webview.start(gui="edgechromium" if IS_WINDOWS else None)
    except Exception:
        if IS_WINDOWS:
            message_box("PingSpace needs Microsoft Edge WebView2, which is missing on this PC.\n\n"
                        "Install the free 'Evergreen Bootstrapper' from:\n" + WEBVIEW2_URL +
                        "\n\nthen open PingSpace again.\n\n" + traceback.format_exc(limit=1))
        raise


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    if IS_WINDOWS and not DRY_RUN and not is_admin():
        relaunch_as_admin()
    try:
        run()
    except Exception:
        message_box("Something went wrong:\n" + traceback.format_exc())
        sys.exit(1)
