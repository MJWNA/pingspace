# Contributing

Thanks for helping. Issues and pull requests are welcome, especially:

- IP ranges that should be blocked but aren't, or Australian ranges that got caught (include the server IP and how you found it).
- Overwatch install locations the auto-detect misses.

## Getting set up

```powershell
git clone https://github.com/MJWNA/pingspace.git
cd pingspace
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

You can work on the interface from macOS or Linux: `python main.py` runs as a dry run there, and opening `ui/index.html` in a browser gives a demo mode.

## Pull requests

- Keep changes focused. One fix or feature per PR.
- Add or update tests. CI runs them on Windows along with a real firewall round trip.
- If you change `ui/index.html`, copy it to `docs/demo/index.html` too (a test checks they match).
- Add a line under `## [Unreleased]` in `CHANGELOG.md`.

## Releasing (maintainers)

1. Bump `version.py`.
2. Move the `Unreleased` notes into a new version section in `CHANGELOG.md`.
3. Commit, then `git tag vX.Y.Z && git push origin main --tags`. The release workflow does the rest.
