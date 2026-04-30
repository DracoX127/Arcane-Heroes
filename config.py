"""
Arcane Heroes — Centralized Configuration & Constants
All game constants live here for single-source-of-truth maintenance.
"""

import os
from colorama import Fore

# ── File Paths ──
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
PLAYERS_FILE = os.path.join(DATA_DIR, "players.json")
SHOP_DATA_FILE = os.path.join(DATA_DIR, "shop_data.json")
HEROES_FILE = os.path.join(DATA_DIR, "heroes.json")

# ── Skill Tree ──
SKILL_TREE_BRANCHES = [
    "ATK",
    "HP",
    "DEF",
    "SPD",
    "CRIT CHANCE",
    "FIRE ATK",
    "WATER ATK",
    "EARTH ATK",
    "AIR ATK",
    "ELECTRIC ATK",
    "SHADOW ATK",
]

SKILL_TREE_BONUSES = {
    "ATK": 3,
    "HP": 30,
    "DEF": 3,
    "SPD": 2,
    "CRIT CHANCE": 2,
    "FIRE ATK": 5,
    "WATER ATK": 5,
    "EARTH ATK": 5,
    "AIR ATK": 5,
    "ELECTRIC ATK": 5,
    "SHADOW ATK": 5,
}

COMMANDER_ELEMENTS = {
    "Pyronis": "FIRE ATK",
    "Aquaryn": "WATER ATK",
    "Terradon": "EARTH ATK",
    "Zephyros": "AIR ATK",
    "Voltaris": "ELECTRIC ATK",
    "Noctyra": "SHADOW ATK",
}

COMMANDER_NAMES = {
    1: "Pyronis",
    2: "Aquaryn",
    3: "Terradon",
    4: "Zephyros",
    5: "Voltaris",
    6: "Noctyra",
}

SKILL_TREE_COLORS = {
    "ATK": Fore.LIGHTRED_EX,
    "HP": Fore.LIGHTGREEN_EX,
    "DEF": Fore.LIGHTBLUE_EX,
    "SPD": Fore.CYAN,
    "CRIT CHANCE": Fore.LIGHTYELLOW_EX,
    "FIRE ATK": Fore.RED,
    "WATER ATK": Fore.BLUE,
    "EARTH ATK": Fore.GREEN,
    "AIR ATK": Fore.CYAN,
    "ELECTRIC ATK": Fore.YELLOW,
    "SHADOW ATK": Fore.MAGENTA,
}

# ── Economy: UI Dimensions ──
PANEL_WIDTH = 118
LEDGER_LIMIT = 18

# ── Economy: Colors ──
RARITY_COLORS = {
    "Common": Fore.WHITE,
    "Uncommon": Fore.LIGHTGREEN_EX,
    "Rare": Fore.CYAN,
    "Epic": Fore.MAGENTA,
    "Mythic": Fore.LIGHTYELLOW_EX,
    "Legendary": Fore.LIGHTRED_EX,
}

ELEMENT_COLORS = {
    "Fire": Fore.RED,
    "Water": Fore.BLUE,
    "Earth": Fore.GREEN,
    "Air": Fore.CYAN,
    "Electric": Fore.YELLOW,
    "Shadow": Fore.MAGENTA,
    None: Fore.WHITE,
}

CATEGORY_COLORS = {
    "Consumables": Fore.LIGHTGREEN_EX,
    "Weapons": Fore.LIGHTRED_EX,
    "Armor": Fore.LIGHTBLUE_EX,
    "Accessories": Fore.LIGHTMAGENTA_EX,
    "Materials": Fore.WHITE,
    "Shards": Fore.YELLOW,
    "Elemental Specials": Fore.LIGHTYELLOW_EX,
}

# ── Economy: Branch Config ──
BRANCH_ORDER = [
    "Merchant",
    "Forge",
    "Exchange",
    "Alchemy",
    "Relics",
    "Logistics",
    "Barter",
    "Prestige",
]

BRANCH_CONFIG = {
    "Merchant": {
        "max_rank": 3,
        "theme": "Better shop prices and cleaner stock quality.",
    },
    "Forge": {
        "max_rank": 3,
        "theme": "Improves gear quality and equipment scaling.",
    },
    "Exchange": {
        "max_rank": 5,
        "theme": "Deeper listing power and trading board efficiency.",
    },
    "Alchemy": {
        "max_rank": 3,
        "theme": "Stronger consumables and better item use outcomes.",
    },
    "Relics": {
        "max_rank": 5,
        "theme": "Access to premium relic stock and luxury elemental goods.",
    },
    "Logistics": {
        "max_rank": 3,
        "theme": "Extra listing capacity and cleaner inventory handling.",
    },
    "Barter": {
        "max_rank": 3,
        "theme": "Barter efficiency and better mixed-deal economics.",
    },
    "Prestige": {
        "max_rank": 5,
        "theme": "Luxury access, elite wares, and premium market leverage.",
    },
}

BRANCH_MODIFIERS = {
    "Merchant": [
        {"shop_discount_pct": 3},
        {"shop_discount_pct": 3, "sale_bonus_pct": 2},
        {"shop_discount_pct": 4, "sale_bonus_pct": 3},
    ],
    "Forge": [
        {"gear_value_bonus_pct": 5},
        {"gear_value_bonus_pct": 10},
        {"gear_value_bonus_pct": 15},
    ],
    "Exchange": [
        {"market_fee_discount_pct": 4},
        {"listing_cap_bonus": 1, "market_fee_discount_pct": 4},
        {"market_fee_discount_pct": 5, "sale_bonus_pct": 2},
        {"listing_cap_bonus": 1, "buy_order_bonus_pct": 5},
        {"market_fee_discount_pct": 6, "sale_bonus_pct": 4},
    ],
    "Alchemy": [
        {"consumable_power_pct": 10},
        {"consumable_power_pct": 15},
        {"consumable_power_pct": 20, "use_fee_discount_pct": 10},
    ],
    "Relics": [
        {"relic_access_tier": 1},
        {"relic_access_tier": 1, "shop_discount_pct": 2},
        {"relic_access_tier": 2, "sale_bonus_pct": 2},
        {"relic_access_tier": 3, "listing_cap_bonus": 1},
        {"relic_access_tier": 4, "sale_bonus_pct": 4},
    ],
    "Logistics": [
        {"listing_cap_bonus": 1},
        {"listing_cap_bonus": 1},
        {"listing_cap_bonus": 2},
    ],
    "Barter": [
        {"barter_bonus_pct": 6},
        {"barter_bonus_pct": 8},
        {"barter_bonus_pct": 12},
    ],
    "Prestige": [
        {"prestige_access_tier": 1},
        {"prestige_access_tier": 2, "market_fee_discount_pct": 2},
        {"prestige_access_tier": 3, "sale_bonus_pct": 2},
        {"prestige_access_tier": 4, "shop_discount_pct": 3},
        {"prestige_access_tier": 5, "market_fee_discount_pct": 4, "sale_bonus_pct": 4},
    ],
}

PRESET_DURATIONS = [
    ("1 hour", 3600),
    ("6 hours", 21600),
    ("24 hours", 86400),
]

SHOP_MILESTONE_REWARDS = {
    2: {"items": {"market_writ": 1}, "gold": 90, "message": "Quartermaster stipend unlocked."},
    3: {"items": {"skill_spark": 1}, "permit_hours": 6, "message": "Broker license package delivered."},
    4: {"commander_items": {"material": 2, "shard": 1}, "message": "Elemental reserve shipment delivered."},
    5: {"gold": 220, "permit_hours": 24, "message": "Guild prestige dividend paid out."},
}

COMMANDER_ELEMENT_NAMES = {
    "Pyronis": "Fire",
    "Aquaryn": "Water",
    "Terradon": "Earth",
    "Zephyros": "Air",
    "Voltaris": "Electric",
    "Noctyra": "Shadow",
}

COMMANDER_RESOURCE_IDS = {
    "Pyronis": {"material": "cinder_ore", "shard": "pyronis_shard"},
    "Aquaryn": {"material": "tideglass", "shard": "aquaryn_shard"},
    "Terradon": {"material": "rootbark_core", "shard": "terradon_shard"},
    "Zephyros": {"material": "sky_silk", "shard": "zephyros_shard"},
    "Voltaris": {"material": "volt_crystal", "shard": "voltaris_shard"},
    "Noctyra": {"material": "umbral_thread", "shard": "noctyra_shard"},
}

LOADOUT_SLOT_LABELS = {
    "weapon": "Weapon",
    "head": "Head",
    "chest": "Chest",
    "hands": "Hands",
    "legs": "Legs",
    "feet": "Feet",
    "accessory_1": "Accessory I",
    "accessory_2": "Accessory II",
    "relic": "Relic",
    "charm": "Charm",
    "sigil": "Sigil",
    "banner": "Banner",
}

MODIFIER_LABELS = {
    "shop_discount_pct": "Shop Discount",
    "sale_bonus_pct": "Sale Bonus",
    "market_fee_discount_pct": "Market Fee Cut",
    "listing_cap_bonus": "Listing Cap",
    "buy_order_bonus_pct": "Buy Order Bonus",
    "barter_bonus_pct": "Barter Bonus",
    "consumable_power_pct": "Consumable Power",
    "gear_value_bonus_pct": "Gear Value",
    "prestige_access_tier": "Prestige Access",
    "relic_access_tier": "Relic Access",
    "use_fee_discount_pct": "Use Fee Cut",
}

RARITY_VALUE_MULTIPLIERS = {
    "Common": 1.00,
    "Uncommon": 1.08,
    "Rare": 1.18,
    "Epic": 1.34,
    "Mythic": 1.56,
    "Legendary": 1.86,
}

CATEGORY_VALUE_MULTIPLIERS = {
    "Consumables": 0.96,
    "Weapons": 1.18,
    "Armor": 1.10,
    "Accessories": 1.14,
    "Materials": 0.94,
    "Shards": 1.26,
    "Elemental Specials": 1.42,
}

STAT_VALUE_WEIGHTS = {
    "ATK": 24.0,
    "DEF": 19.0,
    "HP": 0.95,
    "SPD": 30.0,
    "CRIT CHANCE": 34.0,
    "FIRE ATK": 19.0,
    "WATER ATK": 19.0,
    "EARTH ATK": 19.0,
    "AIR ATK": 19.0,
    "ELECTRIC ATK": 19.0,
    "SHADOW ATK": 19.0,
}

TRADER_ARCHETYPES = [
    {
        "id": "auric_voss",
        "name": "Auric Voss",
        "title": "Price Hawk",
        "style": "sharp",
        "patience": 2,
        "greed": 0.18,
        "buy_bias": 0.91,
        "focus_categories": ["Weapons", "Accessories", "Elemental Specials"],
        "focus_elements": ["Fire", "Electric"],
    },
    {
        "id": "mira_quill",
        "name": "Mira Quill",
        "title": "Archive Broker",
        "style": "calm",
        "patience": 4,
        "greed": 0.08,
        "buy_bias": 0.98,
        "focus_categories": ["Shards", "Relics", "Elemental Specials"],
        "focus_elements": ["Water", "Shadow"],
    },
    {
        "id": "torren_vale",
        "name": "Torren Vale",
        "title": "Quartermaster",
        "style": "stubborn",
        "patience": 3,
        "greed": 0.12,
        "buy_bias": 0.94,
        "focus_categories": ["Armor", "Materials", "Weapons"],
        "focus_elements": ["Earth", "Fire"],
    },
    {
        "id": "syl_vire",
        "name": "Syl Vire",
        "title": "Fast Broker",
        "style": "playful",
        "patience": 3,
        "greed": 0.10,
        "buy_bias": 0.95,
        "focus_categories": ["Accessories", "Materials", "Consumables"],
        "focus_elements": ["Air", "Electric"],
    },
    {
        "id": "nox_mercer",
        "name": "Nox Mercer",
        "title": "Shadow Trader",
        "style": "sly",
        "patience": 2,
        "greed": 0.14,
        "buy_bias": 0.92,
        "focus_categories": ["Shards", "Materials", "Elemental Specials"],
        "focus_elements": ["Shadow", "Water"],
    },
    {
        "id": "iona_crest",
        "name": "Iona Crest",
        "title": "Collector",
        "style": "warm",
        "patience": 5,
        "greed": 0.06,
        "buy_bias": 1.01,
        "focus_categories": ["Relics", "Accessories", "Shards"],
        "focus_elements": ["Water", "Air"],
    },
]

TREND_LABELS = [
    (-99, -3, "falling", Fore.LIGHTBLUE_EX),
    (-2, -1, "soft", Fore.CYAN),
    (0, 0, "steady", Fore.WHITE),
    (1, 2, "warm", Fore.YELLOW),
    (3, 99, "hot", Fore.LIGHTRED_EX),
]

# ── Animation Timing Constants ──
ANIMATION_DELAYS = {
    "fast": 0.005,
    "normal": 0.015,
    "slow": 0.03,
    "dramatic": 0.06,
}

EFFECT_DURATIONS = {
    "flash": 0.4,
    "matrix": 1.0,
    "starfield": 0.8,
    "shimmer": 0.6,
    "explosion": 0.5,
    "bounce": 0.8,
    "color_cycle": 1.0,
    "thunder": 0.5,
    "neon_flicker": 0.6,
}

# ── ASCII Cinema Frame Data ──
ASCII_CINEMA_FRAMES = {
    "lock": [
        "    🔒    ",
        "   🔒🔒   ",
        "  🔒🔒🔒  ",
        " 🔒🔒🔒🔒 ",
        "🔒🔒🔒🔒🔒",
        " 💥💥💥💥💥 ",
        "  ✨✨✨  ",
        "   ✨✨   ",
        "    ✨    ",
    ],
    "card_flip": [
        "┌─────────┐",
        "│ ▓▓▓▓▓▓▓ │",
        "│ ▓▓▓▓▓▓▓ │",
        "│ ▓▓▓▓▓▓▓ │",
        "│ ▓▓▓▓▓▓▓ │",
        "│ ▓▓▓▓▓▓▓ │",
        "└─────────┘",
    ],
    "rune_wave": [
        "ᚠᚢᚦᚨᚱᚲᚷᚹ",
        "ᚺᚾᛁᛃᛇᛈᛉᛊ",
        "ᛏᛒᛖᛗᛚᛜᛞᛟ",
        "ᚠᚢᚦᚨᚱᚲᚷᚹ",
    ],
    "void_spiral": [
        r"    @     ",
        r"   /|\    ",
        r"  / | \   ",
        r" /  |  \  ",
        r"@---●---@",
        r" \  |  /  ",
        r"  \ | /   ",
        r"   \|/    ",
        r"    @     ",
    ],
}

# ── Rarity Glow Border Characters ──
RARITY_GLOW_CHARS = {
    "Common": ("─", "│", "┌", "┐", "└", "┘"),
    "Uncommon": ("═", "║", "╔", "╗", "╚", "╝"),
    "Rare": ("━", "┃", "┏", "┓", "┗", "┛"),
    "Epic": ("▬", "▮", "▭", "▭", "▭", "▭"),
    "Mythic": ("═", "║", "╔", "╗", "╚", "╝"),
    "Legendary": ("█", "█", "█", "█", "█", "█"),
}

# ── Elemental Burst Colors for Skill Unlocks ──
ELEMENT_BURST_COLORS = {
    "FIRE ATK": (Fore.LIGHTRED_EX, Fore.RED, Fore.YELLOW),
    "WATER ATK": (Fore.LIGHTBLUE_EX, Fore.BLUE, Fore.CYAN),
    "EARTH ATK": (Fore.LIGHTGREEN_EX, Fore.GREEN, Fore.LIGHTYELLOW_EX),
    "AIR ATK": (Fore.CYAN, Fore.LIGHTCYAN_EX, Fore.WHITE),
    "ELECTRIC ATK": (Fore.YELLOW, Fore.LIGHTYELLOW_EX, Fore.LIGHTWHITE_EX),
    "SHADOW ATK": (Fore.MAGENTA, Fore.LIGHTMAGENTA_EX, Fore.LIGHTBLACK_EX),
    "ATK": (Fore.LIGHTRED_EX, Fore.RED, Fore.LIGHTYELLOW_EX),
    "HP": (Fore.LIGHTGREEN_EX, Fore.GREEN, Fore.LIGHTCYAN_EX),
    "DEF": (Fore.LIGHTBLUE_EX, Fore.BLUE, Fore.CYAN),
    "SPD": (Fore.CYAN, Fore.LIGHTCYAN_EX, Fore.WHITE),
    "CRIT CHANCE": (Fore.LIGHTYELLOW_EX, Fore.YELLOW, Fore.LIGHTWHITE_EX),
}

# ── Toast Notification Colors ──
TOAST_COLORS = {
    "info": Fore.LIGHTCYAN_EX,
    "success": Fore.LIGHTGREEN_EX,
    "warn": Fore.LIGHTYELLOW_EX,
    "error": Fore.LIGHTRED_EX,
    "rare_drop": Fore.LIGHTMAGENTA_EX,
    "level_up": Fore.LIGHTYELLOW_EX,
}

# ── Animation Timing Constants (Extended) ──
PARTICLE_TRAIL_CHARS = ["*", "✦", "✧", "·", "•", "+", "×", "◆", "◇", "◎"]
RAIN_CHARS = ["|", "│", "┃", "╽", "╿"]
SNOW_CHARS = ["*", "·", "•", "◦", "❄", "❅"]
FOG_CHARS = ["░", "▒", "▓", "≈", "~"]
LIGHTNING_CHARS = ["⚡", "↯", "⌁", "ϟ"]
VOID_CHARS = ["@", "#", "%", "&", "*", "+", "=", "?"]
RUNE_CHARS = ["ᚠ", "ᚢ", "ᚦ", "ᚨ", "ᚱ", "ᚲ", "ᚷ", "ᚹ", "ᚺ", "ᚾ", "ᛁ", "ᛃ", "ᛇ", "ᛈ", "ᛉ", "ᛊ", "ᛏ", "ᛒ", "ᛖ", "ᛗ", "ᛚ", "ᛜ", "ᛞ", "ᛟ"]
