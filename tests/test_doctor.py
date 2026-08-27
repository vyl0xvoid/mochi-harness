from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from mochi_harness.doctor import _device_present  # noqa: E402


class DoctorTests(unittest.TestCase):
    def test_hardware_ids_must_appear_on_the_same_device_row(self) -> None:
        output = "\n".join(
            (
                "VendorID ProductID Product",
                "0x8089 0x1234 First Device",
                "0x9999 0xe Second Device",
            )
        )
        completed = subprocess.CompletedProcess(
            args=("/usr/bin/hidutil", "list"),
            returncode=0,
            stdout=output,
            stderr="",
        )
        with patch("mochi_harness.doctor.subprocess.run", return_value=completed):
            present, _ = _device_present(0x8089, 0x000E)
        self.assertFalse(present)

    def test_exact_hardware_row_is_accepted(self) -> None:
        output = "\n".join(
            (
                "VendorID ProductID Product",
                "0x8089 0xe SayoDevice K07 H3",
            )
        )
        completed = subprocess.CompletedProcess(
            args=("/usr/bin/hidutil", "list"),
            returncode=0,
            stdout=output,
            stderr="",
        )
        with patch("mochi_harness.doctor.subprocess.run", return_value=completed):
            present, _ = _device_present(0x8089, 0x000E)
        self.assertTrue(present)


if __name__ == "__main__":
    unittest.main()
