# Contributing to Nexus

Nexus is an open source project. Contributions of all kinds are welcome.

## How to Contribute

### Reporting Bugs

Open a GitHub issue with:
- A clear description of the bug
- Steps to reproduce it
- What you expected to happen
- What actually happened
- Your Python version and operating system

Never include credentials, API keys, or personal data in issues.

### Suggesting Features

Open a GitHub issue labeled "enhancement" with a description of the feature and why it would benefit college students.

### Submitting Code

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Write your changes
4. Test your changes manually
5. Commit with a clear message: `git commit -m "Add: brief description of what this does"`
6. Push to your fork: `git push origin feature/your-feature-name`
7. Open a pull request against the main branch

### Code Standards

- Python 3.10+
- All secrets must come from .env via python-dotenv — never hardcode anything
- All new functions must have try/except error handling
- All new skill files in skills/ must pass the security scanner
- No markdown in user-facing messages unless explicitly asked for code
- Follow the existing code style — plain function names, clear variable names, comments where logic is non-obvious

### Adding New Skills

New skills go in the skills/ directory. Each skill must:
- Have at least one print() showing results
- Use only approved libraries listed in core/security_scanner.py
- Use absolute paths with os.path.expanduser for all file operations
- Have try/except on every function
- Not contain any hardcoded credentials

You can also ask Nexus to build a skill for you by describing it in plain English. The architect module will generate, audit, and install it automatically.

## Code of Conduct

Be respectful. This project exists to help students who have no money and no support. Keep that mission in mind.
