# Security Policy

## Security model

Fexus is a local desktop application.

There is no Fexus cloud backend in the project.

However, Fexus can connect to infrastructure using SSH and other network protocols, so local application security and credential handling still matter.

## Supported versions

Security fixes target the latest release and the current `main` branch.

## Reporting a vulnerability

Do not publish a working exploit in a public issue.

Use GitHub's private vulnerability reporting/security advisory feature when available.

Include:

- affected version or commit
- operating system
- exact reproduction steps
- impact
- logs that do not contain secrets
- suggested mitigation, if known

## Credentials

Fexus should prefer:

- SSH keys
- SSH agents
- least-privilege user accounts
- local OS credential stores in future releases

Do not commit credentials to the repository.

## Network safety

Do not use Fexus to expose private services to the public internet.

Before enabling a privileged integration:

- understand its permissions
- keep firewalls enabled
- use read-only access where possible
- avoid root where unnecessary
- review the integration code

## Supply chain

This repository uses dependency pinning ranges, Dependabot configuration and GitHub Actions for automated checks.

Public GitHub repositories should also enable:

- secret scanning
- push protection
- Dependabot alerts
- dependency review
- code scanning / CodeQL
- protected branches

## Privacy

The desktop application does not require a Fexus account and does not need Fexus servers to function.
