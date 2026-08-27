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
- Match hardware by an exact supported profile before any vendor command.
- Before a device write, save the complete original records, verify RAM
  read-back, require an acknowledged save, then verify again after power loss.

## Reports

Do not include API keys, session tokens, private prompts, terminal contents, or
personal paths in an issue. Describe the hardware profile, host version,
adapter, expected behavior, and a sanitized reproduction. Approval-boundary or
device-write reports should be treated as high priority.
