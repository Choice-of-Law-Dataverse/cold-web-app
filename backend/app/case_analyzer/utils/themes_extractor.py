"""Theme extraction utilities for PIL theme classification."""

import csv
import logging
from pathlib import Path

from ..tools.models import ThemeWithNA

logger = logging.getLogger(__name__)


def load_themes_table():
    """Load PIL themes from CSV file."""
    themes_path = Path(__file__).parent.parent / "data" / "themes.csv"

    if not themes_path.exists():
        logger.warning("themes.csv not found at %s", themes_path)
        return {}

    themes = {}
    try:
        with open(themes_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                theme = row.get("Theme", "").strip()
                definition = row.get("Definition", "").strip()
                if theme and definition:
                    themes[theme] = definition
    except Exception as e:
        logger.error("Error loading themes: %s", e)
        return {}

    return themes


def format_themes_table(themes_dict):
    """Format themes dictionary as a table string for prompts."""
    if not themes_dict:
        return "No themes available"

    lines = ["Theme | Definition"]
    lines.append("-" * 80)

    for theme, definition in themes_dict.items():
        # Truncate definition if too long for display
        if len(definition) > 200:
            definition = definition[:197] + "..."
        lines.append(f"{theme} | {definition}")

    return "\n".join(lines)


def filter_themes_by_list(themes_list: list[ThemeWithNA]) -> str:
    """Return a formatted Theme|Definition table for the specified themes."""
    if not themes_list:
        return "No themes specified."

    all_themes = _get_themes_dict()
    if not all_themes:
        return "No themes available."

    filtered_themes = {theme: definition for theme, definition in all_themes.items() if theme in themes_list}
    return format_themes_table(filtered_themes)


_themes_cache: dict[str, str] | None = None
_themes_str_cache: str | None = None


def _get_themes_dict() -> dict[str, str]:
    global _themes_cache
    if _themes_cache is None:
        _themes_cache = load_themes_table()
    return _themes_cache


def _get_themes_str() -> str:
    global _themes_str_cache
    if _themes_str_cache is None:
        _themes_str_cache = format_themes_table(_get_themes_dict())
    return _themes_str_cache


class _LazyThemesStr:
    """Lazy proxy that defers CSV I/O until the value is first accessed."""

    def __str__(self) -> str:
        return _get_themes_str()

    def __repr__(self) -> str:
        return _get_themes_str()

    def __bool__(self) -> bool:
        return bool(_get_themes_str())


THEMES_TABLE_STR: str = _LazyThemesStr()  # type: ignore[assignment]
