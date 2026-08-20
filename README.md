# obsidian-mcp

[![CI](https://github.com/trsdn/obsidian-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/trsdn/obsidian-mcp/actions/workflows/ci.yml)
[![Secret scan](https://github.com/trsdn/obsidian-mcp/actions/workflows/secret-scan.yml/badge.svg)](https://github.com/trsdn/obsidian-mcp/actions/workflows/secret-scan.yml)
[![Release](https://img.shields.io/github/v/release/trsdn/obsidian-mcp)](https://github.com/trsdn/obsidian-mcp/releases/latest)
[![Python](https://img.shields.io/badge/Python-3.11--3.14-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/github/license/trsdn/obsidian-mcp)](LICENSE)

A focused Model Context Protocol server that gives local AI clients controlled
filesystem access to an Obsidian vault. It runs over stdio, works without the
Obsidian application or a REST plugin, and supports read-only operation.

**Use it to:** search notes, read Markdown, browse folders, and optionally
create, update, move, or delete notes from any stdio-capable MCP client.

## Why Obsidian MCP?

- **Local by design:** no HTTP server, API token, or Obsidian plugin.
- **Vault-contained paths:** resolved paths and symbolic links cannot escape
  the configured vault root.
- **Read-only mode:** one environment variable disables every write tool.
- **Small surface area:** ten predictable tools backed by ordinary Markdown
  files.
- **Fast search:** uses ripgrep when available, with a pure-Python fallback.

> [!CAUTION]
> The configured MCP client can read every Markdown note in the selected
> vault. Start with `OBSIDIAN_READ_ONLY=1`, and review your model provider's
> data-handling policy before exposing sensitive notes.

## Quick Start

Requirements: Python 3.11 or newer and
[uv](https://docs.astral.sh/uv/getting-started/installation/).

```bash
git clone https://github.com/trsdn/obsidian-mcp.git
cd obsidian-mcp
uv sync --locked --no-dev

export OBSIDIAN_VAULT_PATH="/path/to/your/Obsidian vault"
export OBSIDIAN_READ_ONLY=1
uv run obsidian-mcp
```

The server communicates over stdio and is normally started by an MCP client,
not from an interactive terminal.

## Client Setup

Replace `/path/to/obsidian-mcp` and `/path/to/your/Obsidian vault` in the
examples below.

### VS Code

Add the server to `.vscode/mcp.json`:

```json
{
  "servers": {
    "obsidian": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/obsidian-mcp",
        "run",
        "obsidian-mcp"
      ],
      "env": {
        "OBSIDIAN_VAULT_PATH": "/path/to/your/Obsidian vault",
        "OBSIDIAN_READ_ONLY": "1"
      }
    }
  }
}
```

### Claude Desktop

Add the server under `mcpServers` in Claude Desktop's configuration:

```json
{
  "mcpServers": {
    "obsidian": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/obsidian-mcp",
        "run",
        "obsidian-mcp"
      ],
      "env": {
        "OBSIDIAN_VAULT_PATH": "/path/to/your/Obsidian vault",
        "OBSIDIAN_READ_ONLY": "1"
      }
    }
  }
}
```

Restart the client after changing its MCP configuration.

## Configuration

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `OBSIDIAN_VAULT_PATH` | Yes | None | Absolute path to an existing Obsidian vault |
| `OBSIDIAN_READ_ONLY` | No | `0` | Set to `1`, `true`, or `yes` to disable write tools |

Read-only mode blocks `write_note`, `append_note`, `move_note`, and
`delete_note`. All paths passed to tools are relative to the configured vault.

## Available Tools

| Tool | Access | Purpose |
| --- | --- | --- |
| `vault_info` | Read | Return vault path, access mode, and Markdown file count |
| `list_notes` | Read | List Markdown files under a folder |
| `list_folders` | Read | List subfolders |
| `read_note` | Read | Read a note |
| `search_filename` | Read | Match text or a regular expression against note paths |
| `search_content` | Read | Search note bodies with text or a regular expression |
| `write_note` | Write | Create or overwrite a note |
| `append_note` | Write | Append content, creating the note when necessary |
| `move_note` | Write | Rename or move a note within the vault |
| `delete_note` | Write | Delete a note |

## Security Model

Obsidian MCP trusts the local process that starts it. It does not provide
authentication, user-level authorization, sandboxing, or network controls.
Path validation keeps MCP tool operations inside the selected vault, but it
cannot restrict another local process that already has filesystem access.

For safer operation:

1. Use only MCP clients you trust.
2. Start with `OBSIDIAN_READ_ONLY=1`.
3. Consider a dedicated vault for AI-assisted workflows.
4. Protect the vault with normal operating-system permissions and backups.

See [SECURITY.md](SECURITY.md) for the full security policy and private
vulnerability reporting process.

## Development

```bash
uv sync --locked --all-groups
uv run ruff check .
uv run ruff format --check .
uv run pytest --cov=obsidian_mcp --cov-fail-under=85
uv build
```

Tests use temporary directories and never require a real Obsidian vault.
CI runs on Python 3.11, 3.12, 3.13, and 3.14.

## Project

- [Releases](https://github.com/trsdn/obsidian-mcp/releases)
- [Changelog](CHANGELOG.md)
- [Contributing](CONTRIBUTING.md)
- [Code of conduct](CODE_OF_CONDUCT.md)
- [Security policy](SECURITY.md)
- [Issue tracker](https://github.com/trsdn/obsidian-mcp/issues)

Licensed under the [MIT License](LICENSE).
