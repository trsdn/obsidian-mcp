from pathlib import Path

import pytest

from obsidian_mcp import server


def test_import_does_not_require_vault(monkeypatch):
    monkeypatch.delenv("OBSIDIAN_VAULT_PATH", raising=False)

    with pytest.raises(RuntimeError, match="Missing required env var: OBSIDIAN_VAULT_PATH"):
        server.get_config()


def test_config_loads_environment_and_caches(monkeypatch, vault: Path):
    monkeypatch.setenv("OBSIDIAN_VAULT_PATH", str(vault))
    monkeypatch.setenv("OBSIDIAN_READ_ONLY", "true")

    config = server.get_config()

    assert config.vault == vault.resolve()
    assert config.read_only is True
    assert server.get_config() is config


def test_config_rejects_missing_directory(monkeypatch, tmp_path: Path):
    missing = tmp_path / "missing"
    monkeypatch.setenv("OBSIDIAN_VAULT_PATH", str(missing))

    with pytest.raises(RuntimeError, match="Vault path is not a directory"):
        server.get_config()
