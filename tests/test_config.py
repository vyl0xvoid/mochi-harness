from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from mochi_harness.config import HarnessConfigError, load_config  # noqa: E402


EXAMPLE = ROOT / "config" / "harness.example.json"


class HarnessConfigTests(unittest.TestCase):
    def _document(self) -> dict[str, object]:
        return json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def _load_document(self, document: dict[str, object]):
        with tempfile.TemporaryDirectory(prefix="mochi-harness-") as temporary:
            path = Path(temporary) / "config.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            return load_config(path)

    def test_public_example_is_valid_and_has_exact_three_slots(self) -> None:
        config = load_config(EXAMPLE)
        self.assertEqual(config.hardware_profile, "sayo-k07-h3")
        self.assertEqual(config.vendor_id, 0x8089)
        self.assertEqual(config.product_id, 0x000E)
        self.assertEqual([agent.slot for agent in config.agents], [1, 2, 3])
        self.assertEqual(config.agents[0].approval_adapter, "codex-app-server")

    def test_wrong_hardware_identity_is_rejected(self) -> None:
        document = self._document()
        hardware = document["hardware"]
        assert isinstance(hardware, dict)
        hardware["vendorId"] = 1234
        with self.assertRaisesRegex(HarnessConfigError, "exact USB IDs"):
            self._load_document(document)

    def test_embedded_secret_fields_are_rejected(self) -> None:
        document = self._document()
        document["apiKey"] = "do-not-store-this"
        with self.assertRaisesRegex(HarnessConfigError, "forbidden"):
            self._load_document(document)

    def test_adapter_cannot_claim_an_incompatible_approval_protocol(self) -> None:
        document = self._document()
        agents = document["agents"]
        assert isinstance(agents, list) and isinstance(agents[0], dict)
        agents[0]["approvalAdapter"] = "claude-hooks"
        with self.assertRaisesRegex(HarnessConfigError, "requires approvalAdapter"):
            self._load_document(document)

    def test_slot_ids_and_physical_positions_are_unique(self) -> None:
        document = self._document()
        agents = document["agents"]
        assert isinstance(agents, list) and isinstance(agents[1], dict)
        agents[1]["slot"] = 1
        with self.assertRaisesRegex(HarnessConfigError, "exactly 1, 2, and 3"):
            self._load_document(document)

    def test_command_arguments_keep_intentional_whitespace(self) -> None:
        document = self._document()
        agents = document["agents"]
        assert isinstance(agents, list) and isinstance(agents[2], dict)
        agents[2]["command"] = ["/bin/zsh", "-lc", "print 'two  spaces'"]
        config = self._load_document(document)
        self.assertEqual(config.agents[2].command[2], "print 'two  spaces'")

    def test_credential_bearing_command_arguments_are_rejected(self) -> None:
        document = self._document()
        agents = document["agents"]
        assert isinstance(agents, list) and isinstance(agents[2], dict)
        agents[2]["command"] = ["tool", "--api-key=do-not-store-this"]
        with self.assertRaisesRegex(HarnessConfigError, "requiredEnvironment"):
            self._load_document(document)


if __name__ == "__main__":
    unittest.main()
