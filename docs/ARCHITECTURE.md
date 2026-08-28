# Mochi Harness architecture

## Product boundary

The reference behavior is a seven-control, eyes-free terminal dashboard. Three
keys select agent groups. The dial navigates and focuses exact named sessions.
One key narrates state. One context key sends Return or exact Yes. One guarded
key is single no-op, double exact No, and triple exact exit. Push-to-talk remains
an independent input path.

The public harness separates five concerns:

```text
seven-key hardware profile
          │
          ▼
native input / display / light transport
          │
          ▼
session registry ── exact TTY + owner lifecycle
          │
          ├── adapter: Codex App Server
          ├── adapter: Claude hooks
          ├── adapter: Grok hooks
          └── adapter: command (no implicit approvals)
          │
          ▼
identity pack (name, art, accent) + optional voice pack
```

Hardware behavior and approval safety are profiles, not arbitrary user macros.
Agent identities and launch commands are configuration.

## Adapter contract

Each adapter must eventually expose the same small host interface:

- `launch(session)`: start the configured command with an opaque harness token;
- `connect(session_id, token)`: bind a live agent to its registered exact TTY;
- `normalize_approval(event)`: produce a bounded human action summary without
  leaking commands, paths, usernames, or credentials;
- `respond(request_id, allow|deny)`: answer only the exact synchronized request;
- `disconnect(session_id)`: remove live routing without adopting another tab.

The generic command adapter launches and focuses sessions but has no approval
authority until a separately reviewed adapter is installed.

## Hardware profiles

Version 0.1 supports one profile: `sayo-k07-h3`, exact USB VID/PID
`0x8089/0x000e`, seven keys, one rotary encoder, and a 160×80 display. Native
vendor protocol code belongs behind that profile. A future open-serial profile
for custom Mochi Micro hardware must implement the same semantic controls
without pretending to share the K07 transport.

No profile may write a connected device merely because the product name looks
similar. A write flow must resolve exact identity, read all targets, create a
rollback file, modify declared bytes only, verify RAM, save once, require power
loss, and verify flash.

## Installation design

The installer should be generated from resolved local paths rather than
shipping reference-owner-specific files:

1. discover Python, agent commands, compiler, and supported USB identity;
2. create an owner-owned `0600` config and owner-only state directory inside
   the current user's home;
3. build native helpers locally with warnings as errors;
4. generate Claude/Grok hook files with the installed absolute path;
5. generate a per-user LaunchAgent from a template;
6. guide macOS Automation/Input Monitoring permissions without bypassing them;
7. run the guarded hardware profile configurator only as a separate confirmed
   step;
8. run an automated doctor and a short physical acceptance script.

The published initializer now safely creates the generic config and refuses to
overwrite it. The published doctor validates config ownership and permissions,
uses a precise VID/PID result, and offers a strict hardware-required preflight.
Those commands remain scaffolding: they do not install or run the future host
service.

Uninstall must unload the LaunchAgent and remove generated state without
touching user art, rollback backups, agent CLIs, or unrelated Terminal windows.

## Release milestones

### v0.1 — same hardware, public setup

- migrate the proven bridge and native K07 helpers behind this config loader;
- replace hard-coded provider names with three configured slot identities while
  retaining reviewed built-in adapters;
- add starter art with an explicit license and an identity-pack importer;
- add generated LaunchAgent and hook templates;
- add `init`, `doctor`, `configure-hardware`, `test`, and `uninstall` commands;
- reproduce the complete physical reference acceptance and automated suite on a
  clean macOS user account.

### v0.2 — community adapters

- documented adapter SDK and subprocess protocol;
- multiple agents using the same underlying CLI;
- optional TTS providers and offline voices;
- signed release artifacts and upgrade-safe state migrations.

### v0.3 — open hardware transport

- serial/HID profile for Mochi Micro hardware;
- macOS and Linux host transports;
- no dependency on a vendor configurator for startup art or saved controls.
