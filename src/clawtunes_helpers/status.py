"""Now playing info."""

from dataclasses import dataclass

from clawtunes_helpers.applescript import run_applescript


@dataclass
class NowPlaying:
    """Information about the currently playing track."""

    name: str
    artist: str
    album: str
    duration: float
    position: float

    @property
    def duration_formatted(self) -> str:
        """Format duration as mm:ss."""
        minutes = int(self.duration) // 60
        seconds = int(self.duration) % 60
        return f"{minutes}:{seconds:02d}"

    @property
    def position_formatted(self) -> str:
        """Format position as mm:ss."""
        minutes = int(self.position) // 60
        seconds = int(self.position) % 60
        return f"{minutes}:{seconds:02d}"

    @property
    def progress_bar(self, width: int = 30) -> str:
        """Generate a progress bar."""
        if self.duration <= 0:
            return "[" + "-" * width + "]"
        progress = min(1.0, self.position / self.duration)
        filled = int(width * progress)
        return "[" + "=" * filled + "-" * (width - filled) + "]"


def _now_playing_script() -> str:
    return """
tell application "Music"
    try
        set t to current track
    on error
        return "not_playing"
    end try

    try
        set trackName to name of t
    on error
        return "not_playing"
    end try
    if trackName is missing value then return "not_playing"

    try
        set trackArtist to artist of t
    on error
        set trackArtist to ""
    end try
    if trackArtist is missing value then set trackArtist to ""

    try
        set trackAlbum to album of t
    on error
        set trackAlbum to ""
    end try
    if trackAlbum is missing value then set trackAlbum to ""

    try
        set trackDuration to duration of t
    on error
        set trackDuration to 0
    end try
    if trackDuration is missing value then set trackDuration to 0

    try
        set playerPos to player position
    on error
        set playerPos to 0
    end try
    if playerPos is missing value then set playerPos to 0

    return trackName & "|" & trackArtist & "|" & trackAlbum & "|" & (trackDuration as string) & "|" & (playerPos as string)
end tell
"""


def get_now_playing_raw() -> tuple[str, str, int]:
    """Return raw AppleScript output for now playing."""
    return run_applescript(_now_playing_script())


def parse_now_playing(stdout: str, returncode: int) -> NowPlaying | None:
    """Parse AppleScript output into NowPlaying data."""
    if returncode != 0 or stdout.strip() == "not_playing":
        return None

    parts = stdout.strip().split("|")
    if len(parts) < 5:
        return None

    try:
        duration = parts[3].replace(",", ".")
        position = parts[4].replace(",", ".")
        return NowPlaying(
            name=parts[0],
            artist=parts[1],
            album=parts[2],
            duration=float(duration),
            position=float(position),
        )
    except (ValueError, IndexError):
        return None


def get_now_playing() -> NowPlaying | None:
    """Get information about the currently playing track.

    Returns None if nothing is playing.
    """
    stdout, _, returncode = run_applescript(_now_playing_script())
    return parse_now_playing(stdout, returncode)


def get_player_state() -> str:
    """Get the current player state (playing, paused, stopped)."""
    script = """
tell application "Music"
    return player state as string
end tell
"""
    stdout, _, returncode = run_applescript(script)

    if returncode != 0:
        return "unknown"

    return stdout.strip()
