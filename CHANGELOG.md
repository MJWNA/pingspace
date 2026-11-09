# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.1.0] - 2026-11-09

### Added

- Pin-up chaos in the app: pin-ups of Ronnie peek in from every screen edge, sprint across the window, wander around non-stop, lurk behind the profile, status and Top 8 boxes, and do a cancan line when blocking succeeds. All of it is click-through, so no button is ever blocked, and it calms down under the system's reduced-motion setting.

## [1.0.0] - 2026-11-09

First release of PingSpace, a rework of [Peak2548/ow-server-switcher](https://github.com/Peak2548/ow-server-switcher) for Australian players.

### Added

- Block Overwatch's game traffic to Asia, the Americas and/or Europe and the Middle East, with Asia selected by default.
- Google Cloud's published IP ranges, fetched on each block, cached, and bundled as an offline snapshot.
- Rules scoped to `Overwatch.exe` and UDP only; other apps and Battle.net login are unaffected.
- All-or-nothing rule writes: a failure part way through removes every rule again.
- Firewall status read on launch, so the app shows what is blocked right now.
- Automatic Overwatch.exe detection (running process, Windows uninstall registry, common install paths) with a file picker fallback.
- MySpace-style interface in a pywebview window: Top 8 region picker, glitch effects and an original WebAudio chiptune with a pause that persists.
- `--dry-run` and `--self-test` flags.
- Unit tests, a Windows Firewall integration test, CI on Windows and a release workflow that builds, self-tests and checksums `PingSpace.exe`.
- Step-by-step install guide and live demo on GitHub Pages.

### Fixed

- Selecting Australia in the original tool blocked some Australian servers, because its Singapore (`34.124.0.0/16`) and Netherlands (`37.244.0.0/16`) ranges contain Sydney ranges. Australian ranges are now subtracted from every block list.
- Rules from the original tool applied to every program on the PC. They are now limited to Overwatch.exe, and rules left behind by the original tool are cleaned up.

[Unreleased]: https://github.com/MJWNA/pingspace/compare/v1.1.0...HEAD
[1.1.0]: https://github.com/MJWNA/pingspace/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/MJWNA/pingspace/releases/tag/v1.0.0
