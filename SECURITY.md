# Security Policy

## Supported versions

Security fixes are provided for the latest published release.

## Reporting a vulnerability

Please report suspected vulnerabilities through a private GitHub Security
Advisory for this repository. Do not open a public issue containing note
content, vault paths, credentials, or exploit details.

Include the affected version, impact, reproduction steps, and any suggested
mitigation. You can expect an initial response within seven days.

## Security boundary

obsidian-mcp is a local stdio server. It trusts the MCP client process that
starts it and does not provide authentication, user-level authorization,
sandboxing, or network access controls.

The configured client can read every Markdown note in the selected vault.
Unless `OBSIDIAN_READ_ONLY=1` is set, it can also create, modify, move, and
delete notes. Path resolution prevents tool arguments and symbolic links from
escaping the configured vault, but it does not protect against a malicious
local process with direct filesystem access.

Use only trusted MCP clients, prefer read-only mode, restrict filesystem
permissions, and review the model provider's data-handling policy before
exposing sensitive notes.
