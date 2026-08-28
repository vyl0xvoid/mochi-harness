from __future__ import annotations

import json
import os
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

    def _load_document(
        self, document: dict[str, object], *, preserve_state: bool = False
    ):
        with tempfile.TemporaryDirectory(
            prefix=".mochi-harness-", dir=Path.home()
        ) as temporary:
            if not preserve_state:
                product = document["product"]
                assert isinstance(product, dict)
                product["stateDirectory"] = str(Path(temporary) / "state")
            path = Path(temporary) / "config.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            path.chmod(0o600)
            return load_config(path)

    def test_public_example_is_valid_and_has_exact_three_slots(self) -> None:
        config = load_config(EXAMPLE, require_owner_only=False)
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

    def test_agent_ids_are_unique(self) -> None:
        document = self._document()
        agents = document["agents"]
        assert isinstance(agents, list)
        assert isinstance(agents[0], dict) and isinstance(agents[1], dict)
        agents[1]["id"] = agents[0]["id"]
        with self.assertRaisesRegex(HarnessConfigError, "agent ids must be unique"):
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

    def test_public_status_omits_paths_commands_and_environment_names(self) -> None:
        document = self._document()
        agents = document["agents"]
        assert isinstance(agents, list) and isinstance(agents[2], dict)
        agents[2]["command"] = ["/opt/private-marker/bin/agent"]
        agents[2]["requiredEnvironment"] = ["PRIVATE_MARKER_TOKEN_NAME"]
        config = self._load_document(document)
        public = config.public_dict()
        serialized = json.dumps(public)
        self.assertNotIn("source", public)
        self.assertNotIn("stateDirectory", public)
        public_agents = public["agents"]
        assert isinstance(public_agents, list)
        for agent in public_agents:
            assert isinstance(agent, dict)
            self.assertNotIn("command", agent)
            self.assertNotIn("requiredEnvironment", agent)
        self.assertNotIn("private-marker", serialized)
        self.assertNotIn("PRIVATE_MARKER_TOKEN_NAME", serialized)

    def test_duplicate_json_object_keys_are_rejected(self) -> None:
        raw = EXAMPLE.read_text(encoding="utf-8").replace(
            '"version": 1', '"version": 999,\n  "version": 1', 1
        )
        with tempfile.TemporaryDirectory(
            prefix=".mochi-harness-", dir=Path.home()
        ) as temporary:
            path = Path(temporary) / "config.json"
            path.write_text(raw, encoding="utf-8")
            path.chmod(0o600)
            with self.assertRaisesRegex(HarnessConfigError, "duplicate JSON field"):
                load_config(path)

    def test_runtime_config_permissions_must_be_owner_only(self) -> None:
        document = self._document()
        with tempfile.TemporaryDirectory(
            prefix=".mochi-harness-", dir=Path.home()
        ) as temporary:
            product = document["product"]
            assert isinstance(product, dict)
            product["stateDirectory"] = str(Path(temporary) / "state")
            path = Path(temporary) / "config.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            path.chmod(0o644)
            with self.assertRaisesRegex(HarnessConfigError, "owner-only"):
                load_config(path)

    def test_symbolic_link_config_is_rejected(self) -> None:
        document = self._document()
        with tempfile.TemporaryDirectory(
            prefix=".mochi-harness-", dir=Path.home()
        ) as temporary:
            product = document["product"]
            assert isinstance(product, dict)
            product["stateDirectory"] = str(Path(temporary) / "state")
            target = Path(temporary) / "target.json"
            target.write_text(json.dumps(document), encoding="utf-8")
            target.chmod(0o600)
            link = Path(temporary) / "config.json"
            os.symlink(target, link)
            with self.assertRaisesRegex(HarnessConfigError, "symbolic link"):
                load_config(link)

    def test_state_directory_must_stay_inside_current_home(self) -> None:
        document = self._document()
        product = document["product"]
        assert isinstance(product, dict)
        product["stateDirectory"] = "/tmp/shared-mochi-state"
        with self.assertRaisesRegex(HarnessConfigError, "inside the current user's home"):
            self._load_document(document, preserve_state=True)

    def test_existing_state_directory_must_be_owner_only(self) -> None:
        document = self._document()
        with tempfile.TemporaryDirectory(
            prefix=".mochi-harness-", dir=Path.home()
        ) as temporary:
            directory = Path(temporary)
            state_directory = directory / "state"
            state_directory.mkdir()
            state_directory.chmod(0o755)
            product = document["product"]
            assert isinstance(product, dict)
            product["stateDirectory"] = str(state_directory)
            path = directory / "config.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            path.chmod(0o600)
            with self.assertRaisesRegex(HarnessConfigError, "permissions"):
                load_config(path)

    def test_existing_state_directory_must_not_be_a_symbolic_link(self) -> None:
        document = self._document()
        with tempfile.TemporaryDirectory(
            prefix=".mochi-harness-", dir=Path.home()
        ) as temporary:
            directory = Path(temporary)
            target = directory / "real-state"
            target.mkdir(mode=0o700)
            state_link = directory / "state"
            os.symlink(target, state_link)
            product = document["product"]
            assert isinstance(product, dict)
            product["stateDirectory"] = str(state_link)
            path = directory / "config.json"
            path.write_text(json.dumps(document), encoding="utf-8")
            path.chmod(0o600)
            with self.assertRaisesRegex(HarnessConfigError, "symbolic link"):
                load_config(path)


if __name__ == "__main__":
    unittest.main()
