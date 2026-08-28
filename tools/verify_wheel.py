"""Verify that a Mochi Harness wheel contains real code and starter resources."""

from __future__ import annotations

import configparser
from pathlib import Path
import sys
from zipfile import ZipFile


REQUIRED = {
    "mochi_harness/__init__.py",
    "mochi_harness/config.py",
    "mochi_harness/doctor.py",
    "mochi_harness/init_config.py",
    "mochi_harness/resources/__init__.py",
    "mochi_harness/resources/harness.example.json",
    "mochi_harness/resources/harness.schema.json",
}
ROOT = Path(__file__).resolve().parents[1]


def expected_version() -> str:
    parser = configparser.ConfigParser()
    parser.read(ROOT / "setup.cfg", encoding="utf-8")
    return parser.get("metadata", "version")


def verify_wheel(path: Path) -> None:
    with ZipFile(path) as archive:
        names = set(archive.namelist())
        missing = sorted(REQUIRED - names)
        if missing:
            raise RuntimeError("wheel is missing: " + ", ".join(missing))
        metadata_names = [
            name for name in names if name.endswith(".dist-info/METADATA")
        ]
        if len(metadata_names) != 1:
            raise RuntimeError("wheel must contain exactly one METADATA file")
        metadata = archive.read(metadata_names[0]).decode("utf-8")
        if "Name: mochi-harness\n" not in metadata:
            raise RuntimeError("wheel metadata has the wrong project name")
        if f"Version: {expected_version()}\n" not in metadata:
            raise RuntimeError("wheel metadata has the wrong project version")
        if "Name: UNKNOWN" in metadata or "Version: 0.0.0" in metadata:
            raise RuntimeError("wheel contains legacy UNKNOWN metadata")


def main(argv: list[str] | None = None) -> int:
    arguments = sys.argv[1:] if argv is None else argv
    if len(arguments) != 1:
        print("usage: verify_wheel.py PATH.whl")
        return 2
    try:
        verify_wheel(Path(arguments[0]))
    except (OSError, RuntimeError) as error:
        print(f"ERROR: {error}")
        return 1
    print("Wheel contents and metadata are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
