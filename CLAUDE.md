# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Clawtunes is a command-line tool for controlling Apple Music on macOS. It uses AppleScript to communicate with the Music app, enabling search, playback control, volume management, and library operations from the terminal.

## Common Commands

```bash
# Development setup (choose one)
just install              # Install with pip in editable mode
nix develop              # Or use Nix flake environment

# Run the tool during development
clawtunes --help

# Testing
just test                 # Run all tests
just test-match PATTERN   # Run tests matching pattern (e.g., just test-match test_status)
just test-cov             # Run tests with coverage report

# Code quality
just lint                 # Run all linters (black, ruff, mypy)
just format               # Auto-format code with black
just fix                  # Auto-fix issues (format + ruff --fix)
just check                # Full CI-equivalent checks (lint + test)

# Build
just build                # Create wheel distribution
```

## Architecture

```
src/
├── clawtunes/              # CLI package
│   └── cli.py              # Click-based command definitions
└── clawtunes_helpers/      # Apple Music control logic
    ├── applescript.py      # AppleScript execution wrapper (osascript)
    ├── catalog.py          # Apple Music catalog search/open helpers
    ├── playback.py         # Core music operations (search, play, volume, shuffle, etc.)
    ├── selection.py        # Interactive numbered menu for multiple matches
    └── status.py           # Now-playing info and player state
```

**Key patterns:**
- All Apple Music interaction happens via AppleScript strings executed through `osascript`
- AppleScript returns pipe-delimited data that gets parsed in Python
- The `playback.py` module contains Music app operations for playback, playlists, and device controls
- Mute state is cached in `~/Library/Caches/clawtunes/` for unmute functionality

## Testing

Tests use pytest with fixtures that mock AppleScript execution:
- `mock_applescript` - patches `run_applescript()` to return predefined output
- Tests verify CLI output and correct AppleScript invocation

## CI/CD

GitHub Actions workflow (`.github/workflows/build.yml`) runs formatting, linting, type checking, and tests using Nix for reproducibility.
