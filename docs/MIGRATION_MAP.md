# Runtime migration map

The accepted reference implementation remains untouched while its reusable
parts move into this project behind public interfaces. Every slice lands with
generic fixtures and regression tests before the next slice begins.

| Public component | Reference responsibility | Extraction rule | Status |
| --- | --- | --- | --- |
| `config` | fixed provider, path, hardware, and color constants | strict versioned config, duplicate rejection, owner-only runtime source, redacted public view | hardened scaffold |
| `core.approvals` | exact request queue and bounded summaries | remove owner/provider display names; retain exact responder identity | queued |
| `core.sessions` | named sessions, exact TTY focus/submit/exit | make slots configurable; retain owner-process verification | queued |
| `adapters.codex` | App Server proxy | generate local endpoint/token state; never place tokens in URLs or status | queued |
| `adapters.claude` | permission and elicitation hooks | generate settings/hooks from install path | queued |
| `adapters.grok` | guarded pre-tool hook | generate token-bound hook; ignore ordinary sessions | queued |
| `adapters.command` | generic terminal launcher | launch/focus only; no approval authority | queued |
| `ui.cards` | identity, terminal, and approval cards | use generic licensed fixture art | queued |
| `voice` | provider-aware narration | optional plugin; environment names only | queued |
| `hardware.k07` | input, 160×80 display, and runtime LEDs | build locally for exact profile; never ship accepted local binaries | queued |
| `hardware.configure` | guarded record repair | backup, narrow write, read-back, power-cycle, read-back | queued |
| `service.macos` | supervisor and LaunchAgent | generate paths at install time | queued |
| `cli` | setup and maintenance scripts | expose `init`, `doctor`, `install`, `test`, `uninstall` | safe init + doctor scaffolded |

## Slice order

1. Move pure approval/summary logic and its generic tests.
2. Move exact session lifecycle behavior, including whole-window close
   verification and occupied-port restart refusal.
3. Introduce the command adapter and generic terminal cards.
4. Add reviewed Codex, Claude, and Grok adapters one at a time.
5. Move the K07 native transport behind the exact hardware profile.
6. Generate local service and hook files from templates.
7. Implement guarded hardware configuration and rollback.
8. Pass the complete public physical acceptance on a clean macOS account.

No slice may import owner state, generated settings, live logs, tokens,
rollback files, authorized binaries, or unlicensed identity media.
