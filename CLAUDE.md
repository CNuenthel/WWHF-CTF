# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CTF exploitation framework for the MetaCTF competition (WWHF). Automates flag pulling, exploitation, and submission against the scoring API at `https://scoreboard.mctf.io:8000/`. Targets three separate vulnerable services. Designed to run continuously during a live CTF event on Windows.

## Setup

```bash
pip install -r requirements.txt
```

Tesseract OCR must be installed at `C:\Program Files\Tesseract-OCR\tesseract.exe` for image-based flag extraction (`tools/img_extract.py`).

**Before competition:** Set `TOKEN` in `api.py` and `SERVICE_ID` in each `exploit_svc_*.py`.

## Running Exploits

Each service has its own script run independently:
```bash
python exploit_svc_1.py
python exploit_svc_2.py
python exploit_svc_3.py
```

These run infinite loops with 5-second polling intervals: pull flags -> exploit -> submit.

## Architecture

**`api.py`** - All HTTP communication with the scoring server. Uses bearer token auth via `team-token` header. Functions: `pull_machines()`, `pull_flag_ids()`, `submit_flag()`, `pull_submissions()`. Display helpers write JSON snapshots to `team_data/` and `flag_data/`.

**`common/`** - Domain models.
- `Flag` - Represents a flag to capture. Holds metadata from the API plus a `key` field set after successful exploitation. Call `set_key()` then `submit()`.
- `Team` - Represents a service endpoint (team, service, hostname).

**`exploit_svc_*.py`** - One per service. Each maintains a `FLAGS` queue and `CAPTURED_FLAGS` list as module-level globals. The `exploit_service(flag)` function is the stub to implement per-service exploitation logic. Returns `bool` indicating success; must call `flag.set_key()` before returning `True`.

**`tools/`** - Reusable exploitation utilities:
- `forge_jwt.py` - JWT forgery (unsigned token with admin payload)
- `get_html.py` - HTTP GET wrapper
- `html_extract.py` - Regex extraction of `MetaCTF{...}` flags from HTML (basic, robust, and multi-flag variants)
- `img_extract.py` - Tesseract OCR text extraction from images

## Conventions

- Flag format: `MetaCTF{...}`
- Log prefixes: `[+]` progress, `[!]` error, `[$]` flag captured, `[#]` debug/info
- Python 3.13, type hints use `X | None` union syntax
- Global state pattern in exploit scripts (not thread-safe)

## Known Issues

- `Flag` class has no `is_expired()` method but `exploit_svc_*.py` calls it
- `pull_flag_ids()` in `api.py` hits the `/endpoints` URL (same as `pull_machines()`) rather than a flags-specific endpoint
