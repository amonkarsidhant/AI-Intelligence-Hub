# Security Policy

## Supported Version

The latest `main` branch is the supported version for security fixes.

## Reporting a Vulnerability

Please do not open a public issue for credential leaks, SSRF vectors, auth bypasses, or other sensitive vulnerabilities.

Instead:

1. Open a private security advisory on GitHub if enabled.
2. If that is not available, contact the maintainer directly through a private channel.
3. Include reproduction steps, impact, and any suggested mitigation.

## Sensitive Areas

When reviewing or reporting issues, pay particular attention to:

- feed fetching and external requests
- container and environment variable handling
- stored digests and local SQLite state
- any future SMTP, webhook, or auth integrations
