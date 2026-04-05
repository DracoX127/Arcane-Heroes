import os
import sys
import subprocess
import time
import json
import types
from typing import Any, Dict

class _BlankPalette:
    def __getattr__(self, _name):
        return ""

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

from colorama import Fore

ensure_colorama()

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
