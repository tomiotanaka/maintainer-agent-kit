# Security Policy

## Supported versions

The current `main` branch receives security fixes.

## Reporting a vulnerability

Open a private report through GitHub security advisories when available. Please
do not disclose vulnerabilities in public issues before a fix is available.

Please include:

- affected command or workflow
- expected behavior
- actual behavior
- reproduction steps
- whether sensitive data may be exposed

## Secret handling

This project should never require secrets for dry-run mode. Provider credentials
belong in the provider's own configuration, not in this repository.
