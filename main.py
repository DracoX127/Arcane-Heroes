from typing import Any, Dict
from game_functions import (
    clear,
    clear_last_line,
    creating_account_animation,
    fasttype,
    login_animation,
    start,
    timer_loop,
    type,
    ensure_colorama,
    load_players,
    save_players,
    welcome,
    sync_player_data,
)
from utils import (
    SKILL_TREE_BONUSES,
    COMMANDER_ELEMENTS,
    COMMANDER_NAMES,
    SKILL_TREE_BRANCHES,
    SKILL_TREE_COLORS,
)
import random
import subprocess
import time
import json
import sys
import os
import types

ensure_colorama()
from colorama import Fore, Style


'''
- Shop System with Inventory Management ***PRIORITY***
- List of Heroes with Unique Abilities and Stats
- List of Monsters with Unique Abilities and Stats
- Quest System with Multiple Objectives and Rewards
- Skill Tree and Character Progression ***PRIORITY***
- Battle System with Turn-Based Combat
'''

# ======Clear Player Save======
'''
with open("players.json", "w") as file:
    json.dump({}, file)
os.system('git add players.json')
os.system('git commit -m "player save"')
os.system('git push')
'''
# ======END======

def skill_tree(stats: Dict[str, Any]) -> None:
    sync_player_data(stats)
    exit_option = len(SKILL_TREE_BRANCHES) + 1

    while True:
        clear()
        print(f"{Fore.LIGHTMAGENTA_EX}{Style.BRIGHT}🌌 Skill Tree{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Skill Points Available: {stats['Skill Points']}{Fore.RESET}")
        print(f"{Fore.YELLOW}Each branch only shows the current upgrade tier. Higher tiers cost more skill points.{Fore.RESET}\n")

        print(f"{Fore.LIGHTWHITE_EX}{Style.BRIGHT}Current Buff Totals{Style.RESET_ALL}")
        for branch in SKILL_TREE_BRANCHES:
            color = SKILL_TREE_COLORS.get(branch, Fore.WHITE)
            print(f"{color}{branch:<14}{Fore.RESET}: {stats['Buffs'][branch]}")

        print(f"\n{Fore.LIGHTWHITE_EX}{Style.BRIGHT}Upgrade Branches{Style.RESET_ALL}")
        for index, branch in enumerate(SKILL_TREE_BRANCHES, start=1):
            color = SKILL_TREE_COLORS.get(branch, Fore.WHITE)
            current_level = stats["Skill Tree"][branch]
            next_level = current_level + 1
            cost = current_level
            bonus = SKILL_TREE_BONUSES[branch]
            print(
                f"{color}[{index}] {branch}{Fore.RESET} | Current Lv {current_level} | "
                f"Next Lv {next_level} | Cost {cost} SP | Gain +{bonus} {branch}"
            )

        print(f"{Fore.LIGHTRED_EX}[{exit_option}] Exit Skill Tree{Fore.RESET}")
        choice = input(f"\n{Fore.CYAN}Choose a branch to upgrade: {Fore.RESET}").strip()

        if choice == str(exit_option):
            break

        if not choice.isdigit() or not 1 <= int(choice) <= len(SKILL_TREE_BRANCHES):
            print(f"{Fore.RED}Invalid choice! Pick one of the branch numbers.{Fore.RESET}")
            time.sleep(1.5)
            continue

        branch = SKILL_TREE_BRANCHES[int(choice) - 1]
        cost = stats["Skill Tree"][branch]
        if stats["Skill Points"] < cost:
            print(f"{Fore.RED}Not enough skill points for {branch}! You need {cost} SP.{Fore.RESET}")
            time.sleep(1.5)
            continue

        stats["Skill Points"] -= cost
        stats["Skill Tree"][branch] += 1
        stats["Buffs"][branch] += SKILL_TREE_BONUSES[branch]

        players = load_players()
        if isinstance(players, dict) and "Account Name" in players and "Commander" in players:
            players = {players["Account Name"]: players}
        players[stats["Account Name"]] = stats
        save_players(players)

        print(
            f"{Fore.LIGHTGREEN_EX}{branch} upgraded to Level {stats['Skill Tree'][branch]}! "
            f"+{SKILL_TREE_BONUSES[branch]} {branch} applied.{Fore.RESET}"
        )
        time.sleep(1.5)

def main():
    stats = welcome()
    option = ""

    while option != "10":
        clear()
        print("*************************")
        print("1. Skill Tree")
        print("10. Exit")
        print("*************************")
        option = input("Choose an option: ").strip()
        clear()
        if option == "1":
            skill_tree(stats)

if __name__ == "__main__":
    main()