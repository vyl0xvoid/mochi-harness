"""Public configuration boundary for Mochi Harness."""

from .config import AgentSlot, HarnessConfig, HarnessConfigError, load_config

__all__ = ["AgentSlot", "HarnessConfig", "HarnessConfigError", "load_config"]
__version__ = "0.0.2"
