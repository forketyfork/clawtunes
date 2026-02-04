"""Clawtunes CLI - Control Apple Music from the command line."""

import click

from clawtunes_helpers import playback, status


def format_error(error: str) -> str:
    """Format error message, adding hints for common issues."""
    if "Not authorized" in error or "-1743" in error:
        return (
            f"{error}\n"
            "Hint: Grant automation access in System Settings → "
            "Privacy & Security → Automation → enable your terminal to control Music"
        )
    return error


@click.group()
@click.version_option()
def cli():
    """Control Apple Music from the command line."""
    pass


@cli.group()
def play():
    """Play songs, albums, or playlists."""
    pass


@play.command("song")
@click.argument("name")
def play_song(name: str):
    """Play a song by name."""
    if not playback.play_song(name):
        raise SystemExit(1)


@play.command("album")
@click.argument("name")
def play_album(name: str):
    """Play an album by name."""
    if not playback.play_album(name):
        raise SystemExit(1)


@play.command("playlist")
@click.argument("name")
def play_playlist(name: str):
    """Play a playlist by name."""
    if not playback.play_playlist(name):
        raise SystemExit(1)


@cli.command()
def pause():
    """Pause playback."""
    error = playback.pause()
    if error is None:
        click.echo("Paused")
    else:
        click.echo(f"Failed to pause: {format_error(error)}", err=True)
        raise SystemExit(1)


@cli.command()
def resume():
    """Resume playback."""
    error = playback.resume()
    if error is None:
        click.echo("Resumed")
    else:
        click.echo(f"Failed to resume: {format_error(error)}", err=True)
        raise SystemExit(1)


@cli.command("next")
def next_track():
    """Skip to the next track."""
    error = playback.next_track()
    if error is None:
        click.echo("Skipped to next track")
    else:
        click.echo(f"Failed to skip: {format_error(error)}", err=True)
        raise SystemExit(1)


@cli.command("prev")
def prev_track():
    """Go to the previous track."""
    error = playback.previous_track()
    if error is None:
        click.echo("Went to previous track")
    else:
        click.echo(f"Failed to go back: {format_error(error)}", err=True)
        raise SystemExit(1)


@cli.command("status")
@click.option("--debug", is_flag=True, help="Show AppleScript output for debugging")
def show_status(debug: bool):
    """Show the currently playing track."""
    if debug:
        stdout, stderr, returncode = status.get_now_playing_raw()
        click.echo(f"AppleScript stdout: {stdout!r}")
        if stderr:
            click.echo(f"AppleScript stderr: {stderr!r}", err=True)
        click.echo(f"AppleScript exit code: {returncode}")
        now_playing = status.parse_now_playing(stdout, returncode)
    else:
        now_playing = status.get_now_playing()
    player_state = status.get_player_state()

    if now_playing is None:
        click.echo("Nothing is playing")
        return

    state_indicator = (
        "▶" if player_state == "playing" else "⏸" if player_state == "paused" else "⏹"
    )

    click.echo(f"{state_indicator} {now_playing.name}")
    click.echo(f"  Artist: {now_playing.artist}")
    click.echo(f"  Album:  {now_playing.album}")
    click.echo(
        f"  {now_playing.progress_bar} {now_playing.position_formatted} / {now_playing.duration_formatted}"
    )


# Volume control


@cli.command("volume")
@click.argument("level", required=False)
def volume(level: str | None):
    """Get or set volume. Use +/- prefix for relative adjustment."""
    if level is None:
        result = playback.get_volume()
        if result is None:
            click.echo("Failed to get volume", err=True)
            raise SystemExit(1)
        vol, muted = result
        mute_indicator = " (muted)" if muted else ""
        click.echo(f"Volume: {vol}%{mute_indicator}")
        return

    # Parse level: could be absolute (50) or relative (+10, -10)
    try:
        if level.startswith("+"):
            result = playback.get_volume()
            if result is None:
                click.echo("Failed to get current volume", err=True)
                raise SystemExit(1)
            current, _ = result
            new_level = current + int(level[1:])
        elif level.startswith("-"):
            result = playback.get_volume()
            if result is None:
                click.echo("Failed to get current volume", err=True)
                raise SystemExit(1)
            current, _ = result
            new_level = current - int(level[1:])
        else:
            new_level = int(level)
    except ValueError:
        click.echo(f"Invalid volume level: {level}", err=True)
        raise SystemExit(1)

    error = playback.set_volume(new_level)
    if error:
        click.echo(f"Failed to set volume: {format_error(error)}", err=True)
        raise SystemExit(1)
    click.echo(f"Volume: {max(0, min(100, new_level))}%")


@cli.command("mute")
def mute():
    """Mute volume."""
    error = playback.mute()
    if error:
        click.echo(f"Failed to mute: {format_error(error)}", err=True)
        raise SystemExit(1)
    click.echo("Muted")


@cli.command("unmute")
def unmute():
    """Unmute volume."""
    error = playback.unmute()
    if error:
        click.echo(f"Failed to unmute: {format_error(error)}", err=True)
        raise SystemExit(1)
    click.echo("Unmuted")


# Shuffle and repeat


@cli.command("shuffle")
@click.argument("state", type=click.Choice(["on", "off"], case_sensitive=False))
def shuffle(state: str):
    """Set shuffle mode."""
    error = playback.set_shuffle(state.lower() == "on")
    if error:
        click.echo(f"Failed to set shuffle: {format_error(error)}", err=True)
        raise SystemExit(1)
    click.echo(f"Shuffle: {state.lower()}")


@cli.command("repeat")
@click.argument("mode", type=click.Choice(["off", "all", "one"], case_sensitive=False))
def repeat(mode: str):
    """Set repeat mode."""
    mode_value = mode.lower()
    error = playback.set_repeat(mode_value)
    if error:
        click.echo(f"Failed to change repeat mode: {format_error(error)}", err=True)
        raise SystemExit(1)
    click.echo(f"Repeat: {mode_value}")


# Search


@cli.command("search")
@click.argument("query")
@click.option("--songs/--no-songs", "-s", default=True, help="Search songs")
@click.option("--albums/--no-albums", "-a", default=True, help="Search albums")
@click.option(
    "--playlists/--no-playlists", "-p", default=False, help="Search playlists"
)
@click.option("--limit", "-n", default=10, help="Max results per category")
def search(query: str, songs: bool, albums: bool, playlists: bool, limit: int):
    """Search for songs, albums, or playlists."""
    found_any = False

    if songs:
        results = playback.search_songs(query, limit)
        if results:
            found_any = True
            click.echo(f"Songs ({len(results)}):")
            for _, display in results:
                click.echo(f"  {display}")
            click.echo()

    if albums:
        results = playback.search_albums(query, limit)
        if results:
            found_any = True
            click.echo(f"Albums ({len(results)}):")
            for _, display in results:
                click.echo(f"  {display}")
            click.echo()

    if playlists:
        results = playback.search_playlists(query, limit)
        if results:
            found_any = True
            click.echo(f"Playlists ({len(results)}):")
            for _, display in results:
                click.echo(f"  {display}")
            click.echo()

    if not found_any:
        click.echo(f"No results found for '{query}'")


# Love/dislike


@cli.command("love")
def love():
    """Love the current track."""
    error = playback.love_current_track()
    if error:
        click.echo(f"Failed to love track: {format_error(error)}", err=True)
        raise SystemExit(1)
    now_playing = status.get_now_playing()
    if now_playing:
        click.echo(f"Loved: {now_playing.name}")
    else:
        click.echo("Loved current track")


@cli.command("dislike")
def dislike():
    """Dislike the current track."""
    error = playback.dislike_current_track()
    if error:
        click.echo(f"Failed to dislike track: {format_error(error)}", err=True)
        raise SystemExit(1)
    now_playing = status.get_now_playing()
    if now_playing:
        click.echo(f"Disliked: {now_playing.name}")
    else:
        click.echo("Disliked current track")


# Playlists


@cli.command("playlists")
def list_playlists():
    """List all playlists."""
    playlists = playback.get_all_playlists()
    if not playlists:
        click.echo("No playlists found")
        return

    click.echo(f"Playlists ({len(playlists)}):")
    for name, count in playlists:
        click.echo(f"  {name} ({count} tracks)")


# AirPlay


@cli.command("airplay")
@click.argument("device", required=False)
@click.option("--off", is_flag=True, help="Deselect the device")
def airplay(device: str | None, off: bool):
    """List or select AirPlay devices."""
    devices = playback.get_airplay_devices()

    if device is None:
        if not devices:
            click.echo("No AirPlay devices found")
            return

        click.echo("AirPlay devices:")
        for name, kind, available, selected in devices:
            status_str = ""
            if selected:
                status_str = " [selected]"
            elif not available:
                status_str = " [unavailable]"
            click.echo(f"  {name} ({kind}){status_str}")
        return

    # Find matching device
    matching = [d for d in devices if device.lower() in d[0].lower()]
    if not matching:
        click.echo(f"No device found matching '{device}'", err=True)
        raise SystemExit(1)

    if len(matching) > 1:
        click.echo(f"Multiple devices match '{device}':")
        for name, kind, _, _ in matching:
            click.echo(f"  {name} ({kind})")
        raise SystemExit(1)

    target_name = matching[0][0]
    error = playback.set_airplay_device(target_name, not off)
    if error:
        click.echo(f"Failed to set AirPlay device: {format_error(error)}", err=True)
        raise SystemExit(1)

    if off:
        click.echo(f"Deselected: {target_name}")
    else:
        click.echo(f"Selected: {target_name}")


if __name__ == "__main__":
    cli()
