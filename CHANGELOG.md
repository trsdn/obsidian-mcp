# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]

### Added

- Dependabot configuration for grouped weekly `uv` and GitHub Actions updates.

### Security

- Upgraded locked dependencies to resolve all open Dependabot alerts, including
  `cryptography` 50.0.0, `mcp` 1.29.0, `starlette` 1.6.0, `joserfc` 1.7.4,
  `pyjwt` 2.13.0, `python-multipart` 0.0.32, `pydantic-settings` 2.15.0, and
  `idna` 3.19.

### Changed

- Raised the development `pytest` requirement to `>=9.0.3,<10.0`.

## [0.1.1] - 2026-08-20

### Added

- Root MIT license file, complete Python package metadata, and project links.
- GitHub issue forms, pull request template, code of conduct, and repository
  discovery metadata.
- Release workflow that attaches wheel and source distributions to GitHub
  releases.

### Changed

- Reworked the README around a concise quick start, separate client setup,
  configuration reference, tool access levels, and a clearer security model.

## [0.1.0] - 2026-08-20

### Added

- Local stdio MCP server with ten tools for listing, reading, searching,
  creating, updating, moving, and deleting Markdown notes.
- Vault-bound path resolution, including protection against escaping symbolic
  links.
- Optional read-only mode that blocks all write tools.
- Temporary-vault tests, Python 3.11 through 3.14 CI, and secret scanning.
- Security policy, contribution guide, and portable client configuration.

[Unreleased]: https://github.com/trsdn/obsidian-mcp/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/trsdn/obsidian-mcp/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/trsdn/obsidian-mcp/releases/tag/v0.1.0
