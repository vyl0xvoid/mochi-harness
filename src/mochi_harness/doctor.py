"""Read-only environment doctor for the Mochi Harness public scaffold."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys

from .config import HarnessConfigError, load_config


@dataclass(frozen=True)
class Check:
    name: str
    status: str
    detail: str


def _command_available(command: str) -> bool:
    expanded = Path(command).expanduser()
    if expanded.is_absolute() or "/" in command:
        return expanded.is_file() and os.access(expanded, os.X_OK)
    return shutil.which(command) is not None


def _device_present(vendor_id: int, product_id: int) -> tuple[bool, str]:
    hidutil = Path("/usr/bin/hidutil")
    if not hidutil.is_file():
        return False, "hidutil is unavailable"
    try:
        result = subprocess.run(
            (str(hidutil), "list"),
            check=False,
            capture_output=True,
            text=True,
            timeout=4,
        )
    except (OSError, subprocess.SubprocessError) as error:
        return False, f"HID inspection failed: {error}"
    found = False
    for row in result.stdout.splitlines():
        columns = row.split()
        if len(columns) < 2:
            continue
        try:
            row_vendor = int(columns[0], 0)
            row_product = int(columns[1], 0)
        except ValueError:
            continue
        if (row_vendor, row_product) == (vendor_id, product_id):
            found = True
            break
    return found, (
        "exact USB identity is visible"
        if found
        else f"0x{vendor_id:04x}/0x{product_id:04x} is not currently visible"
    )


def run_doctor(config_path: Path) -> list[Check]:
    checks: list[Check] = []
    try:
        config = load_config(config_path)
    except HarnessConfigError as error:
        return [Check("config", "error", str(error))]
    checks.append(Check("config", "ok", "strict schema and secret guard passed"))

    if platform.system() == "Darwin":
        checks.append(Check("host", "ok", f"macOS {platform.mac_ver()[0] or 'detected'}"))
    else:
        checks.append(Check("host", "error", "version 0.1 supports macOS only"))
    if sys.version_info >= (3, 9):
        checks.append(Check("python", "ok", platform.python_version()))
    else:
        checks.append(Check("python", "error", "Python 3.9 or newer is required"))

    for agent in config.agents:
        executable = agent.command[0]
        available = _command_available(executable)
        checks.append(
            Check(
                f"agent:{agent.identifier}",
                "ok" if available else "error",
                f"{agent.adapter} command {'found' if available else 'missing'}: {executable}",
            )
        )
        missing = [
            name for name in agent.required_environment if not os.environ.get(name)
        ]
        checks.append(
            Check(
                f"environment:{agent.identifier}",
                "warning" if missing else "ok",
                (
                    "missing names: " + ", ".join(missing)
                    if missing
                    else "all declared environment variables are present"
                ),
            )
        )

    present, detail = _device_present(config.vendor_id, config.product_id)
    checks.append(Check("hardware", "ok" if present else "warning", detail))
    checks.append(
        Check(
            "compiler",
            "ok" if shutil.which("clang") else "warning",
            (
                "clang found"
                if shutil.which("clang")
                else "clang is needed to build the macOS helpers"
            ),
        )
    )
    checks.append(
        Check(
            "safety",
            "ok",
            "seven-key-eyes-free-v1 is locked; doctor performed no writes",
        )
    )
    return checks


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args(argv)
    checks = run_doctor(args.config)
    if args.as_json:
        print(json.dumps([asdict(check) for check in checks], indent=2))
    else:
        labels = {"ok": "OK", "warning": "WARN", "error": "ERROR"}
        for check in checks:
            print(f"[{labels[check.status]}] {check.name}: {check.detail}")
    return 1 if any(check.status == "error" for check in checks) else 0


if __name__ == "__main__":
    raise SystemExit(main())
