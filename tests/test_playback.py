"""Tests for playback helpers."""

from clawtunes_helpers import playback


def test_search_songs_uses_args_and_parses(monkeypatch):
    captured = {}

    def fake_run_applescript(script, args=None):
        captured["script"] = script
        captured["args"] = args
        stdout = "1|Song A|Artist A|Album A\n2|Song B|Artist B|Album B\n"
        return stdout, "", 0

    monkeypatch.setattr(playback, "run_applescript", fake_run_applescript)

    results = playback.search_songs("Bohemian Rhapsody", limit=5)

    assert "on run argv" in captured["script"]
    assert captured["args"] == ["Bohemian Rhapsody", "5"]
    assert results == [
        ("1", "Song A - Artist A (Album A)"),
        ("2", "Song B - Artist B (Album B)"),
    ]


def test_search_albums_passes_limit(monkeypatch):
    captured = {}

    def fake_run_applescript(script, args=None):
        captured["script"] = script
        captured["args"] = args
        stdout = "Album A|Artist A\nAlbum B|Artist B\n"
        return stdout, "", 0

    monkeypatch.setattr(playback, "run_applescript", fake_run_applescript)

    results = playback.search_albums("Hits", limit=3)

    assert "on run argv" in captured["script"]
    assert captured["args"] == ["Hits", "3"]
    assert results == [
        ("Album A", "Album A - Artist A"),
        ("Album B", "Album B - Artist B"),
    ]


def test_search_playlists_unlimited_uses_zero_limit(monkeypatch):
    captured = {}

    def fake_run_applescript(script, args=None):
        captured["script"] = script
        captured["args"] = args
        stdout = "Chill Vibes|12\n"
        return stdout, "", 0

    monkeypatch.setattr(playback, "run_applescript", fake_run_applescript)

    results = playback.search_playlists("Chill Vibes")

    assert "on run argv" in captured["script"]
    assert captured["args"] == ["Chill Vibes", "0"]
    assert results == [("Chill Vibes", "Chill Vibes (12 tracks)")]


def test_play_album_by_name_uses_args(monkeypatch):
    captured = {}

    def fake_run_applescript(script, args=None):
        captured["script"] = script
        captured["args"] = args
        return "ok", "", 0

    monkeypatch.setattr(playback, "run_applescript", fake_run_applescript)

    assert playback.play_album_by_name("Album Name")
    assert "on run argv" in captured["script"]
    assert captured["args"] == ["Album Name"]


def test_play_playlist_by_name_uses_args(monkeypatch):
    captured = {}

    def fake_run_applescript(script, args=None):
        captured["script"] = script
        captured["args"] = args
        return "", "", 0

    monkeypatch.setattr(playback, "run_applescript", fake_run_applescript)

    assert playback.play_playlist_by_name("Chill Vibes")
    assert "on run argv" in captured["script"]
    assert captured["args"] == ["Chill Vibes"]


def test_set_airplay_device_uses_args(monkeypatch):
    captured = {}

    def fake_run_applescript(script, args=None):
        captured["script"] = script
        captured["args"] = args
        return "", "", 0

    monkeypatch.setattr(playback, "run_applescript", fake_run_applescript)

    assert playback.set_airplay_device("HomePod", True) is None
    assert "on run argv" in captured["script"]
    assert captured["args"] == ["HomePod", "true"]
