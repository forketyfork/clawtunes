"""Tests for catalog helpers."""

import json

from clawtunes_helpers import catalog


def test_search_catalog_parses_json(monkeypatch):
    mock_response = {
        "resultCount": 2,
        "results": [
            {
                "trackId": 123,
                "trackName": "Bohemian Rhapsody",
                "artistName": "Queen",
                "collectionName": "A Night at the Opera",
                "trackViewUrl": "https://music.apple.com/us/album/123",
            },
            {
                "trackId": 456,
                "trackName": "We Will Rock You",
                "artistName": "Queen",
                "collectionName": "News of the World",
                "trackViewUrl": "https://music.apple.com/us/album/456",
            },
        ],
    }

    class FakeResponse:
        def read(self):
            return json.dumps(mock_response).encode("utf-8")

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

    def fake_urlopen(url, timeout=None):
        return FakeResponse()

    monkeypatch.setattr(catalog.urllib.request, "urlopen", fake_urlopen)

    results = catalog.search_catalog("queen", limit=5)

    assert len(results) == 2
    assert results[0]["trackName"] == "Bohemian Rhapsody"
    assert results[1]["artistName"] == "Queen"


def test_search_catalog_handles_error(monkeypatch):
    def fake_urlopen(url, timeout=None):
        raise catalog.urllib.error.URLError("Network error")

    monkeypatch.setattr(catalog.urllib.request, "urlopen", fake_urlopen)

    results = catalog.search_catalog("query")
    assert results == []


def test_format_catalog_results():
    api_results = [
        {
            "trackName": "Song A",
            "artistName": "Artist A",
            "collectionName": "Album A",
            "trackViewUrl": "https://music.apple.com/a",
        },
        {
            "trackName": "Song B",
            "artistName": "Artist B",
            "collectionName": "Album B",
            "trackViewUrl": "https://music.apple.com/b",
        },
    ]

    formatted = catalog.format_catalog_results(api_results)

    assert formatted == [
        ("https://music.apple.com/a", "Song A - Artist A (Album A)"),
        ("https://music.apple.com/b", "Song B - Artist B (Album B)"),
    ]


def test_open_catalog_track(monkeypatch):
    calls = []

    def fake_run(cmd, capture_output=False, text=False):
        calls.append(cmd)

        class FakeResult:
            returncode = 0

        return FakeResult()

    monkeypatch.setattr(catalog.subprocess, "run", fake_run)

    result = catalog.open_catalog_track("https://music.apple.com/track/123")

    assert result is True
    assert len(calls) == 1
    assert calls[0] == ["open", "music://music.apple.com/track/123"]
