"""Filesystem-based MCP server for an Obsidian vault.

Exposes a small, sharp toolset over the local vault on disk. No Obsidian
process or REST plugin required. Designed for Claude Desktop / any MCP
client over stdio.

Configuration via environment variables:
    OBSIDIAN_VAULT_PATH   Absolute path to the vault root (required).
    OBSIDIAN_READ_ONLY    If "1"/"true", disables write/delete/move tools.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

from fastmcp import FastMCP
from pydantic import Field

MD_SUFFIXES = {".md", ".markdown"}


@dataclass(frozen=True)
class Config:
    vault: Path
    read_only: bool


def _load_config() -> Config:
    raw = os.environ.get("OBSIDIAN_VAULT_PATH", "").strip()
    if not raw:
        raise RuntimeError("Missing required env var: OBSIDIAN_VAULT_PATH")
    vault = Path(raw).expanduser().resolve()
    if not vault.is_dir():
        raise RuntimeError(f"Vault path is not a directory: {vault}")
    read_only = os.environ.get("OBSIDIAN_READ_ONLY", "").lower() in {"1", "true", "yes"}
    return Config(vault=vault, read_only=read_only)


CONFIG: Config | None = None
mcp = FastMCP("obsidian-mcp")


def get_config() -> Config:
    global CONFIG
    if CONFIG is None:
        CONFIG = _load_config()
    return CONFIG


# --- path safety ----------------------------------------------------------


def _resolve(rel: str) -> Path:
    """Resolve a vault-relative path and ensure it stays inside the vault."""
    config = get_config()
    if not rel or rel.strip() in {"", "."}:
        return config.vault
    candidate = (config.vault / rel).resolve()
    try:
        candidate.relative_to(config.vault)
    except ValueError as exc:
        raise ValueError(f"Path escapes the vault: {rel}") from exc
    return candidate


def _ensure_md(path: Path) -> Path:
    if path.suffix.lower() not in MD_SUFFIXES:
        return path.with_suffix(".md")
    return path


def _check_writable() -> None:
    if get_config().read_only:
        raise PermissionError("Server is in read-only mode (OBSIDIAN_READ_ONLY=1).")


def _rel(path: Path) -> str:
    return str(path.relative_to(get_config().vault))


# --- tools ----------------------------------------------------------------


@mcp.tool
def vault_info() -> dict:
    """Return basic information about the configured vault."""
    config = get_config()
    md_files = sum(1 for _ in config.vault.rglob("*.md"))
    return {
        "vault_path": str(config.vault),
        "read_only": config.read_only,
        "markdown_files": md_files,
    }


@mcp.tool
def list_notes(
    folder: Annotated[str, Field(description="Vault-relative folder. Empty for root.")] = "",
    recursive: bool = True,
    limit: Annotated[int, Field(ge=1, le=5000)] = 1000,
) -> list[str]:
    """List markdown notes (vault-relative paths) under a folder."""
    base = _resolve(folder)
    if not base.is_dir():
        raise ValueError(f"Not a folder: {folder}")
    iterator = base.rglob("*.md") if recursive else base.glob("*.md")
    return sorted(_rel(p) for p in iterator)[:limit]


@mcp.tool
def list_folders(
    folder: Annotated[str, Field(description="Vault-relative folder. Empty for root.")] = "",
    recursive: bool = False,
) -> list[str]:
    """List subfolders under a folder."""
    base = _resolve(folder)
    if not base.is_dir():
        raise ValueError(f"Not a folder: {folder}")
    iterator = (
        (p for p in base.rglob("*") if p.is_dir())
        if recursive
        else (p for p in base.iterdir() if p.is_dir())
    )
    return sorted(_rel(p) for p in iterator if not p.name.startswith("."))


@mcp.tool
def read_note(path: str) -> str:
    """Read a markdown note by vault-relative path."""
    target = _ensure_md(_resolve(path))
    if not target.is_file():
        raise FileNotFoundError(f"Note not found: {path}")
    return target.read_text(encoding="utf-8")


@mcp.tool
def write_note(
    path: str,
    content: str,
    overwrite: bool = False,
) -> dict:
    """Create or overwrite a note. Creates parent folders as needed."""
    _check_writable()
    target = _ensure_md(_resolve(path))
    if target.exists() and not overwrite:
        raise FileExistsError(f"Note exists, pass overwrite=true: {_rel(target)}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return {"path": _rel(target), "bytes": len(content.encode("utf-8"))}


@mcp.tool
def append_note(path: str, content: str, separator: str = "\n\n") -> dict:
    """Append content to an existing note (creates it if missing)."""
    _check_writable()
    target = _ensure_md(_resolve(path))
    target.parent.mkdir(parents=True, exist_ok=True)
    existing = target.read_text(encoding="utf-8") if target.exists() else ""
    new = existing + (separator if existing else "") + content
    target.write_text(new, encoding="utf-8")
    return {"path": _rel(target), "bytes": len(new.encode("utf-8"))}


@mcp.tool
def delete_note(path: str) -> dict:
    """Delete a note. Refuses to delete folders."""
    _check_writable()
    target = _ensure_md(_resolve(path))
    if not target.is_file():
        raise FileNotFoundError(f"Note not found: {path}")
    target.unlink()
    return {"deleted": _rel(target)}


@mcp.tool
def move_note(src: str, dst: str, overwrite: bool = False) -> dict:
    """Rename or move a note within the vault."""
    _check_writable()
    src_path = _ensure_md(_resolve(src))
    dst_path = _ensure_md(_resolve(dst))
    if not src_path.is_file():
        raise FileNotFoundError(f"Source note not found: {src}")
    if dst_path.exists() and not overwrite:
        raise FileExistsError(f"Destination exists: {_rel(dst_path)}")
    dst_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src_path), str(dst_path))
    return {"from": _rel(src_path), "to": _rel(dst_path)}


@mcp.tool
def search_filename(
    pattern: Annotated[str, Field(description="Substring or regex against note path.")],
    regex: bool = False,
    limit: Annotated[int, Field(ge=1, le=1000)] = 200,
) -> list[str]:
    """Find notes whose vault-relative path matches a pattern."""
    paths = (_rel(p) for p in get_config().vault.rglob("*.md"))
    if regex:
        rx = re.compile(pattern, re.IGNORECASE)
        matches = (p for p in paths if rx.search(p))
    else:
        needle = pattern.lower()
        matches = (p for p in paths if needle in p.lower())
    return sorted(matches)[:limit]


@mcp.tool
def search_content(
    query: Annotated[str, Field(description="Text or regex to search for in note bodies.")],
    folder: str = "",
    regex: bool = False,
    case_sensitive: bool = False,
    max_results: Annotated[int, Field(ge=1, le=500)] = 100,
) -> list[dict]:
    """Search note contents. Uses ripgrep when available, otherwise pure Python."""
    base = _resolve(folder)
    if not base.is_dir():
        raise ValueError(f"Not a folder: {folder}")

    rg = shutil.which("rg")
    if rg:
        cmd = [
            rg,
            "--no-heading",
            "--with-filename",
            "--line-number",
            "--max-count",
            "5",
            "--glob",
            "*.md",
        ]
        if not case_sensitive:
            cmd.append("--ignore-case")
        if regex:
            cmd.extend(["--regexp", query])
        else:
            cmd.extend(["--fixed-strings", query])
        cmd.append(str(base))
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=20)
        except subprocess.TimeoutExpired:
            return [{"error": "ripgrep timed out"}]
        results: list[dict] = []
        for line in proc.stdout.splitlines():
            try:
                file_part, lineno, snippet = line.split(":", 2)
            except ValueError:
                continue
            try:
                rel = _rel(Path(file_part))
            except ValueError:
                continue
            results.append({"path": rel, "line": int(lineno), "snippet": snippet.strip()})
            if len(results) >= max_results:
                break
        return results

    # Pure-Python fallback
    flags = 0 if case_sensitive else re.IGNORECASE
    matcher = re.compile(query if regex else re.escape(query), flags)
    results = []
    for path in base.rglob("*.md"):
        try:
            for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if matcher.search(line):
                    results.append({"path": _rel(path), "line": i, "snippet": line.strip()})
                    if len(results) >= max_results:
                        return results
        except (OSError, UnicodeDecodeError):
            continue
    return results


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
