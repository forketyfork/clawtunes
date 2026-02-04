# Clawtunes

A command-line tool for controlling Apple Music on macOS.

## What it does

Clawtunes lets you search and play music, control playback, and tweak settings—all from the terminal. When you search for a song or album and there are multiple matches, it shows you a numbered list so you can pick the right one.

## Installation

### With Homebrew (recommended)

```bash
brew tap forketyfork/tap
brew install clawtunes
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
```

### AirPlay

```bash
clawtunes airplay              # List devices
clawtunes airplay "HomePod"    # Select device
clawtunes airplay "HomePod" --off  # Deselect device
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
