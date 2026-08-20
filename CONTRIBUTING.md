# Contributing

Issues and pull requests are welcome. Keep changes focused and never include
real vault content, personal filesystem paths, credentials, private hostnames,
or private network details in reports, fixtures, or logs.

## Development setup

Requirements:

- Python 3.11 or newer
- [uv](https://docs.astral.sh/uv/)

```bash
uv sync --locked --all-groups
uv run ruff check .
uv run pytest --cov=obsidian_mcp --cov-fail-under=85
uv build
```

Tests must use temporary directories and must not require or inspect a real
Obsidian vault.

## Pull requests

Describe user-visible behavior and security implications. Add tests for
behavior changes, preserve the ten-tool MCP contract unless a change is
explicitly breaking, and update the README or changelog when appropriate.

CI validates Python 3.11 through 3.14 and scans the repository for secrets.
