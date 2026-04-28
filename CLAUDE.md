# CLAUDE.md — Nexus Project Guide for AI Assistants

## Project Overview

Nexus is a private, local-first AI assistant for a college student. It runs entirely on the user's local machine and uses the Google Gemini API as its AI backend. All credentials are stored in a `.env` file and never hardcoded.

## Project Root

All code assumes the project lives at `~/nexus`. All file paths use `os.path.expanduser("~/nexus")` for portability.

## Architecture

- `nexus_cli.py` — Main interactive CLI entry point
- `nexus_launcher.sh` — Bash launcher script (start/stop/status/logs/repair)
- `soul.md` — Personality and behavioral instructions loaded into every AI call
- `vault.json` — Root-level default vault template (not used at runtime)
- `requirements.txt` — All Python dependencies
- `.env.example` — Template for environment variable configuration

### core/ modules

- `brain.py` — Gemini API interface; loads soul + vault context on every call
- `memory.py` — Read/write interface for `memory/vault.json`
- `search.py` — DuckDuckGo web search + BeautifulSoup scraping
- `monitor.py` — System stats via psutil; macOS notifications via osascript
- `heartbeat.py` — Background process logging stats every 60 seconds
- `architect.py` — Three-stage code generation: Draft → Audit → Save
- `maintenance.py` — Self-repair: reads error logs, fixes broken files with Gemini Pro
- `ear.py` — Voice input via faster-whisper + sounddevice
- `voice.py` — Voice output via macOS `say` command
- `canvas_sync.py` — Canvas LMS assignment sync via REST API
- `powerschool_sync.py` — PowerSchool grade sync via Playwright

### skills/ modules

- `web_agent.py` — Playwright-based website scraper; delegates to brain.py for Q&A

### memory/ directory

- `vault.json` — Live memory store (gitignored)
- `error_logs.json` — Error log consumed by maintenance.py

### logs/ directory

- `heartbeat.log` — Written by heartbeat.py (gitignored)
- `.gitkeep` — Keeps directory tracked by git

## Key Conventions

1. All file paths use `os.path.expanduser("~/nexus")` — never relative paths
2. All credentials come from `.env` via `python-dotenv` — never hardcoded
3. Every function has try/except error handling
4. Errors are logged to `memory/error_logs.json` — not just printed
5. No file deletion anywhere in the codebase
6. Git commits run after every architect or maintenance action
7. All imports are at the top of each file
8. Every module has `if __name__ == "__main__"` test blocks

## AI Models

- Default (fast): `gemini-2.5-flash-lite` — used for normal conversation
- Smart (heavy): `gemini-2.5-pro` — used for code generation and repair

## Routing Logic in nexus_cli.py

Priority order:
1. `exit` or `quit` → shutdown
2. starts with `build ` → `architect.implement_feature()`
3. starts with `repair` → `maintenance.run_self_repair()`
4. starts with `search ` → `brain.think(use_web=True)`
5. starts with `remember ` → `memory.add_fact()`
6. everything else → `brain.think()`

## Running the Project

```bash
cd ~/nexus
./nexus_launcher.sh start
```

Or directly:
```bash
source venv/bin/activate
python nexus_cli.py
```

## Adding New Skills

Place new `.py` files in `skills/` directory. They will be tracked in `skills_registry` in `memory/vault.json`. Use the `build` command to generate skills via Gemini.

## Testing Modules Standalone

Every module supports standalone testing:
```bash
python core/memory.py
python core/search.py
python core/brain.py
python core/monitor.py
```
