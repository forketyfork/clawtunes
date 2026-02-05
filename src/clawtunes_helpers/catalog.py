"""Search and open from Apple Music catalog using iTunes Search API."""

import json
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

import click

from clawtunes_helpers.selection import select_item


ITUNES_SEARCH_URL = "https://itunes.apple.com/search"


def search_catalog(query: str, limit: int = 10) -> list[dict[str, Any]]:
    """Search Apple Music catalog using iTunes Search API.

    Returns list of song dicts with trackId, trackName, artistName, collectionName, trackViewUrl.
    """
    params = urllib.parse.urlencode(
        {
            "term": query,
            "media": "music",
            "entity": "song",
            "limit": limit,
        }
    )
    url = f"{ITUNES_SEARCH_URL}?{params}"

    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
            results: list[dict[str, Any]] = data.get("results", [])
            return results
    except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
        return []


def format_catalog_results(results: list[dict[str, Any]]) -> list[tuple[str, str]]:
    """Convert API results to (trackViewUrl, display_text) tuples for select_item()."""
    formatted = []
    for item in results:
        track_url = item.get("trackViewUrl", "")
        track_name = item.get("trackName", "Unknown")
        artist = item.get("artistName", "Unknown")
        album = item.get("collectionName", "Unknown")
        display = f"{track_name} - {artist} ({album})"
        formatted.append((track_url, display))
    return formatted


def open_catalog_track(track_url: str) -> bool:
    """Open a track URL in the Music app."""
    try:
        # Convert https:// URL to music:// scheme
        music_url = track_url.replace("https://", "music://")

        result = subprocess.run(
            ["open", music_url],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0
    except Exception:
        return False


def search_and_open(query: str, limit: int = 10) -> bool:
    """Search catalog, let user select, and open the selected track."""
    results = search_catalog(query, limit)

    if not results:
        click.echo(f"No results found for '{query}' in Apple Music catalog")
        return False

    formatted = format_catalog_results(results)

    if len(formatted) == 1:
        track_url = formatted[0][0]
        display = formatted[0][1]
    else:
        click.echo(f"Found {len(formatted)} results in Apple Music:")
        result = select_item(formatted, "Select a song")
        if result is None:
            click.echo("Cancelled")
            return False
        track_url = result
        display = next(d for u, d in formatted if u == track_url)

    click.echo(f"Opening in Apple Music: {display}")
    return open_catalog_track(track_url)
