import os
import platform
import random
import select
import types
import sys
import subprocess
import json
import threading
import time
from colorama import Fore, Style
from typing import Any, Dict
from utils import (
    SKILL_TREE_BONUSES,
    COMMANDER_ELEMENTS,
    COMMANDER_NAMES,
    SKILL_TREE_BRANCHES,
    _BlankPalette,
)

def ensure_colorama():
    os.system("cls" if os.name == "nt" else "clear")
    try:
        from colorama import just_fix_windows_console

        just_fix_windows_console()
        return
    except ImportError:
        check = input(
            "This GAME requires additional components to function properly. "
            "Do you want to allow the installation of the necessary files(Colorama)?: (Y/N): "
        ).strip().lower()
        if check == "y":
            print("Installing necessary files...")
            time.sleep(1)
            subprocess.check_call([sys.executable, "-m", "pip", "install", "colorama"])
            from colorama import just_fix_windows_console

            just_fix_windows_console()
            print("Installation complete! Starting the game...")
            time.sleep(1)
            return

        print(
            "You have chosen not to install the necessary files. "
            "The game may not function properly without them. Starting the game anyway..."
        )
        time.sleep(1)
        blank = _BlankPalette()
        sys.modules["colorama"] = types.SimpleNamespace(
            Fore=blank,
            Style=blank,
            just_fix_windows_console=lambda: None,
        )

def clear_last_line():
    sys.stdout.write("\033[F")
    sys.stdout.write("\033[K")

progress = {
    "start_time": None,
    "duration": None,
    "done": False,
    "item": None,
}
def worker(item, duration, action_text):
    progress["start_time"] = time.time()
    progress["duration"] = duration
    progress["done"] = False
    progress["item"] = item
    while True:
        elapsed = time.time() - progress["start_time"]
        percent = min(100, int((elapsed / duration) * 100))
        remaining = max(0.0, duration - elapsed)

        clear()
        print(f"🛠️ {action_text} {item}...")
        print(f"Progress: {percent}% [{'=' * (percent // 5)}{' ' * (20 - percent // 5)}]  ⏳ {remaining:.1f}s left")

        if elapsed >= duration:
            break
        time.sleep(0.1)

    progress["done"] = True
    clear()
def start(item, action, lower, upper):
    worker(item, random.uniform(lower, upper), action)
def timer_loop(seconds):
    tournament_active = globals().get("tournament_active")
    started_at = time.time()
    while time.time() - started_at < seconds:
        time.sleep(1)
    if isinstance(tournament_active, list) and tournament_active:
        tournament_active[0] = False
    print("\n🏆 Tournament Over!")

def creating_account_animation(name):
    def clear_term():
        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")

    bar_length = 40
    clear_term()
    print(f"{Fore.LIGHTCYAN_EX}{Style.BRIGHT}Creating account for {Fore.MAGENTA}{name}{Fore.RESET}{Style.RESET_ALL}")
    for i in range(bar_length + 1):
        percent = int((i / bar_length) * 100)
        bar = "=" * i + " " * (bar_length - i)
        sys.stdout.write(f"\r{Fore.GREEN}[{bar}]{Fore.RESET} {percent}%")
        sys.stdout.flush()
        time.sleep(random.choice([0.075, 0.08, 0.09, 0.1, 0.065, 0.06, 1.01]))
    print(f"\n{Fore.LIGHTGREEN_EX}Account successfully created! Welcome, {name}!{Fore.RESET}")
    time.sleep(1)
    clear_term()
def login_animation(name):
    def clear_term():
        if platform.system() == "Windows":
            os.system("cls")
        else:
            os.system("clear")

    bar_length = 30
    clear_term()
    print(f"{Fore.CYAN}{Style.BRIGHT}Accessing Arcane Archives for {Fore.MAGENTA}{name}{Fore.CYAN}...{Style.RESET_ALL}")
    for i in range(bar_length + 1):
        percent = int((i / bar_length) * 100)
        bar = "■" * i + " " * (bar_length - i)
        sys.stdout.write(f"\r{Fore.GREEN}[{bar}]{Fore.RESET} {percent}%")
        sys.stdout.flush()
        time.sleep(random.choice([0.075, 0.08, 0.09, 0.1, 0.065, 0.06, 1.01]))
    print(f"\n{Fore.LIGHTGREEN_EX}🔓 Login successful! Welcome back, {name}!{Fore.RESET}")
    time.sleep(1)
    clear_term()

def clear():
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

def type(text, delay=0.01):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def fasttype(text, delay=0.005):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()


def build_default_skill_tree() -> Dict[str, int]:
    return {branch: 1 for branch in SKILL_TREE_BRANCHES}
def build_default_buffs(commander: str) -> Dict[str, int]:
    buffs = {branch: 0 for branch in SKILL_TREE_BRANCHES}
    elemental_branch = COMMANDER_ELEMENTS.get(commander)
    if elemental_branch:
        buffs[elemental_branch] = 20
    return buffs
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
        "Heroes": {},
        "Equipped Items": {},
        "Items": {},
        "Buffs": build_default_buffs(commander),
    }
def load_players(filename="players.json"):
    if os.path.exists(filename):
        if os.path.getsize(filename) == 0:
            with open(filename, "w") as file:
                json.dump({}, file)
        with open(filename, "r") as file:
            return json.load(file)
    return {}
def save_players(players, filename="players.json"):
    with open(filename, "w") as file:
        json.dump(players, file, indent=4)


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

    prompt_frames = [
        f"{Fore.MAGENTA}🌟 Welcome to Arcane Heroes! 🌟{Fore.RESET}",
        f"{Fore.CYAN}⚔️ Prepare your destiny! ⚔️{Fore.RESET}",
        f"{Fore.YELLOW}✨ Choose your path wisely... ✨{Fore.RESET}",
    ]
    for frame in prompt_frames:
        clear()
        print(frame)
        time.sleep(1)

    clear()
    print(f"{Fore.LIGHTGREEN_EX}{Style.BRIGHT}Choose your adventure:{Style.RESET_ALL}")
    print(f"  {Fore.LIGHTBLUE_EX}[1] {Fore.GREEN}Register a new hero 🆕")
    print(f"  {Fore.LIGHTRED_EX}[2] {Fore.YELLOW}Login as a returning champion 🛡️")
    print(f"{Fore.LIGHTMAGENTA_EX}Type 1 to start fresh or 2 to continue your quest!{Fore.RESET}")
    while True:
        try:
            response = int(input(f"{Fore.CYAN}Your choice, brave soul? 👉 {Fore.RESET}"))
            if response in (1, 2):
                break
            print(f"{Fore.RED}Please enter 1 or 2 only!{Fore.RESET}")
        except ValueError:
            print(f"{Fore.RED}Invalid input! Please enter a number (1 or 2).{Fore.RESET}")

    clear()
    if response == 1:
        print(f"{Fore.LIGHTGREEN_EX}{Style.BRIGHT}🆕 Registration Portal{Style.RESET_ALL}")
        name = input(f"{Fore.MAGENTA}{Style.BRIGHT}Enter your account name: {Style.RESET_ALL}").strip()
        clear()

        if name in players:
            print(f"{Fore.RED}Name already exists! Please choose a different name.{Fore.RESET}")
            time.sleep(2)
            return welcome()

        type(f"{Fore.LIGHTRED_EX}1. Pyronis - Fire {Fore.RESET}")
        type(f"{Fore.LIGHTBLUE_EX}2. Aquaryn - Water {Fore.RESET}")
        type(f"{Fore.LIGHTGREEN_EX}3. Terradon - Earth {Fore.RESET}")
        type(f"{Fore.CYAN}4. Zephyros - Air {Fore.RESET}")
        type(f"{Fore.YELLOW}5. Voltaris - Electric {Fore.RESET}")
        type(f"{Fore.MAGENTA}6. Noctyra - Shadow {Fore.RESET}\n")

        time.sleep(0.5)
        try:
            commander = int(input(f"{Fore.LIGHTMAGENTA_EX}⚔️ Choose your commander (1-6): {Fore.RESET}"))
        except ValueError:
            print(f"{Fore.RED}Invalid commander choice! Please try again.{Fore.RESET}")
            time.sleep(2)
            return welcome()

        if commander not in COMMANDER_NAMES:
            print(f"{Fore.RED}Invalid commander choice! Please try again.{Fore.RESET}")
            time.sleep(2)
            return welcome()

        stat = build_player_stats(name, COMMANDER_NAMES[commander])

        creating_account_animation(name)
        players[name] = stat
        save_players(players)
        return stat

    print(f"{Fore.LIGHTCYAN_EX}{Style.BRIGHT}🔐 Login Portal{Style.RESET_ALL}")
    name = input(f"{Fore.MAGENTA}{Style.BRIGHT}Enter your account name: {Style.RESET_ALL}").strip()

    if name not in players:
        print(f"{Fore.RED}❌ Account not found! Please register first.{Fore.RESET}")
        time.sleep(2)
        return welcome()

    stat = players[name]
    if sync_player_data(stat):
        players[name] = stat
        save_players(players)

    print(f"{Fore.LIGHTGREEN_EX}✅ Welcome back, {name}! Loading your adventure...{Fore.RESET}")
    time.sleep(1)
    login_animation(name)

    return stat
