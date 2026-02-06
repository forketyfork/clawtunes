"""Interactive selection helper."""

import click


def _get_flag(name: str) -> bool:
    ctx = click.get_current_context(silent=True)
    if ctx is None or ctx.obj is None:
        return False
    return bool(ctx.obj.get(name, False))


def is_non_interactive() -> bool:
    return _get_flag("non_interactive")


def select_item(items: list[tuple[str, str]], prompt: str) -> str | None:
    """Display numbered list, prompt user, return selected ID.

    Args:
        items: List of (id, display_text) tuples
        prompt: The prompt message to show

    Returns:
        The ID of the selected item, or None if cancelled
    """
    if not items:
        return None

    if len(items) == 1:
        return items[0][0]

    if _get_flag("first"):
        return items[0][0]

    click.echo()
    for i, (_, display) in enumerate(items, 1):
        click.echo(f"  {i}. {display}")
    click.echo()

    if _get_flag("non_interactive"):
        return None

    while True:
        try:
            choice: int = click.prompt(prompt, type=int)
            if 1 <= choice <= len(items):
                selected_id: str = items[choice - 1][0]
                return selected_id
            click.echo(f"Please enter a number between 1 and {len(items)}")
        except click.Abort:
            return None
