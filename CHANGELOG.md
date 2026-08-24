# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]

### Fixed

- A manual `workflow_dispatch` run of the release workflow no longer attempts to
  publish. PyPI rejects re-uploading an existing version, so dispatching without
  a new tag always failed at the upload step. `publish` and `github-release` are
  now restricted to tag pushes, which turns a manual run into a safe dry run of
  the build and quality gates.

## [0.1.2] - 2026-08-24

### Added

- Dependabot configuration for grouped weekly `uv` and GitHub Actions updates.

### Security

- Upgraded locked dependencies to resolve all open Dependabot alerts, including
  `cryptography` 50.0.0, `mcp` 1.29.0, `starlette` 1.6.0, `joserfc` 1.7.4,
  `pyjwt` 2.13.0, `python-multipart` 0.0.32, `pydantic-settings` 2.15.0, and
  `idna` 3.19.

### Changed

- Renamed the published distribution to `trsdn-obsidian-mcp`, because the PyPI
  name `obsidian-mcp` is held by an unrelated project. The import name
  `obsidian_mcp` and the `obsidian-mcp` console command are unchanged.
- Publishing now runs on PyPI Trusted Publishing (GitHub Actions OIDC) through
  a `build` -> `publish` -> `github-release` job chain, so the GitHub release is
  only created after the PyPI upload succeeds. No API tokens are involved.
- Restricted the source distribution to the package source, `README.md`,
  `CHANGELOG.md`, `LICENSE`, and `pyproject.toml`.
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

[Unreleased]: https://github.com/trsdn/obsidian-mcp/compare/v0.1.2...HEAD
[0.1.2]: https://github.com/trsdn/obsidian-mcp/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/trsdn/obsidian-mcp/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/trsdn/obsidian-mcp/releases/tag/v0.1.0
