# Reference harness extraction audit — 2026-08-27

Source inspected: the physically accepted Mochi Mini project beside this clean
scaffold. The accepted unit was left operational; no public refactor was loaded
onto it during this audit.

## Safe core candidates

- structured approval queue and bounded summary logic;
- exact session registry, provider boundaries, and exact-TTY lifecycle checks;
- Codex App Server proxy and Claude/Grok hook concepts;
- validated 160×80 animation loader and provider-card renderer;
- native K07 display, light, hotkey, config-read, and guarded key-repair logic;
- full unit and loopback integration tests;
- the eyes-free control semantics and failure-closed approval design.

These sources still require naming/config extraction before copying. “Safe
candidate” does not mean blindly publish the current file.

## Owner-private by default

- Mission Control metadata and handoffs;
- hardware rollback files and saved donor profiles;
- generated binaries carrying local macOS HID authorization history;
- live state, logs, session tokens, caches, and LaunchAgent files;
- narrator configuration and all environment files;
- absolute home paths in generated Claude settings;
- owner persona art and voice metadata until the owner explicitly chooses a
  redistribution license;
- physical photos and personal build receipts unless deliberately selected for
  documentation.

No literal API credential value was observed in the source/config candidates
reviewed for this scaffold. The owner narrator config is already ignored, but
its voice metadata and external environment-file location are still private by
default.

## Release blockers found

1. The runtime assumes provider names `codex`, `claude`, and `grok` in several
   routing, light, CLI, and native-hotkey paths.
2. The current Claude settings file contains an owner-specific absolute path.
3. The supervisor assumes a Homebrew Codex location and a manually installed
   LaunchAgent.
4. The K07 USB IDs and protocol are compiled into native helpers rather than
   selected through an explicit hardware-profile build.
5. There is no safe initializer, generated hook/LaunchAgent templates,
   uninstaller, clean-account acceptance test, or dependency declaration.
6. Tests currently exercise owner personas and art. Public tests need generic
   fixtures before those assets can be excluded.
7. The existing multi-license text names `host/` but not the actual `bridge/`
   software directory; the public repository needs an unambiguous license map.

## Chosen boundary

The finished personal unit remains the reference implementation. This clean
project owns the public schema, doctor, installer, adapter API, generic assets,
and migrated core. Migration happens component by component with regression
tests and never by copying the whole personal worktree.

The first release should be honest and narrow: macOS plus the exact K07 H3.
“Bring your own agents” means three configurable identities/commands with
reviewed Codex, Claude, and Grok adapters and a non-approving command fallback.
Arbitrary third-party approval adapters are a later SDK, not an unsafe v0.1
promise.
