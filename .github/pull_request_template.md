## Summary

Describe the problem and the outcome of this change.

## Validation

- [ ] `uv run ruff check .`
- [ ] `uv run ruff format --check .`
- [ ] `uv run pytest --cov=obsidian_mcp --cov-fail-under=85`
- [ ] `uv build`

## Security and privacy

- [ ] Tests use temporary directories and do not access a real Obsidian vault.
- [ ] The change introduces no note content, personal paths, credentials, or private network details.
- [ ] I documented changes to vault access, write behavior, or the MCP tool contract.
