# Changelog

## 0.0.2 — 2026-08-27

- redact paths, launch commands, and environment names from public config
  serialization;
- reject duplicate JSON keys, symlink configs, insecure runtime-config
  permissions, unsafe state locations, and insecure existing state folders;
- add an owner-only, no-overwrite initializer with bundled example and schema;
- make HID inspection failures fatal, label VID/PID checks precisely, add a
  strict hardware preflight, and stop claiming runtime safety was exercised;
- restore wheel compatibility with Apple's older pip/setuptools path and verify
  wheel contents, installation, and entry points;
- expand config, initializer, doctor, and packaging regressions;
- add pinned GitHub CI, Dependabot configuration, and private vulnerability
  reporting guidance.

## 0.0.1 — 2026-08-27

- publish the clean configuration, doctor, architecture, safety contract, and
  migration scaffold without owner-specific Mochi Mini state.
