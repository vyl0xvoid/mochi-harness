"""Create an owner-only Mochi Harness configuration from the bundled example."""

from __future__ import annotations

import argparse
from importlib import resources
import os
from pathlib import Path
import stat


DEFAULT_CONFIG = Path("~/Library/Application Support/Mochi Harness/harness.json")


class HarnessInitError(RuntimeError):
    """Raised when a safe initial configuration cannot be created."""


def _inside_home(path: Path) -> tuple[Path, Path]:
    home = Path.home().resolve()
    resolved = path.expanduser().resolve()
    try:
        relative = resolved.relative_to(home)
    except ValueError as error:
        raise HarnessInitError("config path must resolve inside the current home") from error
    if not relative.parts:
        raise HarnessInitError("config path must not be the home directory")
    return resolved, relative


def _private_directory(directory: Path) -> None:
    directory.mkdir(parents=True, mode=0o700, exist_ok=True)
    information = directory.lstat()
    if stat.S_ISLNK(information.st_mode) or not stat.S_ISDIR(information.st_mode):
        raise HarnessInitError("config parent must be a real directory")
    if information.st_uid != os.getuid():
        raise HarnessInitError("config parent must be owned by the current user")
    if stat.S_IMODE(information.st_mode) & 0o077:
        raise HarnessInitError("config parent permissions must be owner-only (0700)")


def initialize_config(output: Path) -> Path:
    candidate = output.expanduser()
    if candidate.is_symlink():
        raise HarnessInitError("config path must not be a symbolic link")
    destination, _ = _inside_home(candidate)
    _private_directory(destination.parent)
    if destination.exists() or destination.is_symlink():
        raise HarnessInitError("refusing to overwrite an existing config")

    payload = (
        resources.files("mochi_harness.resources")
        .joinpath("harness.example.json")
        .read_bytes()
    )
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    created = False
    try:
        descriptor = os.open(destination, flags, 0o600)
        created = True
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    except OSError as error:
        if created:
            destination.unlink(missing_ok=True)
        raise HarnessInitError(f"unable to create owner-only config: {error}") from error
    return destination


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    args = parser.parse_args(argv)
    try:
        destination = initialize_config(args.config)
    except HarnessInitError as error:
        print(f"ERROR: {error}")
        return 1
    _, relative = _inside_home(destination)
    print(f"Created owner-only config at ~/{relative}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
