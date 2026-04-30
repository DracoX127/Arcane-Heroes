"""
Arcane Heroes — Compatibility Shim
Re-exports constants and UI helpers so legacy imports continue to work.
New code should import directly from `config` and `ui`.
"""

# Re-export all constants from config.py
from config import (
    SKILL_TREE_BRANCHES,
    SKILL_TREE_BONUSES,
    SKILL_TREE_COLORS,
    COMMANDER_ELEMENTS,
    COMMANDER_NAMES,
    # Economy constants (for backward compat with any external imports)
    PANEL_WIDTH,
    LEDGER_LIMIT,
    RARITY_COLORS,
    ELEMENT_COLORS,
    CATEGORY_COLORS,
    BRANCH_ORDER,
    BRANCH_CONFIG,
    BRANCH_MODIFIERS,
    PRESET_DURATIONS,
    SHOP_MILESTONE_REWARDS,
    COMMANDER_ELEMENT_NAMES,
    COMMANDER_RESOURCE_IDS,
    LOADOUT_SLOT_LABELS,
    MODIFIER_LABELS,
    RARITY_VALUE_MULTIPLIERS,
    CATEGORY_VALUE_MULTIPLIERS,
    STAT_VALUE_WEIGHTS,
    TRADER_ARCHETYPES,
    TREND_LABELS,
    PLAYERS_FILE,
    SHOP_DATA_FILE,
)

# Re-export UI helpers from ui.py (legacy names)
from ui import (
    ensure_colorama,
    clear,
    clear_last_line,
    typed_print as type,
    fast_typed_print as fasttype,
    visible_len as _visible_len,
    pad as _pad,
    line as _line,
    title as _title,
    panel as _panel,
    prompt as _prompt,
    divider,
    status_bar,
    menu_option,
    header_art,
    footer_art,
    small_header,
    info_line,
    choice_prompt,
    progress_bar,
    ANSI_PATTERN,
)

# Legacy internal name preserved for any direct references
_BlankPalette = __import__("ui", fromlist=["_BlankPalette"])._BlankPalette

