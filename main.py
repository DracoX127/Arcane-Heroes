import random
import time
from typing import Any, Dict, List

from colorama import Fore, Style

from config import COMMANDER_ELEMENT_NAMES
from game_functions import (
    clear,
    ensure_colorama,
    load_players,
    save_players,
    sync_player_data,
    welcome,
)
from hero_data import (
    DEFAULT_CATALOG_STATE,
    EFFECT_TYPES,
    ENCOUNTERED_CATALOG_STATE,
    HERO_ELEMENTS,
    HERO_RARITIES,
    HERO_STYLE_TAGS,
    OWNED_CATALOG_STATE,
    STATUS_VOCAB,
    build_visible_rows,
    display_power,
    filter_rows,
    get_hero_record,
    hero_lookup,
    load_hero_catalog,
    merge_owned_hero,
    sort_rows,
)
from ui import (
    arcane_cataclysm,
    fireworks,
    header_art,
    level_up_celebration,
    matrix_rain,
    menu_option,
    neon_flicker,
    panel,
    rainbow_text,
    shimmer_line,
    sin,
    skill_unlock_burst,
    sp,
    starfield_background,
    status_bar,
    toast_notification,
)
from utils import SKILL_TREE_BONUSES, SKILL_TREE_BRANCHES, SKILL_TREE_COLORS


ensure_colorama()
load_hero_catalog()


ELEMENT_COLORS = {
    "Fire": Fore.LIGHTRED_EX,
    "Water": Fore.LIGHTBLUE_EX,
    "Earth": Fore.LIGHTGREEN_EX,
    "Air": Fore.CYAN,
    "Electric": Fore.YELLOW,
    "Shadow": Fore.MAGENTA,
    "Arcane": Fore.LIGHTWHITE_EX,
}

RARITY_COLORS = {
    "Common": Fore.WHITE,
    "Uncommon": Fore.LIGHTGREEN_EX,
    "Rare": Fore.CYAN,
    "Elite": Fore.LIGHTBLUE_EX,
    "Epic": Fore.LIGHTMAGENTA_EX,
    "Mythic": Fore.LIGHTYELLOW_EX,
    "Legendary": Fore.LIGHTRED_EX,
    "Ancient": Fore.LIGHTCYAN_EX,
    "Celestial": Fore.LIGHTWHITE_EX,
    "Divine": Fore.YELLOW,
    "Eternal": Fore.LIGHTMAGENTA_EX,
}

MAILBOX_LIMIT = 25
PAGE_SIZE = 8

MISSION_BOARD = [
    {
        "name": "Sunforge Rescue",
        "theme": "Save a trapped scouting crew from a molten canyon breach.",
        "recommended": 360,
        "gold": 180,
        "xp": 65,
        "hero_chance": 0.24,
        "encounter_chance": 0.58,
        "focus_elements": ["Fire", "Earth", "Electric"],
    },
    {
        "name": "Stormline Sweep",
        "theme": "Clear sky pirates from the crystal rail route.",
        "recommended": 430,
        "gold": 230,
        "xp": 90,
        "hero_chance": 0.28,
        "encounter_chance": 0.62,
        "focus_elements": ["Air", "Electric", "Water"],
    },
    {
        "name": "Night Rift Lockdown",
        "theme": "Seal a shadow breach before it floods the frontier.",
        "recommended": 510,
        "gold": 320,
        "xp": 120,
        "hero_chance": 0.34,
        "encounter_chance": 0.68,
        "focus_elements": ["Shadow", "Water", "Air"],
    },
]

EXPLORE_ZONES = [
    {
        "name": "Aurora Wilds",
        "theme": "A bright frontier packed with relic trails and hidden camps.",
        "recommended": 320,
        "gold": 90,
        "xp": 40,
        "hero_chance": 0.18,
        "encounter_chance": 0.50,
        "focus_elements": ["Earth", "Air", "Water"],
    },
    {
        "name": "Coral Vault",
        "theme": "Flooded ruins full of lost signals and sleeping guardians.",
        "recommended": 390,
        "gold": 130,
        "xp": 55,
        "hero_chance": 0.22,
        "encounter_chance": 0.56,
        "focus_elements": ["Water", "Shadow", "Electric"],
    },
    {
        "name": "Obsidian Stair",
        "theme": "A dangerous ascent where elite heroes sometimes answer the call.",
        "recommended": 470,
        "gold": 170,
        "xp": 80,
        "hero_chance": 0.26,
        "encounter_chance": 0.64,
        "focus_elements": ["Shadow", "Fire", "Earth"],
    },
]

BATTLE_QUEUE = [
    {
        "name": "Riftfang Hydra",
        "theme": "A snarling arena beast that tests front-line control.",
        "recommended": 370,
        "gold": 150,
        "xp": 70,
        "boss": False,
        "encounter_chance": 0.36,
        "focus_elements": ["Water", "Earth", "Shadow"],
    },
    {
        "name": "Thunder Duke",
        "theme": "An elite raider captain pushing your heroes to their limit.",
        "recommended": 455,
        "gold": 230,
        "xp": 100,
        "boss": True,
        "encounter_chance": 0.46,
        "focus_elements": ["Electric", "Air", "Fire"],
    },
    {
        "name": "Nocturne Colossus",
        "theme": "A towering abyss engine built for late-night disaster.",
        "recommended": 560,
        "gold": 340,
        "xp": 145,
        "boss": True,
        "encounter_chance": 0.58,
        "focus_elements": ["Shadow", "Electric", "Water"],
    },
]

SORT_OPTIONS = {
    "default": "Element -> rarity -> power",
    "power": "Power",
    "name": "Name",
    "rarity": "Rarity",
}


def _element_color(element: str) -> str:
    return ELEMENT_COLORS.get(element, Fore.LIGHTWHITE_EX)


def _rarity_color(rarity: str) -> str:
    return RARITY_COLORS.get(rarity, Fore.LIGHTWHITE_EX)


def _ambient_transition() -> None:
    random.choice(
        [
            lambda: starfield_background(duration=0.35, star_count=45),
            lambda: matrix_rain(duration=0.35, width=90),
            lambda: shimmer_line(char="=", width=72, cycles=1),
        ]
    )()


def _persist_stats(stats: Dict[str, Any]) -> None:
    sync_player_data(stats)
    players = load_players()
    if isinstance(players, dict) and "Account Name" in players and "Commander" in players:
        players = {players["Account Name"]: players}
    players[stats["Account Name"]] = stats
    save_players(players)


def _battle_record(stats: Dict[str, Any]) -> Dict[str, int]:
    return stats.setdefault("Battle Record", {})


def _mailbox(stats: Dict[str, Any]) -> List[Dict[str, Any]]:
    return stats.setdefault("Mailbox", [])


def _deliver_mail(stats: Dict[str, Any], subject: str, body: str, tag: str = "System") -> None:
    mailbox = _mailbox(stats)
    mailbox.append(
        {
            "subject": subject,
            "body": body,
            "tag": tag,
            "read": False,
            "at": int(time.time()),
        }
    )
    if len(mailbox) > MAILBOX_LIMIT:
        del mailbox[:-MAILBOX_LIMIT]


def _unread_mail_count(stats: Dict[str, Any]) -> int:
    return sum(1 for mail in _mailbox(stats) if not mail.get("read"))


def _hero_codex(stats: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return stats.setdefault("Hero Codex", {})


def _owned_heroes(stats: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return stats.setdefault("Heroes", {})


def _codex_counts(stats: Dict[str, Any]) -> Dict[str, int]:
    codex = _hero_codex(stats)
    counts = {
        DEFAULT_CATALOG_STATE: 0,
        ENCOUNTERED_CATALOG_STATE: 0,
        OWNED_CATALOG_STATE: 0,
    }
    for hero_id in hero_lookup():
        state = codex.get(hero_id, {}).get("state", DEFAULT_CATALOG_STATE)
        if state not in counts:
            state = DEFAULT_CATALOG_STATE
        counts[state] += 1
    return counts


def _owned_hero_views(stats: Dict[str, Any]) -> List[Dict[str, Any]]:
    heroes = []
    for hero_id, hero_state in _owned_heroes(stats).items():
        heroes.append(merge_owned_hero(hero_id, hero_state))
    heroes.sort(key=lambda hero: (-int(hero.get("power", 0)), hero.get("name", hero["id"])))
    return heroes


def _top_squad(stats: Dict[str, Any], count: int = 3) -> List[Dict[str, Any]]:
    return _owned_hero_views(stats)[:count]


def _squad_power(stats: Dict[str, Any]) -> int:
    power = sum(int(hero.get("power", 0)) for hero in _top_squad(stats))
    power += int(stats.get("Lvl", 1)) * 18
    power += int(stats.get("Buffs", {}).get("ATK", 0)) * 3
    return power


def _hero_list_line(row: Dict[str, Any]) -> str:
    state = row.get("state", DEFAULT_CATALOG_STATE)
    favorite = f"{Fore.YELLOW}*{Fore.RESET} " if row.get("favorite") else ""
    if state == OWNED_CATALOG_STATE:
        tags = "/".join(row.get("style_tags", [])[:2])
        return (
            f"{favorite}{_rarity_color(row['rarity'])}{row['name']}{Fore.RESET} | "
            f"{_element_color(row['element'])}{row['element']}{Fore.RESET} | "
            f"{tags} | Lv {row.get('level', 1)} Rank {row.get('rank', 1)} | Power {row.get('power', 0)}"
        )
    if state == ENCOUNTERED_CATALOG_STATE:
        return (
            f"{favorite}{_rarity_color(row['rarity'])}{row['name']}{Fore.RESET} | "
            f"{_element_color(row['element'])}{row['element']}{Fore.RESET} | "
            f"{row['title']}"
        )
    return f"{favorite}{Fore.LIGHTBLACK_EX}[Silhouette] ??? ???{Fore.RESET}"


def _format_skill_block(skill: Dict[str, Any]) -> List[str]:
    lines = [
        f"{Fore.LIGHTWHITE_EX}{skill['name']}{Fore.RESET} | {skill['effect_type']} | cd {skill['cooldown']} | target {skill['target_type']}",
        (
            f"Power {skill['power_value']} | Chance {skill['status_chance']} | Duration {skill['duration']} | "
            f"Hits {skill['hit_count']}"
        ),
    ]
    if skill.get("status_name"):
        lines.append(f"Status: {skill['status_name']}")
    if skill.get("self_condition"):
        lines.append(f"Condition: {skill['self_condition']}")
    if skill.get("self_cost"):
        lines.append(f"Cost: {skill['self_cost']}")
    lines.append(skill["description"])
    return lines


def _owned_detail_lines(row: Dict[str, Any]) -> List[str]:
    stats = row.get("base_stats", {})
    lines = [
        f"Name: {_rarity_color(row['rarity'])}{row['name']}{Fore.RESET}",
        f"Title: {row['title']}",
        f"Element: {_element_color(row['element'])}{row['element']}{Fore.RESET}",
        f"Rarity: {row['rarity']}",
        f"Tags: {', '.join(row.get('style_tags', []))}",
        f"Power: {row.get('power', 0)}",
        (
            f"HP {stats.get('hp', 0)} | ATK {stats.get('atk', 0)} | DEF {stats.get('def', 0)} | "
            f"SPD {stats.get('spd', 0)} | CRIT {stats.get('crit', 0)} | ACC {stats.get('acc', 0)} | "
            f"RESIST {stats.get('resist', 0)}"
        ),
        f"Level: {row.get('level', 1)} | Rank: {row.get('rank', 1)} | Soul Stones: {row.get('soul_stones', 0)}",
        "",
        row.get("lore", ""),
        "",
        f"{Fore.LIGHTCYAN_EX}Skills{Fore.RESET}",
    ]
    for skill in row.get("skills", []):
        lines.extend(_format_skill_block(skill))
        lines.append("")
    lines.append(f"{Fore.LIGHTYELLOW_EX}Progression Hooks:{Fore.RESET} Level, Rank, and Soul Stones are tracked for future upgrades.")
    return lines


def _encountered_detail_lines(row: Dict[str, Any]) -> List[str]:
    return [
        f"Name: {_rarity_color(row['rarity'])}{row['name']}{Fore.RESET}",
        f"Title: {row['title']}",
        f"Element: {_element_color(row['element'])}{row['element']}{Fore.RESET}",
        f"Rarity: {row['rarity']}",
        "",
        "You have encountered this hero in the wild.",
        "Full stats, structured skills, and lore unlock once this hero joins your roster.",
    ]


def _unknown_detail_lines() -> List[str]:
    return [
        f"{Fore.LIGHTBLACK_EX}Silhouette Entry{Fore.RESET}",
        "This hero remains unknown.",
        "Encounter the hero during missions, exploration, or battle reports to reveal their identity.",
    ]


def _hero_filters_summary(filters: Dict[str, Any]) -> str:
    return (
        f"Element: {filters['element'] or 'All'} | Rarity: {filters['rarity'] or 'All'} | "
        f"Tag: {filters['style_tag'] or 'All'} | Ownership: {filters['ownership']} | "
        f"Search: {filters['search'] or '-'} | Favorites: {'On' if filters['favorites_only'] else 'Off'} | "
        f"Sort: {SORT_OPTIONS[filters['sort']]}"
    )


def _prompt_choice(label: str, options: List[str], include_all: bool = True) -> str | None:
    while True:
        clear()
        lines = []
        if include_all:
            lines.append("[0] All")
        for index, option in enumerate(options, start=1):
            lines.append(f"[{index}] {option}")
        lines.append("[x] Cancel")
        sp(panel(label, lines, color=Fore.LIGHTBLUE_EX))
        choice = sin(f"{Fore.CYAN}Choose: {Fore.RESET}").strip().lower()
        if choice == "x":
            return None
        if include_all and choice == "0":
            return ""
        if choice.isdigit():
            value = int(choice)
            if 1 <= value <= len(options):
                return options[value - 1]


def _toggle_favorite(stats: Dict[str, Any], hero_id: str) -> bool:
    entry = _hero_codex(stats).setdefault(hero_id, {"state": DEFAULT_CATALOG_STATE, "favorite": False, "encountered_at": 0})
    entry["favorite"] = not bool(entry.get("favorite", False))
    return bool(entry["favorite"])


def _encounter_hero(stats: Dict[str, Any], source_name: str, focus_elements: List[str]) -> Dict[str, Any] | None:
    codex = _hero_codex(stats)
    owned_ids = set(_owned_heroes(stats).keys())
    candidates = [
        hero
        for hero in load_hero_catalog()
        if hero["id"] not in owned_ids
        and codex.get(hero["id"], {}).get("state", DEFAULT_CATALOG_STATE) == DEFAULT_CATALOG_STATE
        and hero["element"] in focus_elements
    ]
    if not candidates:
        candidates = [
            hero
            for hero in load_hero_catalog()
            if hero["id"] not in owned_ids
            and codex.get(hero["id"], {}).get("state", DEFAULT_CATALOG_STATE) == DEFAULT_CATALOG_STATE
        ]
    if not candidates:
        return None
    hero = random.choice(candidates)
    entry = codex.setdefault(hero["id"], {"state": DEFAULT_CATALOG_STATE, "favorite": False, "encountered_at": 0})
    entry["state"] = ENCOUNTERED_CATALOG_STATE
    entry["encountered_at"] = int(time.time())
    _deliver_mail(
        stats,
        f"Hero Encountered: {hero['name']}",
        f"You spotted {hero['name']} during {source_name}. Their codex silhouette has become a real identity entry.",
        tag="Codex",
    )
    return hero


def _recruit_random_hero(stats: Dict[str, Any], source_name: str, focus_elements: List[str]) -> Dict[str, Any] | None:
    codex = _hero_codex(stats)
    owned = _owned_heroes(stats)
    candidates = [
        hero
        for hero in load_hero_catalog()
        if hero["id"] not in owned
        and codex.get(hero["id"], {}).get("state") == ENCOUNTERED_CATALOG_STATE
        and hero["element"] in focus_elements
    ]
    if not candidates:
        candidates = [
            hero
            for hero in load_hero_catalog()
            if hero["id"] not in owned and hero["element"] in focus_elements
        ]
    if not candidates:
        candidates = [hero for hero in load_hero_catalog() if hero["id"] not in owned]
    if not candidates:
        return None
    hero = random.choice(candidates)
    owned[hero["id"]] = {"id": hero["id"], "level": 1, "rank": 1, "soul_stones": 0}
    entry = codex.setdefault(hero["id"], {"state": OWNED_CATALOG_STATE, "favorite": False, "encountered_at": 0})
    entry["state"] = OWNED_CATALOG_STATE
    if not entry.get("encountered_at"):
        entry["encountered_at"] = int(time.time())
    _battle_record(stats)["Heroes Recruited"] = int(_battle_record(stats).get("Heroes Recruited", 0)) + 1
    _deliver_mail(
        stats,
        f"New Hero Recruited: {hero['name']}",
        f"{hero['name']} answered your call after {source_name}. Full stats and skills are now unlocked in Heroes.",
        tag="Recruit",
    )
    return merge_owned_hero(hero["id"], owned[hero["id"]])


def _activity_resolution(stats: Dict[str, Any], recommended: int, xp_reward: int, gold_reward: int) -> bool:
    squad_power = _squad_power(stats)
    commander_bonus = int(stats.get("Buffs", {}).get("ATK", 0)) + int(stats.get("Buffs", {}).get("HP", 0) / 10)
    score = squad_power + commander_bonus
    success_rate = max(0.24, min(0.92, 0.44 + ((score - recommended) / 360.0)))
    if random.random() <= success_rate:
        stats["Gold"] = int(stats.get("Gold", 0)) + gold_reward
        stats["Exp"] = int(stats.get("Exp", 0)) + xp_reward
        return True
    return False


def _exp_target(stats: Dict[str, Any]) -> int:
    return int(stats.get("Lvl", 1)) * 100


def _check_level_up(stats: Dict[str, Any]) -> bool:
    lvl = int(stats.get("Lvl", 1))
    exp = int(stats.get("Exp", 0))
    required = _exp_target(stats)
    leveled = False
    while exp >= required:
        exp -= required
        lvl += 1
        leveled = True
        stats["Skill Points"] = int(stats.get("Skill Points", 0)) + 1
        required = lvl * 100
    if leveled:
        stats["Lvl"] = lvl
        stats["Exp"] = exp
        level_up_celebration(lvl)
        toast_notification(f"Level {lvl} reached! Skill Point +1", toast_type="level_up")
    return leveled


def skill_tree(stats: Dict[str, Any]) -> None:
    sync_player_data(stats)
    exit_option = len(SKILL_TREE_BRANCHES) + 1

    while True:
        clear()
        sp(f"{Fore.LIGHTMAGENTA_EX}{Style.BRIGHT}Skill Tree{Style.RESET_ALL}")
        sp(f"{Fore.CYAN}Skill Points Available: {stats['Skill Points']}{Fore.RESET}")
        sp(f"{Fore.YELLOW}Upgrade your commander to boost every mission run.{Fore.RESET}\n")

        sp(f"{Fore.LIGHTWHITE_EX}{Style.BRIGHT}Current Buff Totals{Style.RESET_ALL}")
        for branch in SKILL_TREE_BRANCHES:
            color = SKILL_TREE_COLORS.get(branch, Fore.WHITE)
            sp(f"{color}{branch:<14}{Fore.RESET}: {stats['Buffs'][branch]}")

        sp(f"\n{Fore.LIGHTWHITE_EX}{Style.BRIGHT}Upgrade Branches{Style.RESET_ALL}")
        for index, branch in enumerate(SKILL_TREE_BRANCHES, start=1):
            color = SKILL_TREE_COLORS.get(branch, Fore.WHITE)
            current_level = stats["Skill Tree"][branch]
            next_level = current_level + 1
            cost = current_level
            bonus = SKILL_TREE_BONUSES[branch]
            sp(
                f"{color}[{index}] {branch}{Fore.RESET} | Current Lv {current_level} | "
                f"Next Lv {next_level} | Cost {cost} SP | Gain +{bonus} {branch}"
            )

        sp(f"{Fore.LIGHTRED_EX}[{exit_option}] Exit Skill Tree{Fore.RESET}")
        choice = sin(f"\n{Fore.CYAN}Choose a branch to upgrade: {Fore.RESET}").strip()

        if choice == str(exit_option):
            _persist_stats(stats)
            return

        if not choice.isdigit() or not 1 <= int(choice) <= len(SKILL_TREE_BRANCHES):
            sp(f"{Fore.RED}Invalid choice! Pick one of the branch numbers.{Fore.RESET}")
            time.sleep(1.3)
            continue

        branch = SKILL_TREE_BRANCHES[int(choice) - 1]
        cost = stats["Skill Tree"][branch]
        if stats["Skill Points"] < cost:
            sp(f"{Fore.RED}Not enough skill points for {branch}. You need {cost} SP.{Fore.RESET}")
            time.sleep(1.3)
            continue

        stats["Skill Points"] -= cost
        stats["Skill Tree"][branch] += 1
        stats["Buffs"][branch] += SKILL_TREE_BONUSES[branch]
        _persist_stats(stats)

        sp(
            f"{Fore.LIGHTGREEN_EX}{branch} upgraded to Level {stats['Skill Tree'][branch]}! "
            f"+{SKILL_TREE_BONUSES[branch]} {branch} applied.{Fore.RESET}"
        )
        skill_unlock_burst(branch)
        time.sleep(0.8)


def heroes_menu(stats: Dict[str, Any]) -> None:
    filters = {
        "element": None,
        "rarity": None,
        "style_tag": None,
        "ownership": "all",
        "search": "",
        "favorites_only": False,
        "sort": "default",
    }
    page = 0

    while True:
        rows = sort_rows(
            filter_rows(
                build_visible_rows(_hero_codex(stats), _owned_heroes(stats), include_legacy_owned=True),
                element=filters["element"],
                rarity=filters["rarity"],
                style_tag=filters["style_tag"],
                ownership=filters["ownership"],
                search=filters["search"],
                favorites_only=filters["favorites_only"],
            ),
            mode=filters["sort"],
        )
        total_pages = max(1, (len(rows) + PAGE_SIZE - 1) // PAGE_SIZE)
        page = min(page, total_pages - 1)
        start = page * PAGE_SIZE
        visible_rows = rows[start:start + PAGE_SIZE]
        counts = _codex_counts(stats)

        clear()
        lines = [
            f"Owned {counts[OWNED_CATALOG_STATE]} / 144 | Encountered {counts[ENCOUNTERED_CATALOG_STATE]} | Unknown {counts[DEFAULT_CATALOG_STATE]}",
            _hero_filters_summary(filters),
            f"Page {page + 1}/{total_pages} | Showing {len(visible_rows)} of {len(rows)} results",
            "",
        ]
        for index, row in enumerate(visible_rows, start=1):
            lines.append(f"[{index}] {_hero_list_line(row)}")
        if not visible_rows:
            lines.append("No heroes match the current filters.")
        lines.extend(
            [
                "",
                "[n] Next page    [p] Previous page",
                "[e] Element / quick jump    [r] Rarity    [t] Style tag",
                "[o] Ownership    [s] Search    [f] Favorites only",
                "[m] Sort mode    [c] Clear filters",
                "[0] Back",
            ]
        )
        sp(panel("Hero Encyclopedia", lines, color=Fore.LIGHTMAGENTA_EX))
        choice = sin(f"{Fore.CYAN}Choose a hero or command: {Fore.RESET}").strip().lower()
        if choice == "0":
            _persist_stats(stats)
            return
        if choice == "n":
            page = min(total_pages - 1, page + 1)
            continue
        if choice == "p":
            page = max(0, page - 1)
            continue
        if choice == "e":
            selected = _prompt_choice("Element Filter / Quick Jump", HERO_ELEMENTS)
            if selected is not None:
                filters["element"] = selected or None
                page = 0
            continue
        if choice == "r":
            selected = _prompt_choice("Rarity Filter", HERO_RARITIES)
            if selected is not None:
                filters["rarity"] = selected or None
                page = 0
            continue
        if choice == "t":
            selected = _prompt_choice("Style Tag Filter", HERO_STYLE_TAGS)
            if selected is not None:
                filters["style_tag"] = selected or None
                page = 0
            continue
        if choice == "o":
            selected = _prompt_choice("Ownership Filter", ["all", "owned", "unowned"], include_all=False)
            if selected:
                filters["ownership"] = selected
                page = 0
            continue
        if choice == "s":
            value = sin(f"{Fore.CYAN}Search name (blank clears): {Fore.RESET}").strip()
            filters["search"] = value
            page = 0
            continue
        if choice == "f":
            filters["favorites_only"] = not filters["favorites_only"]
            page = 0
            continue
        if choice == "m":
            selected = _prompt_choice("Sort Mode", [f"{key}: {label}" for key, label in SORT_OPTIONS.items()], include_all=False)
            if selected:
                filters["sort"] = selected.split(":", 1)[0]
                page = 0
            continue
        if choice == "c":
            filters = {
                "element": None,
                "rarity": None,
                "style_tag": None,
                "ownership": "all",
                "search": "",
                "favorites_only": False,
                "sort": "default",
            }
            page = 0
            continue
        if choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(visible_rows):
                row = visible_rows[index]
                hero_id = row["id"]
                while True:
                    clear()
                    if row["state"] == OWNED_CATALOG_STATE:
                        detail_lines = _owned_detail_lines(row)
                    elif row["state"] == ENCOUNTERED_CATALOG_STATE:
                        detail_lines = _encountered_detail_lines(row)
                    else:
                        detail_lines = _unknown_detail_lines()
                    detail_lines.extend(["", "[v] Toggle favorite", "[0] Back"])
                    sp(panel("Hero Detail", detail_lines, color=_element_color(row.get("element", "Arcane"))))
                    action = sin(f"{Fore.CYAN}Choose: {Fore.RESET}").strip().lower()
                    if action == "0":
                        break
                    if action == "v" and row["state"] != DEFAULT_CATALOG_STATE:
                        favorite = _toggle_favorite(stats, hero_id)
                        row["favorite"] = favorite
                        sp(f"{Fore.LIGHTGREEN_EX}{'Favorited' if favorite else 'Removed from favorites'} {row.get('name', 'hero')}.{Fore.RESET}")
                        time.sleep(0.9)
                        _persist_stats(stats)
                continue


def missions_menu(stats: Dict[str, Any]) -> None:
    while True:
        clear()
        lines = [
            f"Account: {stats['Account Name']} | Squad Power: {_squad_power(stats)} | Gold: {stats['Gold']} | Exp: {stats['Exp']}/{_exp_target(stats)}",
            "",
        ]
        for index, mission in enumerate(MISSION_BOARD, start=1):
            elements = ", ".join(mission["focus_elements"])
            lines.append(
                f"[{index}] {mission['name']} | Rec {mission['recommended']} | Reward {mission['gold']} Gold + {mission['xp']} XP"
            )
            lines.append(f"    {mission['theme']} | Focus: {elements}")
        lines.append("[0] Back")
        sp(panel("Mission Board", lines, color=Fore.LIGHTBLUE_EX))

        choice = sin(f"{Fore.CYAN}Launch which mission? {Fore.RESET}").strip()
        if choice == "0":
            return
        if not choice.isdigit() or not 1 <= int(choice) <= len(MISSION_BOARD):
            sp(f"{Fore.RED}Pick a mission number from the board.{Fore.RESET}")
            time.sleep(1.1)
            continue

        mission = MISSION_BOARD[int(choice) - 1]
        arcane_cataclysm(f"MISSION START :: {mission['name']}")
        sp(f"{Fore.LIGHTYELLOW_EX}{mission['theme']}{Fore.RESET}")
        time.sleep(0.9)

        if random.random() < mission["encounter_chance"]:
            encountered = _encounter_hero(stats, mission["name"], mission["focus_elements"])
            if encountered:
                sp(f"{Fore.CYAN}Encountered: {encountered['name']} is now visible in the encyclopedia.{Fore.RESET}")
                time.sleep(0.9)

        if _activity_resolution(stats, mission["recommended"], mission["xp"], mission["gold"]):
            _battle_record(stats)["Missions Completed"] = int(_battle_record(stats).get("Missions Completed", 0)) + 1
            neon_flicker(f"Mission clear! +{mission['gold']} Gold | +{mission['xp']} XP", cycles=2)
            if random.random() < mission["hero_chance"]:
                hero = _recruit_random_hero(stats, mission["name"], mission["focus_elements"])
                if hero:
                    fireworks(count=4, duration=0.6)
                    sp(f"{Fore.LIGHTGREEN_EX}New hero recruited: {hero['name']}!{Fore.RESET}")
            _deliver_mail(
                stats,
                f"Mission Report: {mission['name']}",
                f"Success. Your squad cleared the objective and returned with {mission['gold']} Gold and {mission['xp']} XP.",
                tag="Mission",
            )
            _check_level_up(stats)
        else:
            _battle_record(stats)["Missions Failed"] = int(_battle_record(stats).get("Missions Failed", 0)) + 1
            sp(f"{Fore.RED}The mission slipped away this time. Your heroes retreat to regroup.{Fore.RESET}")
            _deliver_mail(
                stats,
                f"Mission Report: {mission['name']}",
                "The operation fell short. Strengthen your roster or commander buffs before retrying.",
                tag="Mission",
            )

        _persist_stats(stats)
        sin(f"\n{Fore.LIGHTCYAN_EX}Press ENTER to return to the mission board.{Fore.RESET}")


def explore_menu(stats: Dict[str, Any]) -> None:
    while True:
        clear()
        lines = [
            f"Account: {stats['Account Name']} | Squad Power: {_squad_power(stats)} | Unread Mail: {_unread_mail_count(stats)}",
            "",
        ]
        for index, zone in enumerate(EXPLORE_ZONES, start=1):
            elements = ", ".join(zone["focus_elements"])
            lines.append(
                f"[{index}] {zone['name']} | Rec {zone['recommended']} | Finds up to {zone['gold']} Gold + {zone['xp']} XP"
            )
            lines.append(f"    {zone['theme']} | Focus: {elements}")
        lines.append("[0] Back")
        sp(panel("Explore the Frontier", lines, color=Fore.LIGHTGREEN_EX))

        choice = sin(f"{Fore.CYAN}Explore which zone? {Fore.RESET}").strip()
        if choice == "0":
            return
        if not choice.isdigit() or not 1 <= int(choice) <= len(EXPLORE_ZONES):
            sp(f"{Fore.RED}Choose a zone from the list.{Fore.RESET}")
            time.sleep(1.1)
            continue

        zone = EXPLORE_ZONES[int(choice) - 1]
        starfield_background(duration=0.35, star_count=35)
        sp(f"{Fore.CYAN}Your squad scouts {zone['name']}...{Fore.RESET}")
        time.sleep(0.8)

        _battle_record(stats)["Explorations"] = int(_battle_record(stats).get("Explorations", 0)) + 1
        if random.random() < zone["encounter_chance"]:
            encountered = _encounter_hero(stats, zone["name"], zone["focus_elements"])
            if encountered:
                sp(f"{Fore.CYAN}Encountered: {encountered['name']} joins your codex as a visible entry.{Fore.RESET}")
                time.sleep(0.9)

        if _activity_resolution(stats, zone["recommended"], zone["xp"], zone["gold"]):
            sp(f"{Fore.LIGHTGREEN_EX}Exploration success! Supplies and intel recovered.{Fore.RESET}")
            if random.random() < zone["hero_chance"]:
                hero = _recruit_random_hero(stats, zone["name"], zone["focus_elements"])
                if hero:
                    sp(f"{Fore.LIGHTYELLOW_EX}{hero['name']} was discovered during the expedition!{Fore.RESET}")
            _deliver_mail(
                stats,
                f"Exploration Log: {zone['name']}",
                f"Your squad charted new territory and returned with {zone['gold']} Gold and {zone['xp']} XP worth of progress.",
                tag="Explore",
            )
            _check_level_up(stats)
        else:
            consolation_gold = max(20, zone["gold"] // 3)
            stats["Gold"] = int(stats.get("Gold", 0)) + consolation_gold
            sp(f"{Fore.YELLOW}The route was rough, but your heroes still brought back {consolation_gold} Gold in supplies.{Fore.RESET}")
            _deliver_mail(
                stats,
                f"Exploration Log: {zone['name']}",
                f"The route turned hostile. Your heroes still salvaged {consolation_gold} Gold worth of supplies.",
                tag="Explore",
            )

        _persist_stats(stats)
        sin(f"\n{Fore.LIGHTCYAN_EX}Press ENTER to return to the frontier map.{Fore.RESET}")


def battle_menu(stats: Dict[str, Any]) -> None:
    while True:
        clear()
        lines = [
            f"Account: {stats['Account Name']} | Squad Power: {_squad_power(stats)} | Wins: {_battle_record(stats).get('Battles Won', 0)} | Losses: {_battle_record(stats).get('Battles Lost', 0)}",
            "",
        ]
        for index, enemy in enumerate(BATTLE_QUEUE, start=1):
            boss_marker = "Boss" if enemy["boss"] else "Skirmish"
            elements = ", ".join(enemy["focus_elements"])
            lines.append(
                f"[{index}] {enemy['name']} | {boss_marker} | Rec {enemy['recommended']} | Reward {enemy['gold']} Gold + {enemy['xp']} XP"
            )
            lines.append(f"    {enemy['theme']} | Focus: {elements}")
        lines.append("[0] Back")
        sp(panel("Battle Queue", lines, color=Fore.LIGHTRED_EX))

        choice = sin(f"{Fore.CYAN}Challenge which enemy? {Fore.RESET}").strip()
        if choice == "0":
            return
        if not choice.isdigit() or not 1 <= int(choice) <= len(BATTLE_QUEUE):
            sp(f"{Fore.RED}Choose one of the listed opponents.{Fore.RESET}")
            time.sleep(1.1)
            continue

        enemy = BATTLE_QUEUE[int(choice) - 1]
        arcane_cataclysm(f"BATTLE START :: {enemy['name']}")
        squad_names = ", ".join(hero["name"] for hero in _top_squad(stats)) or "No heroes ready"
        sp(f"{Fore.LIGHTMAGENTA_EX}Front squad:{Fore.RESET} {squad_names}")
        time.sleep(0.8)

        if random.random() < enemy["encounter_chance"]:
            encountered = _encounter_hero(stats, enemy["name"], enemy["focus_elements"])
            if encountered:
                sp(f"{Fore.CYAN}Encountered: {encountered['name']} survives the clash as a new codex sighting.{Fore.RESET}")
                time.sleep(0.9)

        if _activity_resolution(stats, enemy["recommended"], enemy["xp"], enemy["gold"]):
            _battle_record(stats)["Battles Won"] = int(_battle_record(stats).get("Battles Won", 0)) + 1
            if enemy["boss"]:
                _battle_record(stats)["Bosses Defeated"] = int(_battle_record(stats).get("Bosses Defeated", 0)) + 1
            sp(f"{Fore.LIGHTGREEN_EX}Victory! {enemy['name']} is down.{Fore.RESET}")
            _deliver_mail(
                stats,
                f"Battle Result: {enemy['name']}",
                f"Your heroes won the fight and secured {enemy['gold']} Gold plus {enemy['xp']} XP.",
                tag="Battle",
            )
            _check_level_up(stats)
        else:
            _battle_record(stats)["Battles Lost"] = int(_battle_record(stats).get("Battles Lost", 0)) + 1
            sp(f"{Fore.RED}Defeat. The squad falls back before the enemy can finish the job.{Fore.RESET}")
            _deliver_mail(
                stats,
                f"Battle Result: {enemy['name']}",
                "The battle was lost. Upgrade your commander or recruit stronger heroes before the rematch.",
                tag="Battle",
            )

        _persist_stats(stats)
        sin(f"\n{Fore.LIGHTCYAN_EX}Press ENTER to return to the battle queue.{Fore.RESET}")


def stats_page(stats: Dict[str, Any]) -> None:
    clear()
    record = _battle_record(stats)
    exp_target = _exp_target(stats)
    wins = int(record.get("Battles Won", 0))
    losses = int(record.get("Battles Lost", 0))
    total_battles = wins + losses
    win_rate = 0 if total_battles == 0 else int(round((wins / total_battles) * 100))
    commander_element = COMMANDER_ELEMENT_NAMES.get(stats.get("Commander"), "Arcane")
    codex = _codex_counts(stats)
    lines = [
        f"Account Name: {Fore.LIGHTYELLOW_EX}{stats['Account Name']}{Fore.RESET}",
        f"Commander: {_element_color(commander_element)}{stats['Commander']}{Fore.RESET} | Element {commander_element}",
        f"Level: {stats['Lvl']} | Exp: {stats['Exp']}/{exp_target} | Skill Points: {stats['Skill Points']}",
        f"Owned Heroes: {codex[OWNED_CATALOG_STATE]} | Encountered: {codex[ENCOUNTERED_CATALOG_STATE]} | Unknown: {codex[DEFAULT_CATALOG_STATE]}",
        f"Squad Power: {_squad_power(stats)} | Unread Mail: {_unread_mail_count(stats)}",
        f"Missions Completed: {record.get('Missions Completed', 0)} | Missions Failed: {record.get('Missions Failed', 0)}",
        f"Explorations: {record.get('Explorations', 0)} | Bosses Defeated: {record.get('Bosses Defeated', 0)}",
        f"Battles Won: {wins} | Battles Lost: {losses} | Win Rate: {win_rate}%",
        f"Heroes Recruited: {record.get('Heroes Recruited', 0)}",
    ]
    sp(panel("Commander Stats", lines, color=Fore.LIGHTCYAN_EX))
    sin(f"\n{Fore.LIGHTCYAN_EX}Press ENTER to return to Command Nexus.{Fore.RESET}")


def _ai_bot_lines(stats: Dict[str, Any], mode: str) -> List[str]:
    bot_name = stats.get("AI Bot", {}).get("name", "ASTRA")
    squad_power = _squad_power(stats)
    unread = _unread_mail_count(stats)
    record = _battle_record(stats)
    codex = _codex_counts(stats)

    if mode == "roster":
        squad = _top_squad(stats)
        front_line = ", ".join(f"{hero['name']} ({hero['power']})" for hero in squad) or "No owned squad"
        return [
            f"{bot_name} Roster Scan",
            f"Front Squad: {front_line}",
            f"Owned {codex[OWNED_CATALOG_STATE]} / 144 | Encountered {codex[ENCOUNTERED_CATALOG_STATE]} | Squad Power {squad_power}",
            "Advice: use Heroes to filter by element and rarity when planning the next recruit target.",
        ]
    if mode == "missions":
        next_mission = min(MISSION_BOARD, key=lambda mission: abs(mission["recommended"] - squad_power))
        return [
            f"{bot_name} Mission Scan",
            f"Best Fit Right Now: {next_mission['name']}",
            f"Recommended Power: {next_mission['recommended']} | Your Squad: {squad_power}",
            "Advice: if your codex has many encountered heroes, keep pushing missions and exploration to turn sightings into recruits.",
        ]
    return [
        f"{bot_name} Mail Scan",
        f"Unread Messages: {unread}",
        f"Mission Clears: {record.get('Missions Completed', 0)} | Battles Won: {record.get('Battles Won', 0)}",
        "Advice: codex encounter notices arrive through the mailbox, so check recent reports after every run.",
    ]


def ai_bot_menu(stats: Dict[str, Any]) -> None:
    while True:
        clear()
        bot_name = stats.get("AI Bot", {}).get("name", "ASTRA")
        lines = [
            f"{bot_name} Status: {stats.get('AI Bot', {}).get('status', 'Online')}",
            "A tactical assistant for roster, mission, and mailbox guidance.",
            "",
            "[1] Squad Advice",
            "[2] Mission Advice",
            "[3] Mailbox Summary",
            "[0] Back",
        ]
        sp(panel("AI Bot", lines, color=Fore.LIGHTYELLOW_EX))
        choice = sin(f"{Fore.CYAN}Choose an AI scan: {Fore.RESET}").strip()
        if choice == "0":
            return
        if choice not in {"1", "2", "3"}:
            sp(f"{Fore.RED}Pick one of the AI Bot options.{Fore.RESET}")
            time.sleep(1.1)
            continue

        mode = {"1": "roster", "2": "missions", "3": "mail"}[choice]
        clear()
        sp(panel(bot_name, _ai_bot_lines(stats, mode), color=Fore.LIGHTYELLOW_EX))
        sin(f"\n{Fore.LIGHTCYAN_EX}Press ENTER to return to the AI Bot console.{Fore.RESET}")


def mailbox_menu(stats: Dict[str, Any]) -> None:
    while True:
        clear()
        mails = list(reversed(_mailbox(stats)))
        lines = [f"Unread Mail: {_unread_mail_count(stats)}", ""]
        if not mails:
            lines.append("No mail yet.")
        for index, mail in enumerate(mails, start=1):
            marker = f"{Fore.LIGHTGREEN_EX}NEW{Fore.RESET}" if not mail.get("read") else "Read"
            stamp = time.strftime("%m/%d %H:%M", time.localtime(int(mail.get("at", time.time()))))
            lines.append(f"[{index}] {marker} | {mail.get('tag', 'Mail')} | {mail.get('subject', 'Untitled')} | {stamp}")
        lines.append("[0] Back")
        sp(panel("Mailbox", lines, color=Fore.LIGHTGREEN_EX))

        choice = sin(f"{Fore.CYAN}Open which message? {Fore.RESET}").strip()
        if choice == "0":
            _persist_stats(stats)
            return
        if not choice.isdigit() or not 1 <= int(choice) <= len(mails):
            sp(f"{Fore.RED}Choose one of the listed messages.{Fore.RESET}")
            time.sleep(1.1)
            continue

        mail = mails[int(choice) - 1]
        mail["read"] = True
        clear()
        body_lines = [
            f"Tag: {mail.get('tag', 'Mail')}",
            f"Subject: {mail.get('subject', 'Untitled')}",
            "",
            mail.get("body", ""),
        ]
        sp(panel("Message", body_lines, color=Fore.LIGHTGREEN_EX))
        _persist_stats(stats)
        sin(f"\n{Fore.LIGHTCYAN_EX}Press ENTER to return to the mailbox.{Fore.RESET}")


def _front_panel_lines(stats: Dict[str, Any]) -> List[str]:
    commander_element = COMMANDER_ELEMENT_NAMES.get(stats.get("Commander"), "Arcane")
    squad_names = ", ".join(hero["name"] for hero in _top_squad(stats)) or "No heroes yet"
    codex = _codex_counts(stats)
    return [
        f"Account Name: {Fore.LIGHTYELLOW_EX}{Style.BRIGHT}{stats['Account Name']}{Style.RESET_ALL}{Fore.RESET}",
        f"Commander: {_element_color(commander_element)}{stats['Commander']}{Fore.RESET} | Element {commander_element}",
        f"Owned Heroes: {codex[OWNED_CATALOG_STATE]} / 144 | Encountered: {codex[ENCOUNTERED_CATALOG_STATE]} | Unknown: {codex[DEFAULT_CATALOG_STATE]}",
        f"Squad Power: {_squad_power(stats)} | Level: {stats['Lvl']} | Skill Points: {stats['Skill Points']}",
        f"Unread Mail: {_unread_mail_count(stats)} | AI Bot: {stats.get('AI Bot', {}).get('name', 'ASTRA')} online",
        f"Front Squad: {squad_names}",
    ]


def main() -> None:
    stats = welcome()
    sync_player_data(stats)
    _persist_stats(stats)

    starfield_background(duration=0.35, star_count=50)

    while True:
        clear()
        sp(header_art())
        sp(rainbow_text("ARCANE HEROES :: COMMAND NEXUS"))
        sp(status_bar("Collect heroes. Expand the codex. Run missions. Explore. Battle."))
        sp("")
        sp(panel(f"Account Deck :: {stats['Account Name']}", _front_panel_lines(stats), color=Fore.LIGHTCYAN_EX))
        sp(
            panel(
                "Choose Your Next Move",
                [
                    menu_option("1", "Heroes", "🛡️", Fore.LIGHTMAGENTA_EX),
                    menu_option("2", "Missions", "📜", Fore.LIGHTBLUE_EX),
                    menu_option("3", "Explore", "🧭", Fore.LIGHTGREEN_EX),
                    menu_option("4", "Battle", "⚔️", Fore.LIGHTRED_EX),
                    menu_option("5", "Stats", "📊", Fore.LIGHTCYAN_EX),
                    menu_option("6", "Skill Tree", "✨", Fore.YELLOW),
                    menu_option("7", "AI Bot", "🤖", Fore.LIGHTYELLOW_EX),
                    menu_option("8", "Mailbox", "📬", Fore.LIGHTGREEN_EX),
                    menu_option("10", "Exit", "⛔", Fore.LIGHTWHITE_EX),
                ],
                color=Fore.LIGHTMAGENTA_EX,
            )
        )

        option = sin(f"\n{Fore.CYAN}Choose a command: {Fore.RESET}").strip()
        clear()

        if option == "1":
            heroes_menu(stats)
        elif option == "2":
            missions_menu(stats)
        elif option == "3":
            explore_menu(stats)
        elif option == "4":
            battle_menu(stats)
        elif option == "5":
            stats_page(stats)
        elif option == "6":
            skill_tree(stats)
        elif option == "7":
            ai_bot_menu(stats)
        elif option == "8":
            mailbox_menu(stats)
        elif option == "10":
            _persist_stats(stats)
            return
        else:
            sp(f"{Fore.RED}Choose one of the available commands.{Fore.RESET}")
            time.sleep(1.1)
        _ambient_transition()


if __name__ == "__main__":
    main()
