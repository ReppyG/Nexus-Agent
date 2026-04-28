# Security Policy

## Supported Versions

Only the latest version of Nexus receives security fixes.

## Reporting a Vulnerability

Please do not report security vulnerabilities through public GitHub issues.

Email security concerns to the repository maintainer or open a private security advisory on GitHub.

Include:
- A description of the vulnerability
- Steps to reproduce it
- Potential impact
- Suggested fix if you have one

You will receive a response within 72 hours.

## Security Model

Nexus is designed to run on your own server. Your data stays on your server. Key security properties:

**No credential hardcoding.** All secrets are loaded from .env using python-dotenv. The .env file is in .gitignore and never committed.

**Four-layer skill security.** Every skill file goes through static analysis, dependency whitelisting, sandboxed execution, and SHA256 hash verification before running.

**Quarantine system.** Files that fail any security check are moved to quarantine/ and the user is notified immediately.

**No external data leakage.** Nexus only connects to services you explicitly configure: Gemini API, Canvas LMS, PowerSchool, ntfy.sh, and Signal. It does not phone home or send data anywhere else.

**Minimal permissions.** Nexus does not request administrative privileges. It runs as a normal user process.

## Known Limitations

- PowerSchool sync requires storing credentials in .env. Use a strong unique password for your PowerSchool account.
- The Gemini API sends your prompts to Google. Avoid including full assignment text or sensitive personal information in queries.
- signal-cli requires your Signal account credentials. Secure your server appropriately.

## Dependency Security

Dependencies are pinned in requirements.txt. Audit them with `pip audit` before deploying.
