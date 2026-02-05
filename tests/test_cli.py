"""Tests for the clawtunes CLI."""

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

    assert clawtunes.__version__ == "0.2.0"


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
