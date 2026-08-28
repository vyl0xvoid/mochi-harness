# Contributing

Mochi Harness is pre-alpha. The first release target is intentionally narrow:
macOS and the exact SayoDevice K07 H3 hardware profile.

## Local checks

```sh
make check
make package-check
make doctor
```

`make check` is hardware-independent. `make doctor` is read-only and may report
warnings when the supported controller or an example agent command is absent.
`make package-check` builds, inspects, installs, and smoke-tests a disposable
wheel and may download the declared build backend.

## Safety expectations

- Never approve, deny, submit, focus, or terminate whichever application is
  merely frontmost.
- Preserve exact request, session-token, process-owner, and Terminal-TTY
  boundaries.
- Keep one-tap exit impossible.
- Never add credentials, personal paths, live state, hardware backups, or
  generated service files to the repository.
- Keep public/status output free of config paths, state paths, launch commands,
  and environment-variable names.
- Treat owner-only config permissions and state-directory containment as part
  of the command-execution boundary.
- Put new hardware behind an exact profile with a reversible, verified write
  procedure.
- Add regression tests for every approval, process, device-write, or recovery
  behavior change.

Read `SECURITY.md`, `docs/ARCHITECTURE.md`, and
`docs/PHYSICAL_ACCEPTANCE.md` before changing consequential controls.
