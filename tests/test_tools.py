import asyncio
from pathlib import Path
from types import SimpleNamespace

import pytest

from obsidian_mcp import server

EXPECTED_TOOLS = {
    "append_note",
    "delete_note",
    "list_folders",
    "list_notes",
    "move_note",
    "read_note",
    "search_content",
    "search_filename",
    "vault_info",
    "write_note",
}


def test_mcp_exposes_expected_tools():
    tools = asyncio.run(server.mcp.list_tools())

    assert {tool.name for tool in tools} == EXPECTED_TOOLS


def test_path_resolution_stays_inside_vault(config):
    assert server._resolve("") == config.vault
    assert server._resolve("Folder/Alpha.md") == config.vault / "Folder" / "Alpha.md"

    with pytest.raises(ValueError, match="Path escapes the vault"):
        server._resolve("../outside.md")


def test_path_resolution_rejects_symlink_escape(config, tmp_path):
    outside = tmp_path.parent / "outside"
    outside.mkdir(exist_ok=True)
    (config.vault / "escape").symlink_to(outside, target_is_directory=True)

    with pytest.raises(ValueError, match="Path escapes the vault"):
        server._resolve("escape/note.md")


def test_vault_info_and_listing(config):
    assert server.vault_info() == {
        "vault_path": str(config.vault),
        "read_only": False,
        "markdown_files": 1,
    }
    assert server.list_notes(folder="Folder", recursive=True, limit=10) == ["Folder/Alpha.md"]
    assert server.list_folders(folder="", recursive=False) == ["Folder"]


def test_read_write_append_move_and_delete(config):
    created = server.write_note(path="New/Note", content="First")
    assert created == {"path": "New/Note.md", "bytes": 5}
    assert server.read_note(path="New/Note") == "First"

    appended = server.append_note(path="New/Note.md", content="Second")
    assert appended["bytes"] == len("First\n\nSecond")
    assert server.read_note(path="New/Note") == "First\n\nSecond"

    moved = server.move_note(src="New/Note", dst="Moved/Renamed")
    assert moved == {"from": "New/Note.md", "to": "Moved/Renamed.md"}
    assert server.delete_note(path="Moved/Renamed") == {"deleted": "Moved/Renamed.md"}


def test_write_refuses_overwrite(config):
    with pytest.raises(FileExistsError, match="overwrite=true"):
        server.write_note(path="Folder/Alpha", content="replacement")


def test_write_tools_are_blocked_in_read_only_mode(config):
    server.CONFIG = server.Config(vault=config.vault, read_only=True)

    with pytest.raises(PermissionError, match="read-only mode"):
        server.write_note(path="Blocked", content="content")
    with pytest.raises(PermissionError, match="read-only mode"):
        server.append_note(path="Blocked", content="content")
    with pytest.raises(PermissionError, match="read-only mode"):
        server.delete_note(path="Folder/Alpha")
    with pytest.raises(PermissionError, match="read-only mode"):
        server.move_note(src="Folder/Alpha", dst="Moved")


def test_filename_search_supports_text_and_regex(config):
    assert server.search_filename(pattern="alpha") == ["Folder/Alpha.md"]
    assert server.search_filename(pattern=r"Folder/.+\.md", regex=True) == ["Folder/Alpha.md"]


def test_content_search_python_fallback(monkeypatch, config):
    monkeypatch.setattr(server.shutil, "which", lambda name: None)

    result = server.search_content(query="second", folder="Folder")

    assert result == [{"path": "Folder/Alpha.md", "line": 2, "snippet": "Second line"}]


def test_content_search_uses_ripgrep(monkeypatch, config):
    monkeypatch.setattr(server.shutil, "which", lambda name: "/usr/bin/rg")
    monkeypatch.setattr(
        server.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(
            stdout=f"{config.vault}/Folder/Alpha.md:2:Second line\n"
        ),
    )

    result = server.search_content(query="Second", folder="Folder", case_sensitive=True)

    assert result == [{"path": "Folder/Alpha.md", "line": 2, "snippet": "Second line"}]


def test_missing_note_and_folder_errors(config):
    with pytest.raises(FileNotFoundError, match="Note not found"):
        server.read_note(path="Missing")
    with pytest.raises(ValueError, match="Not a folder"):
        server.list_notes(folder="Folder/Alpha.md")


def test_markdown_suffix_is_preserved(config):
    path = Path(config.vault / "Beta.markdown")

    assert server._ensure_md(path) == path
