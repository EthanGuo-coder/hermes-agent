"""Tests for the `hermes memory status` CLI command output.

Covers:
- Built-in label clarifies it refers to the MEMORY.md/USER.md store, not the
  whole memory subsystem (issue #18404).
"""

import io
import sys

from argparse import Namespace
from unittest.mock import patch


def _capture_status(config):
    """Run cmd_status with a stubbed config and capture stdout."""
    import hermes_cli.config as cli_config
    from hermes_cli.memory_setup import cmd_status

    buf = io.StringIO()
    old = sys.stdout
    sys.stdout = buf
    try:
        with patch.object(cli_config, "load_config", return_value=config):
            with patch(
                "hermes_cli.memory_setup._get_available_providers",
                return_value=[],
            ):
                cmd_status(Namespace())
    finally:
        sys.stdout = old
    return buf.getvalue()


class TestMemoryStatusBuiltinLabel:
    """The `Built-in:` line must name the actual store (MEMORY.md/USER.md)."""

    def test_builtin_label_names_md_files_with_provider(self):
        """With a pluggable provider configured, the line must disambiguate
        the built-in MEMORY.md/USER.md store from the memory subsystem."""
        out = _capture_status({"memory": {"provider": "mnemosyne"}})
        assert "MEMORY.md" in out and "USER.md" in out
        assert "Built-in:  always active" not in out

    def test_builtin_label_names_md_files_without_provider(self):
        """Same disambiguation when no external provider is set."""
        out = _capture_status({"memory": {"provider": ""}})
        assert "MEMORY.md" in out and "USER.md" in out
        assert "Built-in:  always active" not in out
