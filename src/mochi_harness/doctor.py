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


def _command_available(command: str, base_directory: Path) -> bool:
    expanded = Path(command).expanduser()
    if expanded.is_absolute() or "/" in command:
        if not expanded.is_absolute():
            expanded = base_directory / expanded
        return expanded.is_file() and os.access(expanded, os.X_OK)
    return shutil.which(command) is not None


def _device_present(vendor_id: int, product_id: int) -> tuple[str, str]:
    hidutil = Path("/usr/bin/hidutil")
    if not hidutil.is_file():
        return "error", "hidutil is unavailable"
    try:
        result = subprocess.run(
            (str(hidutil), "list"),
            check=False,
            capture_output=True,
            text=True,
            timeout=4,
        )
    except (OSError, subprocess.SubprocessError) as error:
        return "error", f"HID inspection failed: {error}"
    if result.returncode != 0:
        return "error", f"hidutil list exited with status {result.returncode}"
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
    return ("ok" if found else "warning"), (
        "supported USB VID/PID is visible"
        if found
        else f"0x{vendor_id:04x}/0x{product_id:04x} is not currently visible"
    )


def run_doctor(
    config_path: Path,
    *,
    allow_public_config: bool = False,
    require_hardware: bool = False,
) -> list[Check]:
    checks: list[Check] = []
    try:
        config = load_config(
            config_path, require_owner_only=not allow_public_config
        )
    except HarnessConfigError as error:
        return [Check("config", "error", str(error))]
    checks.append(
        Check(
            "config",
            "warning" if allow_public_config else "ok",
            (
                "public example accepted for validation only; runtime requires 0600"
                if allow_public_config
                else "strict validator, ownership, permissions, and secret guard passed"
            ),
        )
    )

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
        available = _command_available(executable, config.source.parent)
        checks.append(
            Check(
                f"agent:{agent.identifier}",
                "ok" if available else ("warning" if allow_public_config else "error"),
                (
                    f"{agent.adapter} command found: {executable}"
                    if available
                    else (
                        f"example command is not installed on this validation host: "
                        f"{executable}"
                        if allow_public_config
                        else f"{agent.adapter} command missing: {executable}"
                    )
                ),
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

    hardware_status, detail = _device_present(config.vendor_id, config.product_id)
    if require_hardware and hardware_status == "warning":
        hardware_status = "error"
        detail = f"{detail}; hardware is required for this preflight"
    checks.append(Check("hardware", hardware_status, detail))
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
            "warning",
            (
                "config profile is locked and doctor performed no writes; "
                "runtime and physical safety were not exercised"
            ),
        )
    )
    return checks


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument(
        "--allow-public-config",
        action="store_true",
        help="validate a public example without treating it as a runtime config",
    )
    parser.add_argument(
        "--require-hardware",
        action="store_true",
        help="return an error when the supported USB device is absent",
    )
    args = parser.parse_args(argv)
    checks = run_doctor(
        args.config,
        allow_public_config=args.allow_public_config,
        require_hardware=args.require_hardware,
    )
    if args.as_json:
        print(json.dumps([asdict(check) for check in checks], indent=2))
    else:
        labels = {"ok": "OK", "warning": "WARN", "error": "ERROR"}
        for check in checks:
            print(f"[{labels[check.status]}] {check.name}: {check.detail}")
    return 1 if any(check.status == "error" for check in checks) else 0


if __name__ == "__main__":
    raise SystemExit(main())
