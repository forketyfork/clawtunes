"""Tests for the clawtunes CLI."""

from unittest.mock import patch

from click.testing import CliRunner

from clawtunes.cli import cli


def test_cli_help():
    """Test that CLI help works."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Control Apple Music" in result.output


def test_cli_version():
    """Test that CLI version option exists."""
    import clawtunes

    assert clawtunes.__version__ == "0.2.1"


def test_play_help():
    """Test that play subcommand help works."""
    runner = CliRunner()
    result = runner.invoke(cli, ["play", "--help"])
    assert result.exit_code == 0
    assert "song" in result.output
    assert "album" in result.output
    assert "playlist" in result.output


def test_playlist_help():
    """Test that playlist subcommand help works."""
    runner = CliRunner()
    result = runner.invoke(cli, ["playlist", "--help"])
    assert result.exit_code == 0
    assert "create" in result.output
    assert "add" in result.output
    assert "remove" in result.output


def test_catalog_help():
    """Test that catalog subcommand help works."""
    runner = CliRunner()
    result = runner.invoke(cli, ["catalog", "--help"])
    assert result.exit_code == 0
    assert "search" in result.output


def test_cli_help_shows_non_interactive_and_first():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert "--non-interactive" in result.output
    assert "--first" in result.output


MULTI_SONG_APPLESCRIPT_OUTPUT = "1|Song A|Artist A|Album A\n2|Song B|Artist B|Album B\n"


@patch("clawtunes_helpers.playback.run_applescript")
def test_non_interactive_lists_matches_without_prompt(mock_applescript):
    mock_applescript.return_value = (MULTI_SONG_APPLESCRIPT_OUTPUT, "", 0)
    runner = CliRunner()
    result = runner.invoke(cli, ["-N", "play", "song", "test"])
    assert "1. Song A" in result.output
    assert "2. Song B" in result.output
    assert "Cancelled" not in result.output
    assert result.exit_code == 1


@patch("clawtunes_helpers.playback.run_applescript")
def test_first_auto_selects_first_match(mock_applescript):
    mock_applescript.side_effect = [
        (MULTI_SONG_APPLESCRIPT_OUTPUT, "", 0),  # search_songs
        ("", "", 0),  # play_track_by_id
    ]
    runner = CliRunner()
    result = runner.invoke(cli, ["-1", "play", "song", "test"])
    assert "Playing: Song A" in result.output
    assert result.exit_code == 0
