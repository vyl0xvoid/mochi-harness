"""Strict, secret-free configuration for a three-slot Mochi Harness."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import stat
from typing import Any, Mapping


SUPPORTED_HARDWARE_PROFILE = "sayo-k07-h3"
SUPPORTED_VENDOR_ID = 0x8089
SUPPORTED_PRODUCT_ID = 0x000E
SUPPORTED_CONTROLS_PROFILE = "seven-key-eyes-free-v1"
SUPPORTED_ADAPTERS = frozenset({"codex", "claude", "grok", "command"})
SUPPORTED_APPROVAL_ADAPTERS = frozenset(
    {"codex-app-server", "claude-hooks", "grok-hooks", "none"}
)
EXPECTED_APPROVAL_ADAPTER = {
    "codex": "codex-app-server",
    "claude": "claude-hooks",
    "grok": "grok-hooks",
    "command": "none",
}
_IDENTIFIER = re.compile(r"^[a-z0-9][a-z0-9_-]{0,31}$")
_COLOR = re.compile(r"^#[0-9A-F]{6}$")
_ENVIRONMENT = re.compile(r"^[A-Z][A-Z0-9_]{0,127}$")
_FORBIDDEN_KEY_PARTS = ("apikey", "api_key", "secret", "password", "token")
_CREDENTIAL_ARGUMENT = re.compile(
    r"(?:^|[-_])(api[-_]?key|secret|password|token)(?:$|[=:_-])|"
    r"authorization\s*:|bearer\s+",
    re.IGNORECASE,
)
_UNEXPANDED_ENVIRONMENT = re.compile(r"\$(?:[A-Za-z_][A-Za-z0-9_]*|\{[^}]+\})")


class HarnessConfigError(ValueError):
    """Raised when a harness config could target the wrong thing or leak data."""


class _DuplicateKeyError(ValueError):
    pass


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKeyError(f"duplicate JSON field: {key}")
        result[key] = value
    return result


def _mapping(value: object, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise HarnessConfigError(f"{label} must be an object")
    return value


def _only_keys(value: Mapping[str, Any], allowed: set[str], label: str) -> None:
    extras = sorted(set(value) - allowed)
    if extras:
        raise HarnessConfigError(f"{label} has unsupported fields: {', '.join(extras)}")


def _text(value: object, label: str, maximum: int) -> str:
    if not isinstance(value, str):
        raise HarnessConfigError(f"{label} must be text")
    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        raise HarnessConfigError(f"{label} contains a control character")
    cleaned = " ".join(value.split())
    if not cleaned or len(cleaned) > maximum:
        raise HarnessConfigError(f"{label} must contain 1-{maximum} characters")
    return cleaned


def _command_argument(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise HarnessConfigError(f"{label} must be text")
    if any(ord(character) == 0 for character in value):
        raise HarnessConfigError(f"{label} contains a null character")
    if not value or len(value) > 1024:
        raise HarnessConfigError(f"{label} must contain 1-1024 characters")
    if _CREDENTIAL_ARGUMENT.search(value):
        raise HarnessConfigError(
            f"{label} looks credential-bearing; use requiredEnvironment instead"
        )
    return value


def _path_text(value: object, label: str) -> str:
    if not isinstance(value, str):
        raise HarnessConfigError(f"{label} must be text")
    if any(ord(character) < 32 or ord(character) == 127 for character in value):
        raise HarnessConfigError(f"{label} contains a control character")
    if not value.strip() or len(value) > 1024:
        raise HarnessConfigError(f"{label} must contain 1-1024 characters")
    return value


def _identifier(value: object, label: str) -> str:
    result = _text(value, label, 32).lower()
    if not _IDENTIFIER.fullmatch(result):
        raise HarnessConfigError(f"{label} must be a safe lowercase identifier")
    return result


def _integer(value: object, label: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise HarnessConfigError(f"{label} must be an integer")
    return value


def _reject_embedded_secrets(value: object, path: str = "config") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized = str(key).replace("-", "_").lower()
            compact = normalized.replace("_", "")
            if any(
                part in normalized or part.replace("_", "") in compact
                for part in _FORBIDDEN_KEY_PARTS
            ):
                raise HarnessConfigError(
                    f"{path}.{key} is forbidden; store only environment-variable names"
                )
            _reject_embedded_secrets(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_embedded_secrets(child, f"{path}[{index}]")


@dataclass(frozen=True)
class AgentSlot:
    slot: int
    identifier: str
    display_name: str
    adapter: str
    approval_adapter: str
    command: tuple[str, ...]
    theme: str
    accent_color: str
    required_environment: tuple[str, ...]


@dataclass(frozen=True)
class HarnessConfig:
    source: Path
    product_name: str
    state_directory: Path
    hardware_profile: str
    vendor_id: int
    product_id: int
    controls_profile: str
    agents: tuple[AgentSlot, ...]

    def public_dict(self) -> dict[str, object]:
        """Return status-safe identity data without paths or launch details."""
        return {
            "productName": self.product_name,
            "hardware": {
                "profile": self.hardware_profile,
                "vendorId": self.vendor_id,
                "productId": self.product_id,
            },
            "controlsProfile": self.controls_profile,
            "agents": [
                {
                    "slot": agent.slot,
                    "id": agent.identifier,
                    "displayName": agent.display_name,
                    "adapter": agent.adapter,
                    "approvalAdapter": agent.approval_adapter,
                    "theme": agent.theme,
                    "accentColor": agent.accent_color,
                }
                for agent in self.agents
            ],
        }


def _agent(raw: object, index: int) -> AgentSlot:
    value = _mapping(raw, f"agents[{index}]")
    _only_keys(
        value,
        {
            "slot",
            "id",
            "displayName",
            "adapter",
            "approvalAdapter",
            "command",
            "theme",
            "accentColor",
            "requiredEnvironment",
        },
        f"agents[{index}]",
    )
    slot = _integer(value.get("slot"), f"agents[{index}].slot")
    if slot not in {1, 2, 3}:
        raise HarnessConfigError(f"agents[{index}].slot must be 1, 2, or 3")
    adapter = _identifier(value.get("adapter"), f"agents[{index}].adapter")
    if adapter not in SUPPORTED_ADAPTERS:
        raise HarnessConfigError(f"unsupported adapter: {adapter}")
    approval = _identifier(
        value.get("approvalAdapter"), f"agents[{index}].approvalAdapter"
    )
    if approval not in SUPPORTED_APPROVAL_ADAPTERS:
        raise HarnessConfigError(f"unsupported approval adapter: {approval}")
    expected = EXPECTED_APPROVAL_ADAPTER[adapter]
    if approval != expected:
        raise HarnessConfigError(
            f"{adapter} requires approvalAdapter {expected}, not {approval}"
        )

    raw_command = value.get("command")
    if not isinstance(raw_command, list) or not 1 <= len(raw_command) <= 64:
        raise HarnessConfigError(f"agents[{index}].command must contain 1-64 arguments")
    command = tuple(
        _command_argument(argument, f"agents[{index}].command[{position}]")
        for position, argument in enumerate(raw_command)
    )

    raw_environment = value.get("requiredEnvironment")
    if not isinstance(raw_environment, list):
        raise HarnessConfigError(
            f"agents[{index}].requiredEnvironment must be an array"
        )
    environment: list[str] = []
    for position, raw_name in enumerate(raw_environment):
        name = _text(
            raw_name,
            f"agents[{index}].requiredEnvironment[{position}]",
            128,
        )
        if not _ENVIRONMENT.fullmatch(name):
            raise HarnessConfigError(f"invalid environment-variable name: {name}")
        if name in environment:
            raise HarnessConfigError(f"duplicate environment-variable name: {name}")
        environment.append(name)

    accent = _text(value.get("accentColor"), f"agents[{index}].accentColor", 7).upper()
    if not _COLOR.fullmatch(accent):
        raise HarnessConfigError(
            f"agents[{index}].accentColor must look like #D00065"
        )
    return AgentSlot(
        slot=slot,
        identifier=_identifier(value.get("id"), f"agents[{index}].id"),
        display_name=_text(value.get("displayName"), f"agents[{index}].displayName", 64),
        adapter=adapter,
        approval_adapter=approval,
        command=command,
        theme=_identifier(value.get("theme"), f"agents[{index}].theme"),
        accent_color=accent,
        required_environment=tuple(environment),
    )


def _config_source(path: Path | str, require_owner_only: bool) -> Path:
    candidate = Path(path).expanduser()
    try:
        information = candidate.lstat()
    except OSError as error:
        raise HarnessConfigError(f"unable to inspect harness config: {error}") from error
    if stat.S_ISLNK(information.st_mode):
        raise HarnessConfigError("harness config must not be a symbolic link")
    if not stat.S_ISREG(information.st_mode):
        raise HarnessConfigError("harness config must be a regular file")
    if require_owner_only:
        if information.st_uid != os.getuid():
            raise HarnessConfigError("harness config must be owned by the current user")
        if stat.S_IMODE(information.st_mode) & 0o077:
            raise HarnessConfigError("harness config permissions must be owner-only (0600)")
    return candidate.resolve()


def _state_directory(value: object, require_owner_only: bool) -> Path:
    state_text = _path_text(value, "product.stateDirectory")
    expanded = os.path.expandvars(state_text)
    if _UNEXPANDED_ENVIRONMENT.search(expanded):
        raise HarnessConfigError("product.stateDirectory contains an unset variable")
    candidate = Path(expanded).expanduser()
    if require_owner_only and candidate.is_symlink():
        raise HarnessConfigError("product.stateDirectory must not be a symbolic link")
    result = candidate.resolve()
    home = Path.home().resolve()
    try:
        relative = result.relative_to(home)
    except ValueError as error:
        raise HarnessConfigError(
            "product.stateDirectory must resolve inside the current user's home"
        ) from error
    if not relative.parts:
        raise HarnessConfigError("product.stateDirectory must not be the home directory")
    if require_owner_only and result.exists():
        information = result.stat()
        if not stat.S_ISDIR(information.st_mode):
            raise HarnessConfigError("product.stateDirectory must be a directory")
        if information.st_uid != os.getuid():
            raise HarnessConfigError(
                "product.stateDirectory must be owned by the current user"
            )
        if stat.S_IMODE(information.st_mode) & 0o077:
            raise HarnessConfigError(
                "product.stateDirectory permissions must be owner-only (0700)"
            )
    return result


def load_config(
    path: Path | str, *, require_owner_only: bool = True
) -> HarnessConfig:
    source = _config_source(path, require_owner_only)
    try:
        document = json.loads(
            source.read_text(encoding="utf-8"), object_pairs_hook=_unique_object
        )
    except _DuplicateKeyError as error:
        raise HarnessConfigError(str(error)) from error
    except (OSError, json.JSONDecodeError) as error:
        raise HarnessConfigError(f"unable to read harness config: {error}") from error
    root = _mapping(document, "config")
    _reject_embedded_secrets(root)
    _only_keys(
        root,
        {"version", "product", "hardware", "controlsProfile", "agents"},
        "config",
    )
    if root.get("version") != 1:
        raise HarnessConfigError("config version must be 1")

    product = _mapping(root.get("product"), "product")
    _only_keys(product, {"name", "stateDirectory"}, "product")
    product_name = _text(product.get("name"), "product.name", 64)
    state_directory = _state_directory(
        product.get("stateDirectory"), require_owner_only
    )

    hardware = _mapping(root.get("hardware"), "hardware")
    _only_keys(
        hardware,
        {"profile", "vendorId", "productId", "keyCount", "display"},
        "hardware",
    )
    profile = _identifier(hardware.get("profile"), "hardware.profile")
    if profile != SUPPORTED_HARDWARE_PROFILE:
        raise HarnessConfigError(f"unsupported hardware profile: {profile}")
    vendor_id = _integer(hardware.get("vendorId"), "hardware.vendorId")
    product_id = _integer(hardware.get("productId"), "hardware.productId")
    if (vendor_id, product_id) != (SUPPORTED_VENDOR_ID, SUPPORTED_PRODUCT_ID):
        raise HarnessConfigError(
            "sayo-k07-h3 must use exact USB IDs 0x8089/0x000e"
        )
    if _integer(hardware.get("keyCount"), "hardware.keyCount") != 7:
        raise HarnessConfigError("sayo-k07-h3 must declare exactly seven keys")
    display = _mapping(hardware.get("display"), "hardware.display")
    _only_keys(display, {"width", "height"}, "hardware.display")
    if (
        _integer(display.get("width"), "hardware.display.width") != 160
        or _integer(display.get("height"), "hardware.display.height") != 80
    ):
        raise HarnessConfigError("sayo-k07-h3 display must be exactly 160 x 80")

    controls = _identifier(root.get("controlsProfile"), "controlsProfile")
    if controls != SUPPORTED_CONTROLS_PROFILE:
        raise HarnessConfigError(
            f"unsupported controls profile: {controls}; the safety map is not free-form"
        )
    raw_agents = root.get("agents")
    if not isinstance(raw_agents, list) or len(raw_agents) != 3:
        raise HarnessConfigError("agents must contain exactly three physical slots")
    agents = tuple(_agent(raw, index) for index, raw in enumerate(raw_agents))
    if {agent.slot for agent in agents} != {1, 2, 3}:
        raise HarnessConfigError("agent slots must be exactly 1, 2, and 3")
    if len({agent.identifier for agent in agents}) != 3:
        raise HarnessConfigError("agent ids must be unique")
    ordered = tuple(sorted(agents, key=lambda agent: agent.slot))
    return HarnessConfig(
        source=source,
        product_name=product_name,
        state_directory=state_directory,
        hardware_profile=profile,
        vendor_id=vendor_id,
        product_id=product_id,
        controls_profile=controls,
        agents=ordered,
    )
