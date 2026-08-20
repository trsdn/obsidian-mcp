from pathlib import Path

import pytest

from obsidian_mcp import server


@pytest.fixture(autouse=True)
def reset_config():
    server.CONFIG = None
    yield
    server.CONFIG = None


@pytest.fixture
def vault(tmp_path: Path) -> Path:
    (tmp_path / "Folder").mkdir()
    (tmp_path / "Folder" / "Alpha.md").write_text("Alpha content\nSecond line", encoding="utf-8")
    (tmp_path / "Beta.markdown").write_text("Beta content", encoding="utf-8")
    return tmp_path


@pytest.fixture
def config(vault: Path) -> server.Config:
    value = server.Config(vault=vault, read_only=False)
    server.CONFIG = value
    return value
