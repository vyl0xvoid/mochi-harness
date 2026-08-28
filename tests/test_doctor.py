from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from mochi_harness.doctor import _device_present, run_doctor  # noqa: E402


EXAMPLE = ROOT / "config" / "harness.example.json"


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
            status, _ = _device_present(0x8089, 0x000E)
        self.assertEqual(status, "warning")

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
            status, detail = _device_present(0x8089, 0x000E)
        self.assertEqual(status, "ok")
        self.assertIn("VID/PID", detail)

    def test_failed_hidutil_never_reports_stale_stdout_as_present(self) -> None:
        completed = subprocess.CompletedProcess(
            args=("/usr/bin/hidutil", "list"),
            returncode=1,
            stdout="0x8089 0xe SayoDevice K07 H3\n",
            stderr="inspection failed",
        )
        with patch("mochi_harness.doctor.subprocess.run", return_value=completed):
            status, detail = _device_present(0x8089, 0x000E)
        self.assertEqual(status, "error")
        self.assertIn("status 1", detail)

    def test_strict_preflight_promotes_missing_hardware_to_error(self) -> None:
        with patch(
            "mochi_harness.doctor._device_present",
            return_value=("warning", "supported VID/PID is absent"),
        ):
            checks = run_doctor(
                EXAMPLE,
                allow_public_config=True,
                require_hardware=True,
            )
        hardware = next(check for check in checks if check.name == "hardware")
        self.assertEqual(hardware.status, "error")

    def test_safety_result_is_explicitly_config_only(self) -> None:
        with patch(
            "mochi_harness.doctor._device_present",
            return_value=("warning", "supported VID/PID is absent"),
        ):
            checks = run_doctor(EXAMPLE, allow_public_config=True)
        safety = next(check for check in checks if check.name == "safety")
        self.assertEqual(safety.status, "warning")
        self.assertIn("not exercised", safety.detail)


if __name__ == "__main__":
    unittest.main()
