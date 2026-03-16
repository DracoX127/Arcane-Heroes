from typing import Any, Dict
import subprocess
import threading
import platform
import select
import random
import time
import json
import sys
import os

# ==== Calarifications ====
os.system('clear')
check = input("This GAME requires additional components to function properly. Do you want to allow the installation of the necessary files(Colorama)?: (Y/N): ").strip().lower()
if check == "y":
    print("Installing necessary files...")
    time.sleep(1)
    subprocess.check_call([sys.executable, "-m", "pip", "install", "colorama"])
    from colorama import Fore, Style 
    print("Installation complete! Starting the game...")
    time.sleep(1)
else:
    print("You have chosen not to install the necessary files. The game may not function properly without them. Starting the game anyway...")
    from colorama import Fore, Style 
    time.sleep(1)

'''
1. Player Registeration and Login System
2. Shop System with Inventory Management
3. Skill Tree and Character Progression
4. List of Heroes with Unique Abilities and Stats
5. List of Monsters with Unique Abilities and Stats
6. Quest System with Multiple Objectives and Rewards
7. Battle System with Turn-Based Combat
'''

# ======Clear Player Save======
'''
with open("players.json", "w") as file:
    json.dump({}, file)
os.system('git add players.json')
os.system('git commit -m "player save"')
os.system('git push')
'''

# ========GAME FUNCTIONS=========
def clear_last_line():
    sys.stdout.write("\033[F")  # Move cursor up one line
    sys.stdout.write("\033[K")

progress = {
    "start_time": None,
    "duration": None,
    "done": False,
    "item": None
}
def worker(item, duration, string):
    progress["start_time"] = time.time()
    progress["duration"] = duration
    progress["done"] = False
    progress["item"] = item
    while True:
        elapsed = time.time() - progress["start_time"]
        percent = min(100, int((elapsed / duration) * 100))
        remaining = max(0.0, duration - elapsed)

        clear()
        print(f"🛠️ {string} {item}...")
        print(f"Progress: {percent}% [{'=' * (percent // 5)}{' ' * (20 - percent // 5)}]  ⏳ {remaining:.1f}s left")

        if elapsed >= duration:
            break
        time.sleep(0.1)

    progress["done"] = True
    clear()
def start(item, action, lower, upper):
    duration = random.uniform(lower, upper)
    worker(item, duration, action)
def timer_loop(seconds):
    global tournament_active
    start = time.time()
    while time.time() - start < seconds:
        time.sleep(1)
    tournament_active[0] = False
    print("\n🏆 Tournament Over!")

enchant_progress = {
    "start_time": None,
    "duration": None,
    "done": False
}
def enchantment_worker(duration):
    enchant_progress["start_time"] = time.time()
    enchant_progress["duration"] = duration
    enchant_progress["done"] = False
    while True:
        elapsed = time.time() - enchant_progress["start_time"]
        if elapsed >= duration:
            enchant_progress["done"] = True
            break
        time.sleep(0.2)
def start_enchant(duration):
    threading.Thread(target=enchantment_worker, args=(duration,), daemon=True).start()
    print("✨ Enchantment begun! Do your thing while the crystal does its magic... 🧙‍♀️💠")
def check_enchantment():
    if enchant_progress["start_time"] is None:
        print("🧐 Nothing is being enchanted right now!")
        return

    print("📡 Enchantment progress ... (press ENTER to return to town 🏙️)")

    while True:
        if enchant_progress["done"]:
            return 1
        else:
            elapsed = time.time() - enchant_progress["start_time"]
            remaining = enchant_progress["duration"] - elapsed
            percent = int((elapsed / enchant_progress["duration"]) * 100)
            print(f"\r🧪 Enchanting... {percent}% done | {remaining:.1f}s left", end="", flush=True)
            time.sleep(0.00001)
        if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
            input()  
            print("\n🚪 You leave the armory and head back to town.")
            break

def load_players(filename="players.json"):
    if os.path.exists(filename):
            if os.path.getsize(filename) == 0:
                with open(filename, "w") as file:
                    json.dump({}, file)
            with open(filename, "r") as file:
                return json.load(file)
    else:
        return {}
def save_players(players, filename="players.json"):
    with open(filename, "w") as file:
        json.dump(players, file, indent=4)


def creating_account_animation(name):
    from colorama import Fore, Style
    import sys, time, os

    def clear_term():
        if platform.system() == "Windows":
            os.system('cls')
        else:
            os.system('clear')

    bar_length = 40
    clear_term()
    print(f"{Fore.LIGHTCYAN_EX}{Style.BRIGHT}Creating account for {Fore.MAGENTA}{name}{Fore.RESET}{Style.RESET_ALL}")
    for i in range(bar_length + 1):
        percent = int((i / bar_length) * 100)
        bar = '=' * i + ' ' * (bar_length - i)
        sys.stdout.write(f"\r{Fore.GREEN}[{bar}]{Fore.RESET} {percent}%")
        sys.stdout.flush()
        time1 = random.choice([0.075, 0.08, 0.09, 0.1, 0.065, 0.06, 1.01])
        time.sleep(time1)
    print(f"\n{Fore.LIGHTGREEN_EX}Account successfully created! Welcome, {name}!{Fore.RESET}")
    time.sleep(1)
    clear_term()

def clear():
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')
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
def chat(text):
    print("    _______                    ___________      ________   ___________")
    print("   /       \\    |          |  |                /                |")
    print("  /         \\   |          |  |               /                 |")
    print(" |           |  |          |  |___________   /__________        |")
    print(" |           |  |          |  |                        /        |")
    print("  \\        \\\\   \\          /  |                       /         |")
    print("   \\_______ \\\\   \\________/   |___________   ________/          |")
    print("\n|----------|")
    time.sleep(random.uniform(0.5, 3))
    clear()
    print("    _______                    ___________      ________   ___________")
    print("   /       \\    |          |  |                /                |")
    print("  /         \\   |          |  |               /                 |")
    print(" |           |  |          |  |___________   /__________        |")
    print(" |           |  |          |  |                        /        |")
    print("  \\        \\\\   \\          /  |                       /         |")
    print("   \\_______ \\\\   \\________/   |___________   ________/          |")
    print("\n|===-------|")
    time.sleep(random.uniform(0.5, 3))
    clear()
    print("    _______                    ___________      ________   ___________")
    print("   /       \\    |          |  |                /                |")
    print("  /         \\   |          |  |               /                 |")
    print(" |           |  |          |  |___________   /__________        |")
    print(" |           |  |          |  |                        /        |")
    print("  \\        \\\\   \\          /  |                       /         |")
    print("   \\_______ \\\\   \\________/   |___________   ________/          |")
    print("\n|=====-----|")
    time.sleep(random.uniform(0.5, 3))
    clear()
    print("    _______                    ___________      ________   ___________")
    print("   /       \\    |          |  |                /                |")
    print("  /         \\   |          |  |               /                 |")
    print(" |           |  |          |  |___________   /__________        |")
    print(" |           |  |          |  |                        /        |")
    print("  \\        \\\\   \\          /  |                       /         |")
    print("   \\_______ \\\\   \\________/   |___________   ________/          |")
    print("\n|=======---|")
    time.sleep(random.uniform(0.5, 5))
    clear()
    print("    _______                    ___________      ________   ___________")
    print("   /       \\    |          |  |                /                |")
    print("  /         \\   |          |  |               /                 |")
    print(" |           |  |          |  |___________   /__________        |")
    print(" |           |  |          |  |                        /        |")
    print("  \\        \\\\   \\          /  |                       /         |")
    print("   \\_______ \\\\   \\________/   |___________   ________/          |")
    print("\n|==========|")
    time.sleep(random.uniform(0.5, 2))
    clear()
def welcome() -> Dict[str, Any]:
    os.system('git fetch')
    os.system('git checkout origin/main -- players.json')
    players = load_players()
    clear()
    name = " "
    clear()

    # Animated cool prompt effect
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
            else:
                print(f"{Fore.RED}Please enter 1 or 2 only!{Fore.RESET}")
        except ValueError:
            print(f"{Fore.RED}Invalid input! Please enter a number (1 or 2).{Fore.RESET}")

    clear()
    if response == 1:
        name = input("Enter your name: ")
        print(f"Name: {name}")
        clear()

        if name in players: # Check if the name already exists in the players dictionary
            print(f"{Fore.RED}Name already exists! Please choose a different name.{Fore.RESET}")
            time.sleep(2)
            return welcome()
        else: # If the name is unique, create a new player entry
            type(f"{Fore.LIGHTRED_EX}1. Pyronis - Fire {Fore.RESET}")
            type(f"{Fore.LIGHTBLUE_EX}2. Aquaryn - Water {Fore.RESET}")
            type(f"{Fore.LIGHTGREEN_EX}3. Terradon - Earth {Fore.RESET}")
            type(f"{Fore.CYAN}4. Zephyros - Air {Fore.RESET}")
            type(f"{Fore.YELLOW}5. Voltaris - Electric {Fore.RESET}")
            type(f"{Fore.MAGENTA}6. Noctyra - Shadow {Fore.RESET}\n")

            time.sleep(0.5)
            commander = int(input(f"{Fore.LIGHTMAGENTA_EX}⚔️ Choose your commander (1-6): {Fore.RESET}"))
            if commander == 1:
                stat = {
                    "Account Name": name,
                    "Commander": "Pyronis",
                    "Lvl": 1,
                    "Exp": 0,
                    "Gold": 1000,
                    "Heroes": {},
                    "Equipped Items": {},
                    "Items": {},
                    "Buffs": {
                        "ATK": 0,
                        "DEF": 0,
                        "HP": 0,
                        "SPD": 0,
                        "CRIT": 0,
                        "FIRE ATK": 20,
                        "WATER ATK": 0,
                        "EARTH ATK": 0,
                        "AIR ATK": 0,
                        "ELECTRIC ATK": 0,
                        "SHADOW ATK": 0,
                    }
                }
            elif commander == 2:
                stat = {
                    "Account Name": name,
                    "Commander": "Aquaryn",
                    "Lvl": 1,
                    "Exp": 0,
                    "Gold": 1000,
                    "Heroes": {},   
                    "Equipped Items": {},
                    "Items": {},
                    "Buffs": {
                        "ATK": 0,
                        "DEF": 0,
                        "HP": 0,
                        "SPD": 0,
                        "CRIT": 0,
                        "FIRE ATK": 0,
                        "WATER ATK": 20,
                        "EARTH ATK": 0,
                        "AIR ATK": 0,
                        "ELECTRIC ATK": 0,
                        "SHADOW ATK": 0,
                    }
                }
            elif commander == 3:
                stat = {
                    "Account Name": name,
                    "Commander": "Terradon",
                    "Lvl": 1,
                    "Exp": 0,
                    "Gold": 1000,
                    "Heroes": {},
                    "Equipped Items": {},
                    "Items": {},
                    "Buffs": {
                        "ATK": 0,
                        "DEF": 0,
                        "HP": 0,
                        "SPD": 0,
                        "CRIT": 0,
                        "FIRE ATK": 0,
                        "WATER ATK": 0,
                        "EARTH ATK": 20,
                        "AIR ATK": 0,
                        "ELECTRIC ATK": 0,
                        "SHADOW ATK": 0,
                    }
                }
            elif commander == 4:
                stat = {
                    "Account Name": name,
                    "Commander": "Zephyros",
                    "Lvl": 1,
                    "Exp": 0,
                    "Gold": 1000,
                    "Heroes": {},
                    "Equipped Items": {},
                    "Items": {},
                    "Buffs": {
                        "ATK": 0,
                        "DEF": 0,
                        "HP": 0,
                        "SPD": 0,
                        "CRIT": 0,
                        "FIRE ATK": 0,
                        "WATER ATK": 0,
                        "EARTH ATK": 0,
                        "AIR ATK": 20,
                        "ELECTRIC ATK": 0,
                        "SHADOW ATK": 0,
                    }
                }
            elif commander == 5:
                stat = {
                    "Account Name": name,
                    "Commander": "Voltaris",
                    "Lvl": 1,
                    "Exp": 0,
                    "Gold": 1000,
                    "Heroes": {},
                    "Equipped Items": {},
                    "Items": {},
                    "Buffs": {
                        "ATK": 0,
                        "DEF": 0,
                        "HP": 0,
                        "SPD": 0,
                        "CRIT": 0,
                        "FIRE ATK": 0,
                        "WATER ATK": 0,
                        "EARTH ATK": 0,
                        "AIR ATK": 0,
                        "ELECTRIC ATK": 20,
                        "SHADOW ATK": 0,
                    }
                }
            elif commander == 6:
                stat = {
                    "Account Name": name,
                    "Commander": "Noctyra",
                    "Lvl": 1,
                    "Exp": 0,
                    "Gold": 1000,
                    "Heroes": {},
                    "Equipped Items": {},
                    "Items": {},
                    "Buffs": {
                        "ATK": 0,
                        "DEF": 0,
                        "HP": 0,
                        "SPD": 0,
                        "CRIT": 0,
                        "FIRE ATK": 0,
                        "WATER ATK": 0,
                        "EARTH ATK": 0,
                        "AIR ATK": 0,
                        "ELECTRIC ATK": 0,
                        "SHADOW ATK": 20,
                    }
                }
            
            creating_account_animation(name)
            players[name] = stat
            with open("players.json", "w") as file:
                json.dump(players, file, indent=4)
            os.system('git add players.json')
            os.system('git commit -m "Player Save"')
            os.system('git push')
            return stat

stats = welcome()