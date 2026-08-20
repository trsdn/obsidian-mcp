# obsidian-mcp

- A filesystem-based [MCP](https://modelcontextprotocol.io/) server for Obsidian
vaults, built with [FastMCP](https://github.com/PrefectHQ/fastmcp). It reads and
writes Markdown directly, so the Obsidian application and a REST plugin are not
required.

- Runs locally over stdio.
- Keeps every resolved tool path inside the configured vault.
- Supports read-only operation for browse and search clients.
- Uses ripgrep when available and falls back to pure Python search.

> [!IMPORTANT]
> An MCP client can read every Markdown note in the configured vault. Start
> with `OBSIDIAN_READ_ONLY=1` unless the client must create, change, move, or
> delete notes.

## Tools

| Tool | Purpose |
| --- | --- |
| `vault_info` | Return vault path, access mode, and Markdown file count |
| `list_notes` | List Markdown files under a folder |
| `list_folders` | List subfolders |
| `read_note` | Read a note |
| `write_note` | Create or overwrite a note |
| `append_note` | Append content, creating the note if necessary |
| `delete_note` | Delete a note |
| `move_note` | Rename or move a note within the vault |
| `search_filename` | Match against vault-relative paths |
| `search_content` | Search note bodies with text or a regular expression |

The four write tools are disabled when `OBSIDIAN_READ_ONLY=1`.

## Requirements

- Python 3.11 or newer
- [uv](https://docs.astral.sh/uv/)
- Optional: [ripgrep](https://github.com/BurntSushi/ripgrep)

## Install

```bash
git clone https://github.com/trsdn/obsidian-mcp.git
cd obsidian-mcp
uv sync --locked --no-dev
```

`OBSIDIAN_VAULT_PATH` is required and must point to an existing directory:

```bash
export OBSIDIAN_VAULT_PATH="/path/to/your/Obsidian vault"
export OBSIDIAN_READ_ONLY=1
uv run obsidian-mcp
```

## Client configuration

Add a stdio server to your MCP client and replace both example paths:

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

Claude Desktop uses the same server definition under the `mcpServers` key
instead of `servers` and does not need the `type` field.

## Development

```bash
uv sync --locked --all-groups
uv run ruff check .
uv run pytest --cov=obsidian_mcp --cov-fail-under=85
uv build
```

Tests use temporary directories and never require a real Obsidian vault.

## Security

- Keep the server local and only configure it in MCP clients you trust.
- Use a dedicated vault or `OBSIDIAN_READ_ONLY=1` to reduce impact.
- All tool paths are resolved and checked against the configured vault root,
  including paths that contain symbolic links.
- Note content returned to an MCP client may be sent to that client's model
  provider. Apply the provider's data-handling policy to the entire vault.
- See [SECURITY.md](SECURITY.md) for vulnerability reporting and the supported
  security boundary.

## License

MIT
