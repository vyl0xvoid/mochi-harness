# Physical acceptance contract

This is the release gate for the first supported build: macOS and an exact
SayoDevice K07 H3. It describes required behavior; commands that depend on the
future runtime or guarded configurator are not claimed as implemented yet.

## Before any write

- `make check` passes.
- `mochi-harness-doctor --require-hardware` identifies the host, agent commands,
  and supported USB VID/PID and exits successfully.
- The intended device records are read and saved to an owner-only rollback
  file with a digest.
- The proposed byte changes name exact records and leave every other control
  unchanged.
- The person at the device explicitly confirms the write step.

## Hardware persistence

- The write is acknowledged and read back.
- The controller is unplugged long enough to lose power, then reconnected.
- The exact records are read back again before the host service starts.
- Rollback is tested or its exact safe procedure is displayed and retained.

## Daily interaction

- Reconnect lands on the neutral home screen.
- Each of three selector keys shows its configured identity and `0/0` when
  empty.
- Dial double-press or long-hold opens a named session for the active slot.
- A new session appears once as `1/1`; additional sessions have stable names
  and positions.
- Dial rotation stays inside the active slot. Dial press focuses the exact
  registered Terminal TTY.
- Push-to-talk uses the configured dictation path.
- Narration reports the selected session through its configured voice or a
  declared safe fallback.

## Consequential controls

- Ordinary submit sends Return only to the exact selected registered TTY.
- A structured request displays a bounded human summary before any approval is
  armed.
- Exact Yes, the waiting slot, and global narration turn visibly alert only
  after the request card and lights synchronize.
- Selecting another slot never reveals or resolves the waiting request.
- Returning to the waiting slot restores and re-arms only that exact request.
- Yes responds once to the exact request. It is a no-op without an armed card
  or selected session.
- Guarded-key single tap and hold do nothing.
- Guarded-key double tap denies only the exact synchronized request.
- Guarded-key triple tap closes only the exact selected registered session,
  including its one-tab Terminal window, and verifies the TTY is gone.

## Recovery

- Resolving the final request restores all alert lights to idle.
- A missing display stream redraws home instead of leaving the factory page.
- Unplug/replug preserves the safe hardware signals and restarts the neutral
  home without a browser configurator.
- A service restart refuses to overlap occupied local ports.
- Uninstall removes generated services and hooks without deleting identity
  packs, rollback records, agent CLIs, or unrelated Terminal windows.

The acceptance record must distinguish automated results from what a person
actually saw, heard, and pressed on the physical controller.
