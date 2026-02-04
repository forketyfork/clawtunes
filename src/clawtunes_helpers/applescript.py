"""AppleScript execution wrapper."""

import subprocess
from collections.abc import Sequence


def run_applescript(
    script: str, args: Sequence[str] | None = None
) -> tuple[str, str, int]:
    """Execute AppleScript and return (stdout, stderr, returncode)."""
    command = ["osascript", "-e", script]
    if args:
        command.extend(args)
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip(), result.stderr.strip(), result.returncode
