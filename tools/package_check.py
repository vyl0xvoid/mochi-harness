"""Build, inspect, install, and smoke-test a wheel in disposable directories."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import venv

from verify_wheel import verify_wheel


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="mochi-harness-package-") as temporary:
        directory = Path(temporary)
        wheel_directory = directory / "dist"
        subprocess.run(
            (
                sys.executable,
                "-m",
                "pip",
                "wheel",
                "--no-deps",
                "--wheel-dir",
                str(wheel_directory),
                str(ROOT),
            ),
            check=True,
        )
        wheels = tuple(wheel_directory.glob("*.whl"))
        if len(wheels) != 1:
            raise RuntimeError("package build must produce exactly one wheel")
        verify_wheel(wheels[0])

        environment = directory / "venv"
        venv.EnvBuilder(with_pip=True).create(environment)
        python = environment / "bin" / "python"
        scripts = environment / "bin"
        subprocess.run(
            (
                str(python),
                "-m",
                "pip",
                "install",
                "--no-index",
                str(wheels[0]),
            ),
            check=True,
        )
        subprocess.run((str(scripts / "mochi-harness-doctor"), "--help"), check=True)
        subprocess.run((str(scripts / "mochi-harness-init"), "--help"), check=True)
    print("Wheel build, contents, installation, and entry points are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
