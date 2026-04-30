import os
import platform
import random
import sys
import subprocess
import json
import threading
import time
from colorama import Fore, Style
from typing import Any, Dict

from config import (
    SKILL_TREE_BONUSES,
    COMMANDER_ELEMENTS,
    COMMANDER_ELEMENT_NAMES,
    COMMANDER_NAMES,
    SKILL_TREE_BRANCHES,
    PLAYERS_FILE,
    PANEL_WIDTH,
)
from hero_data import (
    OWNED_CATALOG_STATE,
    build_default_codex,
    normalize_owned_hero,
    starter_hero_ids,
)
from ui import (
    ensure_colorama,
    clear,
    clear_last_line,
    typed_print,
    fast_typed_print,
    progress_bar,
    line,
    title,
    panel,
    prompt,
    header_art,
    small_header,
    footer_art,
    status_bar,
    menu_option,
    info_line,
    divider,
    sp,
    sin,
    crazy_transition,
    starfield_background,
    matrix_rain,
    rainbow_text,
    color_cycle_print,
    thunder_effect,
    neon_flicker,
    explosion_print,
    shimmer_line,
    jitter_text,
    flash_screen,
    emoji_explosion,
    fireworks,
    orbiting_dots,
    typing_burst,
    scanline_reveal,
    pulsing_border,
)


def creating_account_animation(name: str) -> None:
    bar_length = 40
    clear()
    sp(f"{Fore.LIGHTCYAN_EX}{Style.BRIGHT}Creating account for {Fore.MAGENTA}{name}{Fore.RESET}{Style.RESET_ALL}")
    for i in range(bar_length + 1):
        percent = int((i / bar_length) * 100)
        bar = "=" * i + " " * (bar_length - i)
        sys.stdout.write(f"\r{Fore.GREEN}[{bar}]{Fore.RESET} {percent}%")
        sys.stdout.flush()
        time.sleep(random.choice([0.075, 0.08, 0.09, 0.1, 0.065, 0.06, 1.01]))
    sp(f"\n{Fore.LIGHTGREEN_EX}Account successfully created! Welcome, {name}!{Fore.RESET}")
    fireworks(count=5, duration=0.8)
    emoji_explosion("✨", count=20)
    time.sleep(0.5)
    clear()


def login_animation(name: str) -> None:
    bar_length = 30
    clear()
    sp(f"{Fore.CYAN}{Style.BRIGHT}Accessing Arcane Archives for {Fore.MAGENTA}{name}{Fore.CYAN}...{Style.RESET_ALL}")
    for i in range(bar_length + 1):
        percent = int((i / bar_length) * 100)
        bar = "■" * i + " " * (bar_length - i)
        sys.stdout.write(f"\r{Fore.GREEN}[{bar}]{Fore.RESET} {percent}%")
        sys.stdout.flush()
        time.sleep(random.choice([0.075, 0.08, 0.09, 0.1, 0.065, 0.06, 1.01]))
    sp(f"\n{Fore.LIGHTGREEN_EX}🔓 Login successful! Welcome back, {name}!{Fore.RESET}")
    thunder_effect(f"🔓 Login successful! Welcome back, {name}!")
    color_cycle_print(f"Welcome back, {name}!", duration=0.6)
    time.sleep(0.5)
    clear()


progress = {
    "start_time": None,
    "duration": None,
    "done": False,
    "item": None,
}


def worker(item: str, duration: float, action_text: str) -> None:
    progress["start_time"] = time.time()
    progress["duration"] = duration
    progress["done"] = False
    progress["item"] = item
    while True:
        elapsed = time.time() - progress["start_time"]
        percent = min(100, int((elapsed / duration) * 100))
        remaining = max(0.0, duration - elapsed)

        clear()
        sp(f"🛠️ {action_text} {item}...", color=Fore.LIGHTYELLOW_EX)
        sp(progress_bar(percent))
        sp(f"  ⏳ {remaining:.1f}s left", color=Fore.LIGHTWHITE_EX)

        if elapsed >= duration:
            break
        time.sleep(0.1)

    progress["done"] = True
    clear()


def start(item: str, action: str, lower: float, upper: float) -> None:
    worker(item, random.uniform(lower, upper), action)


def timer_loop(seconds: int) -> None:
    tournament_active = globals().get("tournament_active")
    started_at = time.time()
    while time.time() - started_at < seconds:
        time.sleep(1)
    if isinstance(tournament_active, list) and tournament_active:
        tournament_active[0] = False
    sp("\n🏆 Tournament Over!", color=Fore.LIGHTMAGENTA_EX)


def build_default_skill_tree() -> Dict[str, int]:
    return {branch: 1 for branch in SKILL_TREE_BRANCHES}


def build_default_buffs(commander: str) -> Dict[str, int]:
    buffs = {branch: 0 for branch in SKILL_TREE_BRANCHES}
    elemental_branch = COMMANDER_ELEMENTS.get(commander)
    if elemental_branch:
        buffs[elemental_branch] = 20
    return buffs


def build_default_heroes(commander: str) -> Dict[str, Dict[str, Any]]:
    return {
        hero_id: {
            "id": hero_id,
            "level": 1,
            "rank": 1,
            "soul_stones": 0,
        }
        for hero_id in starter_hero_ids(commander)
    }


def build_default_hero_codex(commander: str) -> Dict[str, Dict[str, Any]]:
    codex = build_default_codex()
    for hero_id in starter_hero_ids(commander):
        codex.setdefault(hero_id, {})
        codex[hero_id]["state"] = OWNED_CATALOG_STATE
        codex[hero_id]["favorite"] = False
        codex[hero_id]["encountered_at"] = 0
    return codex


def build_default_mailbox(name: str, commander: str) -> list[Dict[str, Any]]:
    commander_name = commander or "your Commander"
    return [
        {
            "subject": "Welcome to Arcane Heroes",
            "body": (
                f"Commander {name}, your hero roster is now online. "
                "Head to Heroes to inspect your squad, then start running missions and battles."
            ),
            "tag": "System",
            "read": False,
            "at": int(time.time()),
        },
        {
            "subject": "ASTRA Bot Online",
            "body": (
                f"ASTRA has synced with {commander_name}. "
                "Open the AI Bot menu any time for squad, mission, and mailbox guidance."
            ),
            "tag": "AI",
            "read": False,
            "at": int(time.time()),
        },
    ]


def build_default_battle_record() -> Dict[str, int]:
    return {
        "Missions Completed": 0,
        "Missions Failed": 0,
        "Explorations": 0,
        "Battles Won": 0,
        "Battles Lost": 0,
        "Bosses Defeated": 0,
        "Heroes Recruited": 0,
    }


def build_default_ai_bot() -> Dict[str, Any]:
    return {
        "name": "ASTRA",
        "mode": "Tactical Guide",
        "status": "Online",
    }


def spent_skill_points(skill_tree: Dict[str, int]) -> int:
    total = 0
    for branch in SKILL_TREE_BRANCHES:
        next_level = max(1, int(skill_tree.get(branch, 1)))
        total += (next_level - 1) * next_level // 2
    return total


def sync_player_data(player: Dict[str, Any]) -> bool:
    changed = False
    skill_tree = player.get("Skill Tree")
    if not isinstance(skill_tree, dict):
        skill_tree = build_default_skill_tree()
        player["Skill Tree"] = skill_tree
        changed = True

    for branch in SKILL_TREE_BRANCHES:
        try:
            next_level = int(skill_tree.get(branch, 1))
        except (TypeError, ValueError):
            next_level = 1
        next_level = max(1, next_level)
        if skill_tree.get(branch) != next_level:
            skill_tree[branch] = next_level
            changed = True
        elif branch not in skill_tree:
            skill_tree[branch] = 1
            changed = True

    if "Skill Points" not in player:
        earned_points = max(1, int(player.get("Lvl", 1)))
        player["Skill Points"] = max(0, earned_points - spent_skill_points(skill_tree))
        changed = True

    rebuilt_buffs = build_default_buffs(player.get("Commander", ""))
    for branch in SKILL_TREE_BRANCHES:
        unlocked_levels = max(0, int(skill_tree[branch]) - 1)
        rebuilt_buffs[branch] += unlocked_levels * SKILL_TREE_BONUSES[branch]

    if player.get("Buffs") != rebuilt_buffs:
        player["Buffs"] = rebuilt_buffs
        changed = True

    heroes = player.get("Heroes")
    if not isinstance(heroes, dict) or not heroes:
        player["Heroes"] = build_default_heroes(player.get("Commander", ""))
        heroes = player["Heroes"]
        changed = True
    else:
        normalized_heroes: Dict[str, Dict[str, Any]] = {}
        for hero_id, hero_data in heroes.items():
            normalized = normalize_owned_hero(hero_id, hero_data)
            if normalized != hero_data:
                changed = True
            normalized_heroes[hero_id] = normalized
        if normalized_heroes != heroes:
            player["Heroes"] = normalized_heroes
            heroes = player["Heroes"]
            changed = True

    codex = player.get("Hero Codex")
    if not isinstance(codex, dict):
        player["Hero Codex"] = build_default_hero_codex(player.get("Commander", ""))
        codex = player["Hero Codex"]
        changed = True
    else:
        default_codex = build_default_codex()
        for hero_id, default_entry in default_codex.items():
            entry = codex.get(hero_id)
            if not isinstance(entry, dict):
                codex[hero_id] = dict(default_entry)
                changed = True
                continue
            for key, default_value in default_entry.items():
                if key not in entry:
                    entry[key] = default_value
                    changed = True

    for hero_id in list(heroes.keys()):
        entry = codex.setdefault(hero_id, {"state": OWNED_CATALOG_STATE, "favorite": False, "encountered_at": 0})
        if entry.get("state") != OWNED_CATALOG_STATE:
            entry["state"] = OWNED_CATALOG_STATE
            changed = True
        if "favorite" not in entry:
            entry["favorite"] = False
            changed = True
        if "encountered_at" not in entry:
            entry["encountered_at"] = 0
            changed = True

    if "Mailbox" not in player or not isinstance(player.get("Mailbox"), list):
        player["Mailbox"] = build_default_mailbox(
            player.get("Account Name", "Commander"),
            player.get("Commander", ""),
        )
        changed = True

    ai_bot = player.get("AI Bot")
    default_ai_bot = build_default_ai_bot()
    if not isinstance(ai_bot, dict):
        player["AI Bot"] = default_ai_bot
        changed = True
    else:
        for key, default in default_ai_bot.items():
            if key not in ai_bot:
                ai_bot[key] = default
                changed = True

    battle_record = player.get("Battle Record")
    default_battle_record = build_default_battle_record()
    if not isinstance(battle_record, dict):
        player["Battle Record"] = default_battle_record
        changed = True
    else:
        for key, default in default_battle_record.items():
            if key not in battle_record:
                battle_record[key] = default
                changed = True

    # Ensure economy fields exist for backward compatibility
    for key, default in (
        ("Economy Reputation", 0),
        ("Economy Ledger", []),
        ("Claimed Shop Milestones", [1]),
        ("Shop Level", 1),
        ("Economy Tree", {branch: 0 for branch in [
            "Merchant", "Forge", "Exchange", "Alchemy",
            "Relics", "Logistics", "Barter", "Prestige",
        ]}),
        ("Economy Actions", 0),
        ("Active Permits", []),
        ("Market State", {}),
        ("Item Meta", {}),
        ("Shop Purchase History", {}),
        ("Consumable Buffs", {}),
    ):
        if key not in player:
            player[key] = default
            changed = True

    # Fix reserved_qty over-shooting owned qty
    items = player.get("Items", {})
    item_meta = player.get("Item Meta", {})
    for item_id, qty in list(items.items()):
        meta = item_meta.setdefault(item_id, {"reserved_qty": 0})
        if meta.get("reserved_qty", 0) > qty:
            meta["reserved_qty"] = qty
            changed = True

    return changed


def build_player_stats(name: str, commander: str) -> Dict[str, Any]:
    return {
        "Account Name": name,
        "Commander": commander,
        "Lvl": 1,
        "Exp": 0,
        "Gold": 1000,
        "Skill Points": 1,
        "Skill Tree": build_default_skill_tree(),
        "Heroes": build_default_heroes(commander),
        "Hero Codex": build_default_hero_codex(commander),
        "Equipped Items": {},
        "Items": {},
        "Buffs": build_default_buffs(commander),
        "Mailbox": build_default_mailbox(name, commander),
        "AI Bot": build_default_ai_bot(),
        "Battle Record": build_default_battle_record(),
        "Economy Reputation": 0,
        "Economy Ledger": [],
        "Claimed Shop Milestones": [1],
        "Shop Level": 1,
        "Economy Tree": {branch: 0 for branch in [
            "Merchant", "Forge", "Exchange", "Alchemy",
            "Relics", "Logistics", "Barter", "Prestige",
        ]},
        "Economy Actions": 0,
        "Active Permits": [],
        "Market State": {},
        "Item Meta": {},
        "Shop Purchase History": {},
        "Consumable Buffs": {},
    }


def load_players(filename: str = PLAYERS_FILE) -> Dict[str, Any]:
    if os.path.exists(filename):
        if os.path.getsize(filename) == 0:
            with open(filename, "w") as file:
                json.dump({}, file)
        with open(filename, "r") as file:
            return json.load(file)
    return {}


def save_players(players: Dict[str, Any], filename: str = PLAYERS_FILE) -> None:
    with open(filename, "w") as file:
        json.dump(players, file, indent=4)


def _commander_color(commander: str) -> str:
    mapping = {
        "Pyronis": Fore.LIGHTRED_EX,
        "Aquaryn": Fore.LIGHTBLUE_EX,
        "Terradon": Fore.LIGHTGREEN_EX,
        "Zephyros": Fore.CYAN,
        "Voltaris": Fore.YELLOW,
        "Noctyra": Fore.MAGENTA,
    }
    return mapping.get(commander, Fore.WHITE)


def welcome() -> Dict[str, Any]:
    players = load_players()
    if isinstance(players, dict) and "Account Name" in players and "Commander" in players:
        players = {players["Account Name"]: players}

    players_changed = False
    for player_name, player_data in players.items():
        if isinstance(player_data, dict) and player_data.get("Account Name", player_name):
            if player_data.get("Account Name") != player_name:
                player_data["Account Name"] = player_name
                players_changed = True
            if sync_player_data(player_data):
                players_changed = True
    if players_changed:
        save_players(players)

    clear()

    # Animated intro with starfield and matrix effects
    starfield_background(duration=0.6, star_count=60)
    matrix_rain(duration=0.8, width=100)

    # Animated intro
    prompt_frames = [
        f"{Fore.MAGENTA}🌟 Welcome to Arcane Heroes! 🌟{Fore.RESET}",
        f"{Fore.CYAN}⚔️ Prepare your destiny! ⚔️{Fore.RESET}",
        f"{Fore.YELLOW}✨ Choose your path wisely... ✨{Fore.RESET}",
    ]
    for frame in prompt_frames:
        clear()
        neon_flicker(frame, cycles=2)
        time.sleep(0.3)

    clear()
    sp(header_art())
    shimmer_line(char="═", width=PANEL_WIDTH, cycles=1)
    sp("")
    sp(f"{Fore.LIGHTCYAN_EX}{Style.BRIGHT}Choose Your Adventure{Style.RESET_ALL}{Fore.RESET}")
    sp("")
    sp(menu_option("1", "Register a new hero", "🆕", Fore.LIGHTBLUE_EX))
    sp(menu_option("2", "Login as a returning champion", "🛡️", Fore.LIGHTRED_EX))
    sp("")
    sp(f"  {Fore.LIGHTMAGENTA_EX}Type 1 to start fresh or 2 to continue your quest!{Fore.RESET}")
    shimmer_line(char="═", width=PANEL_WIDTH, cycles=1)

    while True:
        try:
            response = int(prompt("Your choice, brave soul? 👉 "))
            if response in (1, 2):
                break
            sp(f"{Fore.RED}  Please enter 1 or 2 only!{Fore.RESET}")
        except ValueError:
            sp(f"{Fore.RED}  Invalid input! Please enter a number (1 or 2).{Fore.RESET}")

    clear()
    if response == 1:
        sp(header_art())
        sp(f"{Fore.LIGHTCYAN_EX}{Style.BRIGHT}🆕 Registration Portal{Style.RESET_ALL}{Fore.RESET}")
        sp("")
        name = prompt(f"{Fore.MAGENTA}{Style.BRIGHT}Enter your account name: {Style.RESET_ALL}").strip()
        clear()

        if name in players:
            sp(panel("Error", [f"Name '{name}' already exists! Please choose a different name."], color=Fore.RED))
            time.sleep(2)
            return welcome()

        sp(header_art())
        sp(f"{Fore.LIGHTCYAN_EX}{Style.BRIGHT}⚔️ Choose Your Commander{Style.RESET_ALL}{Fore.RESET}")
        sp("")
        sp(rainbow_text("1. Pyronis - Fire"), delay=0.01)
        sp(rainbow_text("2. Aquaryn - Water"), delay=0.01)
        sp(rainbow_text("3. Terradon - Earth"), delay=0.01)
        sp(rainbow_text("4. Zephyros - Air"), delay=0.01)
        sp(rainbow_text("5. Voltaris - Electric"), delay=0.01)
        sp(rainbow_text("6. Noctyra - Shadow"), delay=0.01)
        sp("")

        time.sleep(0.5)
        try:
            commander = int(prompt(f"{Fore.LIGHTMAGENTA_EX}⚔️ Choose your commander (1-6): {Fore.RESET}"))
        except ValueError:
            sp(f"{Fore.RED}Invalid commander choice! Please try again.{Fore.RESET}")
            time.sleep(2)
            return welcome()

        if commander not in COMMANDER_NAMES:
            sp(f"{Fore.RED}Invalid commander choice! Please try again.{Fore.RESET}")
            time.sleep(2)
            return welcome()

        stat = build_player_stats(name, COMMANDER_NAMES[commander])

        creating_account_animation(name)
        players[name] = stat
        save_players(players)
        return stat

    sp(header_art())
    sp(f"{Fore.LIGHTCYAN_EX}{Style.BRIGHT}🔐 Login Portal{Style.RESET_ALL}{Fore.RESET}")
    sp("")
    name = prompt(f"{Fore.MAGENTA}{Style.BRIGHT}Enter your account name: {Style.RESET_ALL}").strip()

    if name not in players:
        sp(panel("Login Failed", [f"❌ Account '{name}' not found! Please register first."], color=Fore.RED))
        time.sleep(2)
        return welcome()

    stat = players[name]
    if sync_player_data(stat):
        players[name] = stat
        save_players(players)

    c_color = _commander_color(stat.get("Commander", ""))
    sp(panel(
        "Login Success",
        [
            f"✅ Welcome back, {Fore.LIGHTMAGENTA_EX}{name}{Fore.RESET}!",
            f"Commander: {c_color}{stat.get('Commander', '?')}{Fore.RESET}",
            "Loading your adventure...",
        ],
        color=Fore.LIGHTGREEN_EX,
    ))
    time.sleep(1)
    login_animation(name)

    return stat
