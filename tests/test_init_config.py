from __future__ import annotations

from importlib import resources
from pathlib import Path
import os
import stat
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from mochi_harness.init_config import (  # noqa: E402
    HarnessInitError,
    initialize_config,
)
from mochi_harness.config import load_config  # noqa: E402


class InitConfigTests(unittest.TestCase):
    def test_bundled_example_and_schema_match_public_copies(self) -> None:
        package = resources.files("mochi_harness.resources")
        self.assertEqual(
            package.joinpath("harness.example.json").read_text(encoding="utf-8"),
            (ROOT / "config" / "harness.example.json").read_text(encoding="utf-8"),
        )
        self.assertEqual(
            package.joinpath("harness.schema.json").read_text(encoding="utf-8"),
            (ROOT / "schemas" / "harness.schema.json").read_text(encoding="utf-8"),
        )

    def test_initializer_creates_0600_config_and_never_overwrites(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix=".mochi-harness-init-", dir=Path.home()
        ) as temporary:
            destination = Path(temporary) / "harness.json"
            created = initialize_config(destination)
            self.assertEqual(created, destination.resolve())
            self.assertEqual(stat.S_IMODE(created.stat().st_mode), 0o600)
            self.assertEqual(load_config(created).controls_profile, "seven-key-eyes-free-v1")
            with self.assertRaisesRegex(HarnessInitError, "refusing to overwrite"):
                initialize_config(destination)

    def test_initializer_rejects_non_private_parent(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix=".mochi-harness-init-", dir=Path.home()
        ) as temporary:
            directory = Path(temporary)
            directory.chmod(0o755)
            with self.assertRaisesRegex(HarnessInitError, "owner-only"):
                initialize_config(directory / "harness.json")

    def test_initializer_rejects_paths_outside_home(self) -> None:
        with self.assertRaisesRegex(HarnessInitError, "inside the current home"):
            initialize_config(Path("/private/tmp/mochi-harness-outside-home.json"))

    def test_initializer_rejects_symbolic_link_destinations(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix=".mochi-harness-init-", dir=Path.home()
        ) as temporary:
            directory = Path(temporary)
            target = directory / "target.json"
            link = directory / "harness.json"
            os.symlink(target, link)
            with self.assertRaisesRegex(HarnessInitError, "symbolic link"):
                initialize_config(link)


if __name__ == "__main__":
    unittest.main()
