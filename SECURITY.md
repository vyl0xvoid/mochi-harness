# Security policy

Mochi Harness can approve agent actions and terminate terminal processes, so
its safe target identity matters more than convenience.

## Non-negotiable behavior

- Never send approval, Return, denial, or termination to the frontmost app.
- Bind actions to an exact registered session token, owner process identity,
  and Terminal TTY.
- Keep one-tap exit impossible.
- Fail closed when an approval screen, alert light, provider boundary, or exact
  responder cannot be synchronized.
- Never print, cache, return, or commit credential values.
- Never expose config paths, state paths, launch commands, or environment names
  through public/status serialization.
- Runtime config must be a real owner-owned `0600` file, and runtime state must
  stay in an owner-only directory inside that user's home.
- Match hardware by an exact supported profile before any vendor command.
- Before a device write, save the complete original records, verify RAM
  read-back, require an acknowledged save, then verify again after power loss.

## Reports

Use the repository's **Security → Report a vulnerability** flow for a private
report. Do not put an approval-boundary or device-write vulnerability in a
public issue.

Do not include API keys, session tokens, private prompts, terminal contents, or
personal paths. Describe the hardware profile, host version, adapter, expected
behavior, and a sanitized reproduction. Approval-boundary or device-write
reports are treated as high priority.

The project is pre-alpha and has no supported runtime release yet. Security
reports about the published config, initializer, doctor, packaging, or future
runtime design are still welcome.
