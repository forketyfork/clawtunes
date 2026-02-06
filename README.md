# Clawtunes

[![Build status](https://github.com/forketyfork/clawtunes/actions/workflows/build.yml/badge.svg)](https://github.com/forketyfork/clawtunes/actions/workflows/build.yml)
[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/language-Python-blue.svg)](https://python.org/)
[![Clawhub Skill](https://img.shields.io/badge/clawhub-skill-orange.svg)](https://clawhub.ai/forketyfork/clawtunes)

A command-line tool for controlling Apple Music on macOS. Also available as a [Claude Code skill on Clawhub](https://clawhub.ai/forketyfork/clawtunes).

## What it does

Clawtunes lets you search and play music, control playback, manage playlists, and tweak settings—all from the terminal. When you search for a song or album and there are multiple matches, it shows you a numbered list so you can pick the right one.

## Installation

### With Homebrew (recommended)

```bash
brew install forketyfork/tap/clawtunes
```

### With pip

```bash
pip install clawtunes
```

### With Nix

```bash
nix run github:forketyfork/clawtunes
```

Or add to your flake inputs and install permanently.

## Usage

### Playing music

```bash
# Play a song (shows selection menu if multiple matches)
clawtunes play song "Bohemian Rhapsody"

# Play an album
clawtunes play album "Abbey Road"

# Play a playlist
clawtunes play playlist "Chill Vibes"
```

### Non-interactive mode

By default, when multiple matches are found, clawtunes shows a numbered menu for selection. Use `--non-interactive` (`-N`) to skip the prompt and just list the matches, or `--first` (`-1`) to auto-select the first match:

```bash
# List matches without prompting (exits with code 1)
clawtunes -N play song "love"

# Auto-select the first match
clawtunes -1 play song "love"
```

These flags apply to all commands that involve selection: `play song`, `play album`, `play playlist`, `playlist add`, `playlist remove`, and `catalog search`.

### Playback controls

```bash
clawtunes pause
clawtunes resume
clawtunes next
clawtunes prev
```

### Status

```bash
clawtunes status
```

### Volume

```bash
clawtunes volume         # Show current volume
clawtunes volume 50      # Set to 50%
clawtunes volume +10     # Increase by 10%
clawtunes volume -10     # Decrease by 10%
clawtunes mute           # Mute
clawtunes unmute         # Unmute
```

### Shuffle and repeat

```bash
clawtunes shuffle on     # Enable shuffle
clawtunes shuffle off    # Disable shuffle
clawtunes repeat off     # Set repeat off
clawtunes repeat all     # Repeat all
clawtunes repeat one     # Repeat one
```

### Search

```bash
clawtunes search "query"              # Search songs and albums
clawtunes search "query" -p           # Include playlists
clawtunes search "query" --no-albums  # Songs only
clawtunes search "query" -n 20        # Show more results
```

### Love/dislike

```bash
clawtunes love           # Love current track
clawtunes dislike        # Dislike current track
```

### Playlists

```bash
clawtunes playlists      # List all playlists
clawtunes playlist create "Road Trip"
clawtunes playlist add "Road Trip" "Kickstart My Heart"
clawtunes playlist remove "Road Trip" "Kickstart My Heart"
```

### AirPlay

```bash
clawtunes airplay              # List devices
clawtunes airplay "HomePod"    # Select device
clawtunes airplay "HomePod" --off  # Deselect device
```

### Apple Music catalog

```bash
clawtunes catalog search "Bowie Heroes"
clawtunes catalog search "Bowie Heroes" -n 5
```

## Example output

```
$ clawtunes status
▶ Bohemian Rhapsody
  Artist: Queen
  Album:  A Night at the Opera
  [===============---------------] 2:34 / 5:55

$ clawtunes search "yesterday"
Songs (3):
  Yesterday - The Beatles (Help!)
  Yesterday - Boyz II Men (II)
  Yesterday Once More - Carpenters (Now & Then)

Albums (1):
  Help! - The Beatles
```

## Requirements

- macOS (uses AppleScript to control Apple Music)
- Python 3.10+
- Apple Music app

## Development

The project uses Nix for development:

```bash
# Enter dev environment
nix develop

# Or with direnv
direnv allow

# Run checks
just check

# Run specific commands
just lint
just test
just format
```

## License

MIT
