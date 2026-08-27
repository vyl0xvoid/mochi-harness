# Mochi Harness

Mochi Harness is the open-source, bring-your-own-agents version of the working
Mochi Mini controller: three agent selectors, named terminal sessions, dial
navigation, exact approvals, spoken summaries, screen identities, alert lights,
and a deliberately guarded No/exit key.

This repository is a clean extraction scaffold. It defines the public config,
safety boundary, read-only doctor, adapter contract, and release plan without
changing or publishing the owner-specific Mochi Mini installation. The proven
runtime migrates here only after every personal path, persona asset, voice
profile, backup, and machine-specific permission is separated.

## Intended setup

1. Buy a supported seven-key controller. Version 0.1 targets the SayoDevice
   K07 H3 used by the physical reference build.
2. Install the host package on a Mac.
3. Copy `config/harness.example.json` to an owner-only local config.
4. Put an agent command in each of the three physical slots. Built-in adapters
   cover Codex, Claude, and Grok; a command adapter is the generic fallback.
5. Add original 160×80 identity art and optional voice metadata. Credentials
   are supplied only through named environment variables.
6. Run the read-only doctor.
7. Run the guarded hardware configurator. It must back up every key record,
   change only the declared device, read changes back before saving, and verify
   them again after unplug/replug.
8. Complete the physical acceptance script before enabling approvals.

The target user experience is the same as the accepted Mochi Mini build. The
configuration is different; the safety contract is not.

## Safety contract

- Provider keys select groups; they never send Escape or Control-C.
- The dial changes or focuses an exact registered terminal, never whichever
  window happens to be frontmost.
- Submit accepts only the exact synchronized request or sends Return to the
  exact selected registered TTY.
- The guarded key is one-tap no-op, double-tap exact No, and triple-tap exact
  selected-terminal exit.
- Hardware flashing is never part of ordinary startup and never runs without a
  complete rollback record plus post-replug verification.
- Secret-bearing fields and common credential-bearing command arguments are
  rejected. Config stores environment-variable names only.

## Validate the scaffold

```sh
make check
make doctor
```

The doctor is read-only. It does not install services, change hotkeys, flash a
device, open an agent, or request an approval.

## Project map

```text
CONTRIBUTING.md         safety and development expectations
config/                 safe example configuration
schemas/                public JSON Schema
src/mochi_harness/      config validator and read-only doctor
docs/ARCHITECTURE.md    runtime and adapter boundaries
docs/EXTRACTION_AUDIT.md private/public migration receipt
docs/MIGRATION_MAP.md   component-by-component extraction order
docs/PHYSICAL_ACCEPTANCE.md clean-device release gate
tests/                  config and safety regressions
```

Status: foundation ready; runtime extraction and installer are the next
milestone. See `docs/ARCHITECTURE.md` for the bounded path to a v0.1 release.
