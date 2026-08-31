# Security Policy

## Supported Versions

AeroOpt-X is currently under active development.

Security fixes are generally applied to the latest version available on the `main` branch.

| Version | Supported |
| ------- | --------- |
| Latest `main` branch | ✅ |
| Older releases | ⚠️ Best effort |
| Unsupported / archived versions | ❌ |

---

## Reporting a Vulnerability

If you discover a security vulnerability in AeroOpt-X, please do not publicly disclose the vulnerability through GitHub Issues.

Instead, report it privately to the project maintainer.

When reporting a vulnerability, please include as much information as possible:

- A clear description of the vulnerability
- The affected component or file
- Steps to reproduce the issue
- Proof-of-concept information, if appropriate
- Potential impact
- Suggested mitigation, if available
- The version or commit where the issue was discovered

Please avoid including unnecessary sensitive information or credentials.

---

## What Happens After You Report

After receiving a security report, the project maintainer will make a reasonable effort to:

1. Confirm receipt of the report.
2. Investigate and reproduce the issue.
3. Assess the potential impact.
4. Develop and test a fix where appropriate.
5. Release or publish the fix.
6. Coordinate disclosure when necessary.

Response and resolution times may vary depending on the severity and complexity of the issue.

---

## Security Scope

The following areas are currently considered part of the AeroOpt-X security scope:

- Flask application routes
- API endpoints
- Input validation
- JSON request handling
- Dependency vulnerabilities
- Docker configuration
- Container configuration
- Application configuration
- Frontend JavaScript where security vulnerabilities may affect users

---

## Out of Scope

The following are generally outside the scope of this security policy:

- Issues requiring physical access to a user's computer
- Social engineering attacks
- Vulnerabilities in third-party services outside the project's control
- Denial-of-service reports involving unrealistic or excessive traffic
- Vulnerabilities requiring users to intentionally disable normal browser or operating-system security protections

---

## Security Best Practices for Contributors

Contributors should:

- Never commit passwords, API keys, tokens, or credentials.
- Avoid committing `.env` files containing secrets.
- Keep dependencies reasonably up to date.
- Validate user-provided input.
- Avoid exposing sensitive information in API responses.
- Review Docker and deployment configuration changes carefully.
- Report potential vulnerabilities responsibly.

---

## Disclosure Policy

Please allow reasonable time for a vulnerability to be investigated and addressed before publicly disclosing details.

Public disclosure before a fix is available may place users and deployments at unnecessary risk.

---

## Contact

For security-related reports, please contact the repository owner privately.

Do not use the public issue tracker to disclose sensitive security vulnerabilities.

---

© 2026 AeroOpt-X. All rights reserved.
