"""Theme extraction utilities for PIL theme classification."""

import csv
import logging
from pathlib import Path

from app.case_analyzer.models import ThemeWithNA

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
    """
    Returns a formatted table of Theme|Definition for specified themes.

    Args:
        themes_list: List of theme names to include

    Returns:
        Formatted markdown table string
    """
    if not themes_list:
        return "No themes specified."

    all_themes = THEMES_TABLE_DF
    if not all_themes:
        return "No themes available."

    # Filter themes based on the provided list
    filtered_themes = {theme: definition for theme, definition in all_themes.items() if theme in themes_list}

    return format_themes_table(filtered_themes)


# Load themes at module level
THEMES_TABLE_DF = load_themes_table()
THEMES_TABLE_STR = format_themes_table(THEMES_TABLE_DF)
