# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.4.0] - 2026-11-10

### Added

- More emo-era cringe in the app and the guide: tilted rainbow WordArt phrases ("rawr XD", "its not a phase MOM", "*glomps u*"...), heavy-eyeliner emo eyes that blink out of the dark with a mascara tear, rains of broken hearts, skulls, crosses and stars, fake Windows 98 "u r the 1,000,000th visitor" popups that slide in, shake and leave, and Blingee sparkles round the pin-ups. Where the side gutters have room, pop-ups stay in them so the text stays readable.

### Fixed

- The guide's gutter pin-ups were piled up and hidden behind the steps: a later `.pinhit{position:relative}` rule overrode the gutter's `position:absolute`. A layout script now spreads the pin-ups and stickers evenly down both sides, sized to the space available, and the gutters show from 1100px wide instead of 1290px.

## [1.3.1] - 2026-11-10

### Added

- Three new pin-ups of Ronnie: the Marilyn (dress billowing over a vent), the sailor salute and the roller-skating diner waitress. The app picks from all five for peekers, streakers, wanderers, lurkers and the cancan (each positioned by its real width), the bum gag sometimes swaps in the Marilyn, the guide's gutters mix them in, and one peeks up from the bottom corner of the studio now and then.

## [1.3.0] - 2026-11-10

### Added

- **PingSpace Studio** (`ui/studio.html`), an 8-bit beat lab opened from the profile's music box:
  - FL Studio-style channel rack with 10 channels (Kick, 808, Snare, Clap, Hat, Open Hat, Perc, Lead, Bass, Keys), 16 or 32 steps, mute, solo, volume and a trigger light per channel.
  - Piano roll for every channel across six octaves: click to add, drag to lengthen, drag to move, drag the edge to resize, right-click or double-click to delete, clickable piano keys.
  - Play notes from the computer keyboard (Z to M and Q to U), with REC to record into the loop while it plays.
  - Synth engine with three pulse widths, triangle, saw and noise, ADSR, low-pass filter and resonance, vibrato, glide and detune. Drums have tune, decay, punch, snap, tone and drive, and the 808 is melodic.
  - Patterns A to D with copy and paste, song mode that plays a chain of up to 8 patterns, BPM, swing, master volume, a 3 to 16 bit CRUNCH bit-crusher and tempo-synced echo.
  - RANDOM BEAT, two demo songs (lo-ping lullaby and ping pong panic), autosave, saved songs in `%APPDATA%\PingSpace\songs`, and EXPORT .WAV (rendered offline, saved through a save dialog).
- Y2K effects (`ui/y2k.js`) on the app and the install guide: random neon lightning bolts with forks and a soft flash, spinning NEW!/HOT!/OMG!! starbursts, twinkling sparkles and shooting stars. Flashes stay well under the photosensitivity limit, and it all switches off under reduced motion.

### Changed

- The sausage sprays far more: bursts of 3 to 7 faster, bigger spurts every second or two, wider spray, more goo on screen at once. Pin-up hit testing is now measured once per frame so hundreds of drops stay smooth.

## [1.2.2] - 2026-11-10

### Fixed

- In the app the sausage cursor only showed over buttons. pywebview injects `body { cursor: default }` after the page's CSS when text selection is off, which beat the page's plain `body` rule. The cursor rule now uses `html body`, and a test checks it still outranks pywebview's injected CSS.

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

[Unreleased]: https://github.com/MJWNA/pingspace/compare/v1.4.0...HEAD
[1.4.0]: https://github.com/MJWNA/pingspace/compare/v1.3.1...v1.4.0
[1.3.1]: https://github.com/MJWNA/pingspace/compare/v1.3.0...v1.3.1
[1.3.0]: https://github.com/MJWNA/pingspace/compare/v1.2.2...v1.3.0
[1.2.2]: https://github.com/MJWNA/pingspace/compare/v1.2.1...v1.2.2
[1.2.1]: https://github.com/MJWNA/pingspace/compare/v1.2.0...v1.2.1
[1.2.0]: https://github.com/MJWNA/pingspace/compare/v1.1.1...v1.2.0
[1.1.1]: https://github.com/MJWNA/pingspace/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/MJWNA/pingspace/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/MJWNA/pingspace/releases/tag/v1.0.0
