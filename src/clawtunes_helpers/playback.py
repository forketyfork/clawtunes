"""Play songs/albums/playlists and control playback."""

import click
from pathlib import Path

from clawtunes_helpers.applescript import run_applescript
from clawtunes_helpers.selection import select_item


def search_songs(name: str, limit: int | None = None) -> list[tuple[str, str]]:
    """Search for songs by name.

    Returns list of (id, display_text) tuples.
    """
    script = """
on run argv
    set query to item 1 of argv
    set limitValue to item 2 of argv as integer
    tell application "Music"
        set matchingTracks to (every track whose name contains query)
        if limitValue > 0 then
            if (count of matchingTracks) > limitValue then
                set matchingTracks to items 1 thru limitValue of matchingTracks
            end if
        end if
        set output to ""
        repeat with t in matchingTracks
            set trackId to id of t
            set trackName to name of t
            set trackArtist to artist of t
            set trackAlbum to album of t
            set output to output & trackId & "|" & trackName & "|" & trackArtist & "|" & trackAlbum & linefeed
        end repeat
        return output
    end tell
end run
"""
    limit_value = limit if limit is not None else 0
    stdout, _, returncode = run_applescript(script, [name, str(limit_value)])

    if returncode != 0 or not stdout:
        return []

    results = []
    for line in stdout.strip().split("\n"):
        if not line.strip():
            continue
        parts = line.split("|")
        if len(parts) >= 4:
            track_id, track_name, artist, album = parts[0], parts[1], parts[2], parts[3]
            display = f"{track_name} - {artist} ({album})"
            results.append((track_id, display))

    return results


def play_track_by_id(track_id: str) -> bool:
    """Play a track by its ID."""
    script = """
on run argv
    set trackId to item 1 of argv as integer
    tell application "Music"
        set t to (first track whose id is trackId)
        play t
    end tell
end run
"""
    _, _, returncode = run_applescript(script, [track_id])
    return returncode == 0


def play_song(name: str) -> bool:
    """Search for and play a song by name."""
    songs = search_songs(name)

    if not songs:
        click.echo(f"No songs found matching '{name}'")
        return False

    if len(songs) == 1:
        click.echo(f"Playing: {songs[0][1]}")
        return play_track_by_id(songs[0][0])

    click.echo(f"Found {len(songs)} matching songs:")
    selected_id = select_item(songs, "Select a song")

    if selected_id is None:
        click.echo("Cancelled")
        return False

    selected_display = next(d for i, d in songs if i == selected_id)
    click.echo(f"Playing: {selected_display}")
    return play_track_by_id(selected_id)


def search_albums(name: str, limit: int | None = None) -> list[tuple[str, str]]:
    """Search for albums by name.

    Returns list of (album_name, display_text) tuples.
    Note: Album names are used as identifiers since AppleScript doesn't have album IDs.
    """
    script = """
on run argv
    set query to item 1 of argv
    set limitValue to item 2 of argv as integer
    tell application "Music"
        set matchingTracks to (every track whose album contains query)
        set albumList to {}
        set albumArtists to {}
        repeat with t in matchingTracks
            set albumName to album of t
            set artistName to artist of t
            if albumName is not in albumList then
                set end of albumList to albumName
                set end of albumArtists to artistName
                if limitValue > 0 and (count of albumList) >= limitValue then
                    exit repeat
                end if
            end if
        end repeat
        set output to ""
        repeat with i from 1 to count of albumList
            set output to output & item i of albumList & "|" & item i of albumArtists & linefeed
        end repeat
        return output
    end tell
end run
"""
    limit_value = limit if limit is not None else 0
    stdout, _, returncode = run_applescript(script, [name, str(limit_value)])

    if returncode != 0 or not stdout:
        return []

    results = []
    for line in stdout.strip().split("\n"):
        if not line.strip():
            continue
        parts = line.split("|")
        if len(parts) >= 2:
            album_name, artist = parts[0], parts[1]
            display = f"{album_name} - {artist}"
            results.append((album_name, display))

    return results


def play_album_by_name(album_name: str) -> bool:
    """Play an album by its name."""
    script = """
on run argv
    set albumName to item 1 of argv
    tell application "Music"
        set albumTracks to (every track whose album is albumName)
        if (count of albumTracks) > 0 then
            set queueName to "Clawtunes Queue"
            if exists playlist queueName then
                set queuePlaylist to playlist queueName
                delete every track of queuePlaylist
            else
                set queuePlaylist to make new playlist with properties {name:queueName}
            end if
            repeat with t in albumTracks
                duplicate t to queuePlaylist
            end repeat
            play queuePlaylist
            return "ok"
        else
            return "not_found"
        end if
    end tell
end run
"""
    stdout, _, returncode = run_applescript(script, [album_name])
    return returncode == 0 and stdout.strip() == "ok"


def play_album(name: str) -> bool:
    """Search for and play an album by name."""
    albums = search_albums(name)

    if not albums:
        click.echo(f"No albums found matching '{name}'")
        return False

    if len(albums) == 1:
        click.echo(f"Playing album: {albums[0][1]}")
        return play_album_by_name(albums[0][0])

    click.echo(f"Found {len(albums)} matching albums:")
    selected_name = select_item(albums, "Select an album")

    if selected_name is None:
        click.echo("Cancelled")
        return False

    selected_display = next(d for n, d in albums if n == selected_name)
    click.echo(f"Playing album: {selected_display}")
    return play_album_by_name(selected_name)


def search_playlists(name: str, limit: int | None = None) -> list[tuple[str, str]]:
    """Search for playlists by name.

    Returns list of (playlist_name, display_text) tuples.
    """
    script = """
on run argv
    set query to item 1 of argv
    set limitValue to item 2 of argv as integer
    tell application "Music"
        set matchingPlaylists to (every playlist whose name contains query)
        if limitValue > 0 then
            if (count of matchingPlaylists) > limitValue then
                set matchingPlaylists to items 1 thru limitValue of matchingPlaylists
            end if
        end if
        set output to ""
        repeat with p in matchingPlaylists
            set pName to name of p
            set trackCount to count of tracks of p
            set output to output & pName & "|" & trackCount & linefeed
        end repeat
        return output
    end tell
end run
"""
    limit_value = limit if limit is not None else 0
    stdout, _, returncode = run_applescript(script, [name, str(limit_value)])

    if returncode != 0 or not stdout:
        return []

    results = []
    for line in stdout.strip().split("\n"):
        if not line.strip():
            continue
        parts = line.split("|")
        if len(parts) >= 2:
            playlist_name, track_count = parts[0], parts[1]
            display = f"{playlist_name} ({track_count} tracks)"
            results.append((playlist_name, display))

    return results


def play_playlist_by_name(playlist_name: str) -> bool:
    """Play a playlist by its name."""
    script = """
on run argv
    set playlistName to item 1 of argv
    tell application "Music"
        play playlist playlistName
    end tell
end run
"""
    _, _, returncode = run_applescript(script, [playlist_name])
    return returncode == 0


def play_playlist(name: str) -> bool:
    """Search for and play a playlist by name."""
    playlists = search_playlists(name)

    if not playlists:
        click.echo(f"No playlists found matching '{name}'")
        return False

    if len(playlists) == 1:
        click.echo(f"Playing playlist: {playlists[0][1]}")
        return play_playlist_by_name(playlists[0][0])

    click.echo(f"Found {len(playlists)} matching playlists:")
    selected_name = select_item(playlists, "Select a playlist")

    if selected_name is None:
        click.echo("Cancelled")
        return False

    selected_display = next(d for n, d in playlists if n == selected_name)
    click.echo(f"Playing playlist: {selected_display}")
    return play_playlist_by_name(selected_name)


def pause() -> str | None:
    """Pause playback. Returns error message on failure, None on success."""
    script = """
tell application "Music"
    pause
end tell
"""
    _, stderr, returncode = run_applescript(script)
    return stderr if returncode != 0 else None


def resume() -> str | None:
    """Resume playback. Returns error message on failure, None on success."""
    script = """
tell application "Music"
    play
end tell
"""
    _, stderr, returncode = run_applescript(script)
    return stderr if returncode != 0 else None


def next_track() -> str | None:
    """Skip to next track. Returns error message on failure, None on success."""
    script = """
tell application "Music"
    next track
end tell
"""
    _, stderr, returncode = run_applescript(script)
    return stderr if returncode != 0 else None


def previous_track() -> str | None:
    """Go to previous track. Returns error message on failure, None on success."""
    script = """
tell application "Music"
    back track
end tell
"""
    _, stderr, returncode = run_applescript(script)
    return stderr if returncode != 0 else None


# Volume control


def get_volume() -> tuple[int, bool] | None:
    """Get current volume and mute state. Returns (volume, is_muted) or None on error."""
    script = """
tell application "Music"
    return (sound volume as string) & "|" & (mute as string)
end tell
"""
    stdout, _, returncode = run_applescript(script)
    if returncode != 0:
        return None
    parts = stdout.strip().split("|")
    if len(parts) < 2:
        return None
    try:
        volume = int(parts[0])
        is_muted = parts[1].lower() == "true"
        return (volume, is_muted)
    except ValueError:
        return None


def set_volume(volume: int) -> str | None:
    """Set volume (0-100). Returns error message on failure, None on success."""
    volume = max(0, min(100, volume))
    script = f"""
tell application "Music"
    set sound volume to {volume}
end tell
"""
    _, stderr, returncode = run_applescript(script)
    return stderr if returncode != 0 else None


def _mute_state_path() -> Path:
    cache_dir = Path.home() / "Library" / "Caches" / "clawtunes"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / "mute_volume"


def mute() -> str | None:
    """Mute by setting volume to 0, caching previous volume."""
    result = get_volume()
    if result is None:
        return "Failed to get current volume"
    current, _ = result

    state_path = _mute_state_path()
    if state_path.exists():
        return None

    state_path.write_text(str(current), encoding="utf-8")
    error = set_volume(0)
    if error:
        state_path.unlink(missing_ok=True)
        return error
    return None


def unmute() -> str | None:
    """Restore volume from the cached value if available."""
    state_path = _mute_state_path()
    if not state_path.exists():
        return None
    try:
        previous = int(state_path.read_text(encoding="utf-8").strip())
    except ValueError:
        previous = 50
    error = set_volume(previous)
    if error:
        return error
    state_path.unlink(missing_ok=True)
    return None


# Shuffle and repeat


def get_shuffle() -> bool | None:
    """Get shuffle state. Returns True/False or None on error."""
    script = """
tell application "Music"
    return shuffle enabled as string
end tell
"""
    stdout, _, returncode = run_applescript(script)
    if returncode != 0:
        return None
    return stdout.strip().lower() == "true"


def set_shuffle(enabled: bool) -> str | None:
    """Set shuffle state. Returns error or None."""
    script = """
on run argv
    set stateValue to item 1 of argv
    tell application "Music"
        if stateValue is "on" then
            set shuffle enabled to true
        else if stateValue is "off" then
            set shuffle enabled to false
        else
            error "Invalid shuffle state"
        end if
    end tell
end run
"""
    state = "on" if enabled else "off"
    _, stderr, returncode = run_applescript(script, [state])
    return stderr if returncode != 0 else None


def get_repeat() -> str | None:
    """Get repeat mode. Returns 'off', 'one', 'all', or None on error."""
    script = """
tell application "Music"
    return song repeat as string
end tell
"""
    stdout, _, returncode = run_applescript(script)
    if returncode != 0:
        return None
    return stdout.strip()


def set_repeat(mode: str) -> str | None:
    """Set repeat mode to off, all, or one. Returns error or None."""
    script = """
on run argv
    set modeValue to item 1 of argv
    tell application "Music"
        if modeValue is "off" then
            set song repeat to off
        else if modeValue is "all" then
            set song repeat to all
        else if modeValue is "one" then
            set song repeat to one
        else
            error "Invalid repeat mode"
        end if
    end tell
end run
"""
    _, stderr, returncode = run_applescript(script, [mode])
    return stderr if returncode != 0 else None


# Love/dislike


def love_current_track() -> str | None:
    """Love the current track. Returns error message on failure, None on success."""
    script = """
tell application "Music"
    set favorited of current track to true
end tell
"""
    _, stderr, returncode = run_applescript(script)
    return stderr if returncode != 0 else None


def dislike_current_track() -> str | None:
    """Dislike the current track. Returns error message on failure, None on success."""
    script = """
tell application "Music"
    set disliked of current track to true
end tell
"""
    _, stderr, returncode = run_applescript(script)
    return stderr if returncode != 0 else None


def get_current_track_love_state() -> tuple[bool, bool] | None:
    """Get favorite/dislike state of current track. Returns (favorited, disliked) or None."""
    script = """
tell application "Music"
    set isFavorited to favorited of current track
    set isDisliked to disliked of current track
    return (isFavorited as string) & "|" & (isDisliked as string)
end tell
"""
    stdout, _, returncode = run_applescript(script)
    if returncode != 0:
        return None
    parts = stdout.strip().split("|")
    if len(parts) < 2:
        return None
    return (parts[0].lower() == "true", parts[1].lower() == "true")


# Playlists


def create_playlist(name: str) -> tuple[bool, str]:
    """Create a new playlist.

    Returns (success, message) tuple.
    """
    script = """
on run argv
    set playlistName to item 1 of argv
    tell application "Music"
        if exists playlist playlistName then
            return "exists"
        else
            make new playlist with properties {name:playlistName}
            return "ok"
        end if
    end tell
end run
"""
    stdout, stderr, returncode = run_applescript(script, [name])
    if returncode != 0:
        return False, stderr
    if stdout.strip() == "exists":
        return False, f"Playlist '{name}' already exists"
    return True, f"Created playlist: {name}"


def add_song_to_playlist(playlist_name: str, track_id: str) -> tuple[bool, str]:
    """Add a track to a playlist by track ID.

    Returns (success, message) tuple.
    """
    script = """
on run argv
    set playlistName to item 1 of argv
    set trackId to item 2 of argv as integer
    tell application "Music"
        if not (exists playlist playlistName) then
            return "playlist_not_found"
        end if
        set targetTrack to (first track whose id is trackId)
        set targetPlaylist to playlist playlistName
        duplicate targetTrack to targetPlaylist
        return "ok"
    end tell
end run
"""
    stdout, stderr, returncode = run_applescript(script, [playlist_name, track_id])
    if returncode != 0:
        return False, stderr
    if stdout.strip() == "playlist_not_found":
        return False, f"Playlist '{playlist_name}' not found"
    return True, ""


def remove_song_from_playlist(playlist_name: str, track_id: str) -> tuple[bool, str]:
    """Remove a track from a playlist by track ID.

    Returns (success, message) tuple.
    """
    script = """
on run argv
    set playlistName to item 1 of argv
    set trackId to item 2 of argv as integer
    tell application "Music"
        if not (exists playlist playlistName) then
            return "playlist_not_found"
        end if
        set targetPlaylist to playlist playlistName
        set matchingTracks to (every track of targetPlaylist whose id is trackId)
        if (count of matchingTracks) is 0 then
            return "track_not_found"
        end if
        delete (first track of targetPlaylist whose id is trackId)
        return "ok"
    end tell
end run
"""
    stdout, stderr, returncode = run_applescript(script, [playlist_name, track_id])
    if returncode != 0:
        return False, stderr
    result = stdout.strip()
    if result == "playlist_not_found":
        return False, f"Playlist '{playlist_name}' not found"
    if result == "track_not_found":
        return False, "Track not found in playlist"
    return True, ""


def search_songs_in_playlist(
    playlist_name: str, song_name: str, limit: int | None = None
) -> list[tuple[str, str]]:
    """Search for songs within a specific playlist.

    Returns list of (id, display_text) tuples.
    """
    script = """
on run argv
    set playlistName to item 1 of argv
    set query to item 2 of argv
    set limitValue to item 3 of argv as integer
    tell application "Music"
        if not (exists playlist playlistName) then
            return ""
        end if
        set targetPlaylist to playlist playlistName
        set matchingTracks to (every track of targetPlaylist whose name contains query)
        if limitValue > 0 then
            if (count of matchingTracks) > limitValue then
                set matchingTracks to items 1 thru limitValue of matchingTracks
            end if
        end if
        set output to ""
        repeat with t in matchingTracks
            set trackId to id of t
            set trackName to name of t
            set trackArtist to artist of t
            set trackAlbum to album of t
            set output to output & trackId & "|" & trackName & "|" & trackArtist & "|" & trackAlbum & linefeed
        end repeat
        return output
    end tell
end run
"""
    limit_value = limit if limit is not None else 0
    stdout, _, returncode = run_applescript(
        script, [playlist_name, song_name, str(limit_value)]
    )

    if returncode != 0 or not stdout:
        return []

    results = []
    for line in stdout.strip().split("\n"):
        if not line.strip():
            continue
        parts = line.split("|")
        if len(parts) >= 4:
            track_id, track_name, artist, album = parts[0], parts[1], parts[2], parts[3]
            display = f"{track_name} - {artist} ({album})"
            results.append((track_id, display))

    return results


def add_song_to_playlist_interactive(playlist_name: str, song_query: str) -> bool:
    """Search for a song and add it to a playlist with user selection."""
    songs = search_songs(song_query)

    if not songs:
        click.echo(f"No songs found matching '{song_query}'")
        return False

    if len(songs) == 1:
        selected_id = songs[0][0]
        selected_display = songs[0][1]
    else:
        click.echo(f"Found {len(songs)} matching songs:")
        result = select_item(songs, "Select a song")
        if result is None:
            click.echo("Cancelled")
            return False
        selected_id = result
        selected_display = next(d for i, d in songs if i == selected_id)

    success, message = add_song_to_playlist(playlist_name, selected_id)
    if success:
        click.echo(f'Added "{selected_display}" to "{playlist_name}"')
        return True
    else:
        click.echo(message, err=True)
        return False


def remove_song_from_playlist_interactive(playlist_name: str, song_query: str) -> bool:
    """Search for a song in a playlist and remove it with user selection."""
    songs = search_songs_in_playlist(playlist_name, song_query)

    if not songs:
        click.echo(
            f"No songs found matching '{song_query}' in playlist '{playlist_name}'"
        )
        return False

    if len(songs) == 1:
        selected_id = songs[0][0]
        selected_display = songs[0][1]
    else:
        click.echo(f"Found {len(songs)} matching songs in '{playlist_name}':")
        result = select_item(songs, "Select a song")
        if result is None:
            click.echo("Cancelled")
            return False
        selected_id = result
        selected_display = next(d for i, d in songs if i == selected_id)

    success, message = remove_song_from_playlist(playlist_name, selected_id)
    if success:
        click.echo(f'Removed "{selected_display}" from "{playlist_name}"')
        return True
    else:
        click.echo(message, err=True)
        return False


def get_all_playlists() -> list[tuple[str, int]]:
    """Get all playlists. Returns list of (name, track_count) tuples."""
    script = """
tell application "Music"
    set output to ""
    repeat with p in (every user playlist)
        set pName to name of p
        set trackCount to count of tracks of p
        set output to output & pName & "|" & trackCount & linefeed
    end repeat
    return output
end tell
"""
    stdout, _, returncode = run_applescript(script)
    if returncode != 0 or not stdout:
        return []

    results = []
    for line in stdout.strip().split("\n"):
        if not line.strip():
            continue
        parts = line.split("|")
        if len(parts) >= 2:
            try:
                results.append((parts[0], int(parts[1])))
            except ValueError:
                results.append((parts[0], 0))
    return results


# AirPlay


def get_airplay_devices() -> list[tuple[str, str, bool, bool]]:
    """Get AirPlay devices. Returns list of (name, kind, available, selected) tuples."""
    script = """
tell application "Music"
    set output to ""
    repeat with d in (every AirPlay device)
        set dName to name of d
        set dKind to kind of d as string
        set dAvailable to available of d
        set dSelected to selected of d
        set output to output & dName & "|" & dKind & "|" & (dAvailable as string) & "|" & (dSelected as string) & linefeed
    end repeat
    return output
end tell
"""
    stdout, _, returncode = run_applescript(script)
    if returncode != 0 or not stdout:
        return []

    results = []
    for line in stdout.strip().split("\n"):
        if not line.strip():
            continue
        parts = line.split("|")
        if len(parts) >= 4:
            name = parts[0]
            kind = parts[1]
            available = parts[2].lower() == "true"
            selected = parts[3].lower() == "true"
            results.append((name, kind, available, selected))
    return results


def set_airplay_device(name: str, selected: bool) -> str | None:
    """Select or deselect an AirPlay device. Returns error or None on success."""
    script = """
on run argv
    set deviceName to item 1 of argv
    set isSelected to (item 2 of argv) is "true"
    tell application "Music"
        set targetDevice to (first AirPlay device whose name is deviceName)
        set selected of targetDevice to isSelected
    end tell
end run
"""
    _, stderr, returncode = run_applescript(
        script, [name, "true" if selected else "false"]
    )
    return stderr if returncode != 0 else None
