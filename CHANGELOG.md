# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.2.1] - 2026-11-09

### Changed

- Spurts carry far more volume than drips: a bigger glob, a rope of medium globs that fuses into a thick stream, and a spray of 5 to 8 droplets. Big splats get more and longer drips, and more goo can be on screen at once.

## [1.2.0] - 2026-11-09

### Added

- Sausage cursor and leaky goo in the app, shared with the install guide (`ui/goo.js`). A blob hangs off the cursor tip, swells when the pointer slows, drops, and splats on whatever is underneath, with drips that fade after a few seconds. Every few seconds the tip fires a burst of 2 to 4 spurts, each weaker than the last, that arc through the air and land on things, with dripping in between.
- Drops land on the pin-ups themselves, following each image's exact outline (head, shoulders, chest), and stick to them as they move, flip, jiggle and wobble. Every pin-up now sits in a `.pinhit` box with three invisible corner markers so the goo can trace its on-screen transform.

### Fixed

- The second "install supervisor" pin-up in the guide was meant to be mirrored but wasn't.

## [1.1.1] - 2026-11-09

### Fixed

- **Find Overwatch** and **[ find it ]** did nothing. The file picker's filter (`Overwatch (Overwatch.exe)`) isn't a format pywebview accepts, so it raised before the picker opened and the page swallowed the error. The picker now opens in the Overwatch folder, the blog log says what happened (picked, cancelled, or not Overwatch.exe), the path box flashes, and any failure shows an error box. A test checks the filter against pywebview's own validator.

## [1.1.0] - 2026-11-09

### Added

- Pin-up chaos in the app: pin-ups of Ronnie peek in from every screen edge, sprint across the window, wander around non-stop, lurk behind the profile, status and Top 8 boxes, and do a cancan line when blocking succeeds. All of it is click-through, so no button is ever blocked, and it calms down under the system's reduced-motion setting.
- The bum gag: hovering the block button slides Ronnie's pin-up over it, and clicking boops him with a jelly wobble, a comic BOING and an ElevenLabs sound effect. The click always goes through to the button.

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

[Unreleased]: https://github.com/MJWNA/pingspace/compare/v1.2.1...HEAD
[1.2.1]: https://github.com/MJWNA/pingspace/compare/v1.2.0...v1.2.1
[1.2.0]: https://github.com/MJWNA/pingspace/compare/v1.1.1...v1.2.0
[1.1.1]: https://github.com/MJWNA/pingspace/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/MJWNA/pingspace/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/MJWNA/pingspace/releases/tag/v1.0.0
