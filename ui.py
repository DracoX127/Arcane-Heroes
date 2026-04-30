"""
Arcane Heroes — Unified Visual Engine (CRAZY NEON OVERLOAD EDITION)
All UI rendering, color management, and terminal helpers live here.
NOW WITH MAXIMUM CHAOS.
"""

import math
import os
import platform
import random
import re
import subprocess
import sys
import time
import types
from typing import List

from colorama import Fore, Style


# Early print helper usable before full UI is initialized
def _early_print(text: str, color: str = Fore.MAGENTA) -> None:
    try:
        print(f"{color}{text}{Fore.RESET}")
    except Exception:
        print(text)

# ── Colorama Bootstrap ──

class _BlankPalette:
    def __getattr__(self, _name: str) -> str:
        return ""


def ensure_colorama() -> None:
    """Make sure colorama is available; offer to install if missing."""
    os.system("cls" if os.name == "nt" else "clear")
    try:
        from colorama import just_fix_windows_console
        just_fix_windows_console()
        return
    except ImportError:
        check = input(
            "This GAME requires additional components to function properly. "
            "Do you want to allow the installation of the necessary files (Colorama)?: (Y/N): "
        ).strip().lower()
        if check == "y":
            _early_print("Installing necessary files...", color=Fore.LIGHTYELLOW_EX)
            time.sleep(1)
            subprocess.check_call([sys.executable, "-m", "pip", "install", "colorama"])
            from colorama import just_fix_windows_console
            just_fix_windows_console()
            _early_print("Installation complete! Starting the game...", color=Fore.LIGHTGREEN_EX)
            time.sleep(1)
            return

        _early_print(
            "You have chosen not to install the necessary files. The game may not function properly without them. Starting the game anyway...",
            color=Fore.LIGHTRED_EX,
        )
        time.sleep(1)
        blank = _BlankPalette()
        sys.modules["colorama"] = types.SimpleNamespace(
            Fore=blank,
            Style=blank,
            just_fix_windows_console=lambda: None,
        )


# ── Terminal Helpers ──

def clear() -> None:
    """Clear the terminal screen."""
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")


def clear_last_line() -> None:
    """Erase the previous terminal line."""
    sys.stdout.write("\033[F")
    sys.stdout.write("\033[K")


def typed_print(text: str, delay: float = 0.01) -> None:
    """Type out text character by character."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()


def fast_typed_print(text: str, delay: float = 0.005) -> None:
    """Fast variant of typed_print."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()


# ── Convenience Styled Print/Input ──


def styled_print(text: str, color: str = Fore.LIGHTWHITE_EX, delay: float | None = None) -> None:
    """Print text ensuring it's styled. If `text` already contains ANSI, leave as-is.

    - If `delay` is provided, use `typed_print` to animate.
    - Otherwise use a normal `print`.
    """
    # Preserve blank lines
    if text.strip() == "":
        print()
        return

    # Detect existing ANSI sequences
    if ANSI_PATTERN.search(text) is None:
        text = f"{color}{text}{Fore.RESET}"
    if delay is None:
        print(text)
    else:
        typed_print(text, delay=delay)


def styled_input(prompt_text: str, color: str = Fore.LIGHTCYAN_EX) -> str:
    """Input wrapper that styles the prompt text consistently."""
    if ANSI_PATTERN.search(prompt_text) is None:
        prompt_text = f"{color}{prompt_text}{Fore.RESET}"
    return input(prompt_text).strip()


# Short aliases for convenience elsewhere in the codebase
sp = styled_print
sin = styled_input


# ── Layout Constants ──
PANEL_WIDTH = 118
ANSI_PATTERN = re.compile(r"\033\[[0-9;]*m")

# ── Theme Palette (fantasy / dark neon) ──
THEME = {
    "primary": Fore.MAGENTA,
    "accent": Fore.LIGHTCYAN_EX,
    "muted": Fore.LIGHTBLACK_EX,
    "highlight": Fore.LIGHTYELLOW_EX,
    "title": Fore.LIGHTMAGENTA_EX,
    "panel_border": Fore.MAGENTA,
    "option": Fore.LIGHTWHITE_EX,
}

# Global toggle to force the "insane" UI everywhere
INSANE_UI = True

# ── CRAZY ANIMATION ARSENAL ──

# Neon color cycle for maximum chaos
NEON_CYCLE = [
    Fore.MAGENTA, Fore.LIGHTMAGENTA_EX, Fore.LIGHTCYAN_EX, Fore.CYAN,
    Fore.LIGHTYELLOW_EX, Fore.YELLOW, Fore.LIGHTRED_EX, Fore.RED,
    Fore.LIGHTGREEN_EX, Fore.GREEN, Fore.LIGHTBLUE_EX, Fore.BLUE,
]

RAINBOW_CYCLE = [
    Fore.RED, Fore.LIGHTRED_EX, Fore.YELLOW, Fore.LIGHTYELLOW_EX,
    Fore.GREEN, Fore.LIGHTGREEN_EX, Fore.CYAN, Fore.LIGHTCYAN_EX,
    Fore.BLUE, Fore.LIGHTBLUE_EX, Fore.MAGENTA, Fore.LIGHTMAGENTA_EX,
]

GLITCH_CHARS = "!@#$%^&*()_+-=[]{}|;:,.<>?/~`"


def _strip_ansi(text: str) -> str:
    """Remove all ANSI escape codes from text."""
    return ANSI_PATTERN.sub("", text)


def rainbow_text(text: str, offset: int = 0) -> str:
    """Paint text with a rainbow color cycle."""
    out = []
    for i, ch in enumerate(text):
        color = RAINBOW_CYCLE[(i + offset) % len(RAINBOW_CYCLE)]
        out.append(f"{color}{ch}")
    out.append(Fore.RESET)
    return "".join(out)


def glitch_text(text: str, intensity: float = 0.3) -> str:
    """Return text with random characters glitched."""
    out = []
    for ch in text:
        if random.random() < intensity and ch.isalnum():
            out.append(f"{Fore.LIGHTRED_EX}{random.choice(GLITCH_CHARS)}{Fore.RESET}")
        else:
            out.append(ch)
    return "".join(out)


def wave_text(text: str) -> str:
    """Return text with wave-like color cycling."""
    out = []
    for i, ch in enumerate(text):
        color = NEON_CYCLE[i % len(NEON_CYCLE)]
        out.append(f"{color}{ch}{Fore.RESET}")
    return "".join(out)


def neon_flicker(text: str, cycles: int = 3) -> None:
    """Print text with a flickering neon sign effect."""
    for _ in range(cycles):
        for bright in (True, False, True, False, True):
            clear()
            if bright:
                print(f"{Fore.LIGHTMAGENTA_EX}{Style.BRIGHT}{text}{Style.RESET_ALL}{Fore.RESET}")
            else:
                print(f"{Fore.MAGENTA}{Style.DIM}{text}{Style.RESET_ALL}{Fore.RESET}")
            time.sleep(0.04)
    clear()
    print(f"{Fore.LIGHTMAGENTA_EX}{Style.BRIGHT}{text}{Style.RESET_ALL}{Fore.RESET}")


def typewriter_crazy(text: str, delay: float = 0.015) -> None:
    """Typewriter effect with random color changes per character."""
    for char in text:
        color = random.choice(NEON_CYCLE)
        sys.stdout.write(f"{color}{char}{Fore.RESET}")
        sys.stdout.flush()
        time.sleep(delay + random.uniform(-0.005, 0.005))
    print()


def explosion_print(text: str, color: str = Fore.LIGHTYELLOW_EX, delay: float = 0.02) -> None:
    """Print text that 'explodes' outward from center."""
    stripped = _strip_ansi(text)
    length = len(stripped)
    mid = length // 2
    for i in range(mid + 1):
        left = max(0, mid - i)
        right = min(length, mid + i + (length % 2))
        display = " " * left + stripped[left:right] + " " * (length - right)
        sys.stdout.write(f"\r{color}{Style.BRIGHT}{display}{Style.RESET_ALL}{Fore.RESET}")
        sys.stdout.flush()
        time.sleep(delay)
    print()


def particle_burst(x: int = 59, y: int = 10, count: int = 30) -> None:
    """Simulate an ASCII particle burst at position."""
    particles = []
    for _ in range(count):
        px = x + random.randint(-20, 20)
        py = y + random.randint(-5, 5)
        char = random.choice(["*", "✦", "✧", "·", "•", "+", "×"])
        color = random.choice(NEON_CYCLE)
        particles.append((px, py, char, color))

    # Print particles
    for _ in range(3):
        clear()
        for px, py, char, color in particles:
            # Simple terminal positioning attempt
            print(f"\033[{py};{px}H{color}{char}{Fore.RESET}", end="")
        sys.stdout.flush()
        time.sleep(0.08)
    clear()


def shimmer_line(char: str = "═", width: int = PANEL_WIDTH, cycles: int = 2) -> None:
    """Print a line with a shimmering light effect moving across it."""
    for _ in range(cycles):
        for pos in range(width):
            line_chars = []
            for i in range(width):
                if i == pos:
                    line_chars.append(f"{Fore.LIGHTWHITE_EX}{Style.BRIGHT}{char}{Style.RESET_ALL}")
                elif abs(i - pos) <= 2:
                    line_chars.append(f"{Fore.LIGHTCYAN_EX}{char}{Fore.RESET}")
                elif abs(i - pos) <= 5:
                    line_chars.append(f"{Fore.CYAN}{char}{Fore.RESET}")
                else:
                    line_chars.append(f"{Fore.MAGENTA}{Style.DIM}{char}{Style.RESET_ALL}")
            sys.stdout.write("\r" + "".join(line_chars))
            sys.stdout.flush()
            time.sleep(0.01)
    print()


def jitter_text(text: str, jitter_count: int = 5) -> None:
    """Print text that jitters/vibrates slightly."""
    for _ in range(jitter_count):
        offset = random.choice(["", " ", "  "])
        sys.stdout.write(f"\r{offset}{text}{Fore.RESET}")
        sys.stdout.flush()
        time.sleep(0.05)
    print()


def matrix_rain(duration: float = 1.0, width: int = 80) -> None:
    """Brief matrix-style falling characters effect."""
    chars = "0123456789ABCDEF"
    end_time = time.time() + duration
    while time.time() < end_time:
        clear()
        # Generate random falling characters
        for row in range(15):
            line = ""
            for col in range(width // 2):
                if random.random() < 0.3:
                    ch = random.choice(chars)
                    color = random.choice([Fore.GREEN, Fore.LIGHTGREEN_EX, Fore.LIGHTBLACK_EX])
                    line += f"{color}{ch}{Fore.RESET} "
                else:
                    line += "  "
            print(line)
        time.sleep(0.08)
    clear()


def flash_screen(color: str = Fore.LIGHTMAGENTA_EX, times: int = 3) -> None:
    """Flash the entire screen with a color."""
    for _ in range(times):
        clear()
        print(f"{color}{Style.BRIGHT}{' ' * 2000}{Style.RESET_ALL}")
        sys.stdout.flush()
        time.sleep(0.04)
        clear()
        time.sleep(0.04)


def spiral_text(text: str, center_x: int = 59, center_y: int = 10) -> None:
    """Display text in a rough spiral pattern."""
    clear()
    for i, ch in enumerate(text[:40]):  # Limit to avoid overflow
        x = int(center_x + (i * 0.4) * (i % 3 - 1))
        y = int(center_y + (i * 0.4) * 0.3)
        color = NEON_CYCLE[i % len(NEON_CYCLE)]
        print(f"\033[{y};{x}H{color}{ch}{Fore.RESET}", end="")
        sys.stdout.flush()
        time.sleep(0.04)
    print()
    time.sleep(0.3)
    clear()


def bounce_text(text: str, bounces: int = 3) -> None:
    """Print text with a bouncing effect."""
    for _ in range(bounces):
        for offset in range(5):
            clear()
            print("\n" * offset + f"{Fore.LIGHTCYAN_EX}{Style.BRIGHT}{text}{Style.RESET_ALL}{Fore.RESET}")
            sys.stdout.flush()
            time.sleep(0.06)
        for offset in range(5, 0, -1):
            clear()
            print("\n" * offset + f"{Fore.LIGHTCYAN_EX}{Style.BRIGHT}{text}{Style.RESET_ALL}{Fore.RESET}")
            sys.stdout.flush()
            time.sleep(0.06)
    clear()
    print(f"{Fore.LIGHTCYAN_EX}{Style.BRIGHT}{text}{Style.RESET_ALL}{Fore.RESET}")


def color_cycle_print(text: str, duration: float = 1.0) -> None:
    """Print text that rapidly cycles through colors."""
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        color = NEON_CYCLE[i % len(NEON_CYCLE)]
        sys.stdout.write(f"\r{color}{Style.BRIGHT}{text}{Style.RESET_ALL}{Fore.RESET}")
        sys.stdout.flush()
        time.sleep(0.06)
        i += 1
    print()


def starfield_background(duration: float = 0.8, star_count: int = 50) -> None:
    """Display a brief animated starfield."""
    end_time = time.time() + duration
    while time.time() < end_time:
        clear()
        stars = []
        for _ in range(star_count):
            x = random.randint(1, PANEL_WIDTH)
            y = random.randint(1, 20)
            brightness = random.choice(["·", "•", "*", "✦"])
            color = random.choice([Fore.WHITE, Fore.LIGHTBLACK_EX, Fore.LIGHTCYAN_EX, Fore.LIGHTMAGENTA_EX])
            stars.append((x, y, brightness, color))
        for x, y, brightness, color in stars:
            print(f"\033[{y};{x}H{color}{brightness}{Fore.RESET}", end="")
        sys.stdout.flush()
        time.sleep(0.1)
    clear()


def thunder_effect(text: str) -> None:
    """Print text with thunder/lightning flash effects."""
    for _ in range(2):
        clear()
        print(f"{Fore.WHITE}{Style.BRIGHT}{' ' * 2000}{Style.RESET_ALL}")
        sys.stdout.flush()
        time.sleep(0.03)
        clear()
        print(f"{Fore.LIGHTYELLOW_EX}{Style.BRIGHT}{text}{Style.RESET_ALL}{Fore.RESET}")
        sys.stdout.flush()
        time.sleep(0.1)
        clear()
        time.sleep(0.05)
    print(f"{Fore.LIGHTYELLOW_EX}{Style.BRIGHT}{text}{Style.RESET_ALL}{Fore.RESET}")


def emoji_explosion(emoji: str = "✨", count: int = 20) -> None:
    """Print a burst of emojis scattered across the screen."""
    clear()
    for _ in range(count):
        x = random.randint(1, PANEL_WIDTH)
        y = random.randint(1, 15)
        print(f"\033[{y};{x}H{emoji}", end="")
    sys.stdout.flush()
    time.sleep(0.3)
    clear()


def crazy_transition(effect: str = "random", duration: float = 0.5) -> None:
    """Play a crazy transition effect."""
    if effect == "random":
        effect = random.choice(["flash", "matrix", "starfield", "shimmer", "explosion"])
    if effect == "flash":
        flash_screen(random.choice(NEON_CYCLE), times=2)
    elif effect == "matrix":
        matrix_rain(duration=duration)
    elif effect == "starfield":
        starfield_background(duration=duration)
    elif effect == "shimmer":
        shimmer_line(cycles=1)
    elif effect == "explosion":
        emoji_explosion(random.choice(["✨", "💥", "🔥", "⚡"]), count=15)


# ── New Animation Helpers ──

def scroll_text(text: str, direction: str = "left", delay: float = 0.03) -> None:
    """Scroll text across the terminal width like a marquee."""
    stripped = _strip_ansi(text)
    width = PANEL_WIDTH
    padded = " " * width + stripped + " " * width
    for i in range(len(padded) - width + 1):
        window = padded[i:i + width]
        color = NEON_CYCLE[i % len(NEON_CYCLE)]
        sys.stdout.write(f"\r{color}{Style.BRIGHT}{window}{Style.RESET_ALL}{Fore.RESET}")
        sys.stdout.flush()
        time.sleep(delay)
    print()


def scanline_reveal(text: str, delay: float = 0.02) -> None:
    """Reveal text with a horizontal scanline effect."""
    stripped = _strip_ansi(text)
    length = len(stripped)
    for pos in range(length + 1):
        display = ""
        for i, ch in enumerate(stripped):
            if i < pos:
                color = Fore.LIGHTWHITE_EX if i == pos - 1 else Fore.WHITE
                display += f"{color}{ch}{Fore.RESET}"
            else:
                display += f"{Fore.LIGHTBLACK_EX}·{Fore.RESET}"
        sys.stdout.write(f"\r{display}")
        sys.stdout.flush()
        time.sleep(delay)
    print()


def pulsing_border(text: str, cycles: int = 3, delay: float = 0.12) -> None:
    """Print text surrounded by a pulsing border."""
    stripped = _strip_ansi(text)
    width = min(PANEL_WIDTH, len(stripped) + 8)
    for cycle in range(cycles):
        for bright in (True, False):
            clear()
            border_char = "█" if bright else "░"
            border_color = Fore.LIGHTMAGENTA_EX if bright else Fore.MAGENTA
            horizontal = border_color + border_char * width + Fore.RESET
            padding = " " * ((width - len(stripped) - 2) // 2)
            print(horizontal)
            print(f"{border_color}{border_char}{Fore.RESET}{padding}{stripped}{padding}{border_color}{border_char}{Fore.RESET}")
            print(horizontal)
            sys.stdout.flush()
            time.sleep(delay)
    clear()


def fireworks(count: int = 8, duration: float = 1.2) -> None:
    """Display a brief ASCII fireworks effect."""
    chars = ["*", "✦", "✧", "·", "•", "+", "×", "◆", "◇"]
    end_time = time.time() + duration
    burst_count = 0
    while time.time() < end_time and burst_count < count:
        clear()
        cx = random.randint(20, PANEL_WIDTH - 20)
        cy = random.randint(3, 12)
        color = random.choice(NEON_CYCLE)
        # Draw burst center
        print(f"\033[{cy};{cx}H{color}{random.choice(chars)}{Fore.RESET}", end="")
        # Draw burst rays
        for _ in range(6):
            rx = cx + random.randint(-8, 8)
            ry = cy + random.randint(-3, 3)
            if rx != cx or ry != cy:
                print(f"\033[{ry};{rx}H{color}{random.choice(chars)}{Fore.RESET}", end="")
        sys.stdout.flush()
        time.sleep(duration / count)
        burst_count += 1
    clear()


def typing_burst(lines: List[str], delay: float = 0.008) -> None:
    """Type multiple lines with a burst effect, each line getting a random color."""
    for line in lines:
        color = random.choice(NEON_CYCLE)
        for char in line:
            sys.stdout.write(f"{color}{char}{Fore.RESET}")
            sys.stdout.flush()
            time.sleep(delay + random.uniform(-0.002, 0.002))
        print()
        time.sleep(0.03)


def orbiting_dots(text: str, cycles: int = 3, delay: float = 0.1) -> None:
    """Show text with orbiting dots around it."""
    dots = ["◐", "◓", "◑", "◒"]
    for _ in range(cycles):
        for dot in dots:
            clear()
            prefix = f"{Fore.LIGHTCYAN_EX}{dot}{Fore.RESET}"
            suffix = f"{Fore.LIGHTCYAN_EX}{dot}{Fore.RESET}"
            print(f"\n\n{prefix}  {Fore.LIGHTMAGENTA_EX}{Style.BRIGHT}{text}{Style.RESET_ALL}{Fore.RESET}  {suffix}")
            sys.stdout.flush()
            time.sleep(delay)
    clear()


# ═══════════════════════════════════════════════════════════════════════════════
#  PHASE 0: THE BIG ONE — ARCANE CATACLYSM
# ═══════════════════════════════════════════════════════════════════════════════


def arcane_cataclysm(title_text: str = "CATACLYSM") -> None:
    """Multi-phase world-ending ritual animation. hijacks the entire terminal."""
    import math
    from config import RUNE_CHARS, VOID_CHARS, LIGHTNING_CHARS
    center_x, center_y = PANEL_WIDTH // 2, 10

    # ── Phase 1: Ominous Pulse ──
    for _ in range(6):
        clear()
        dim = f"{Fore.MAGENTA}{Style.DIM}{' ' * 2000}{Style.RESET_ALL}"
        bright = f"{Fore.LIGHTMAGENTA_EX}{Style.BRIGHT}{' ' * 2000}{Style.RESET_ALL}"
        print(bright if _ % 2 == 0 else dim)
        sys.stdout.flush()
        time.sleep(0.08)

    # ── Phase 2: Rune Circle ──
    runes = RUNE_CHARS[:12]
    for frame in range(18):
        clear()
        radius = 14 - frame * 0.3
        for i, rune in enumerate(runes):
            angle = (frame * 0.35) + (i * (6.283 / len(runes)))
            px = int(center_x + math.cos(angle) * radius)
            py = int(center_y + math.sin(angle) * radius * 0.45)
            color = NEON_CYCLE[i % len(NEON_CYCLE)]
            print(f"\033[{py};{px}H{color}{rune}{Fore.RESET}", end="")
        sys.stdout.flush()
        time.sleep(0.035)

    # ── Phase 3: Void Vortex ──
    angle = 0
    for _ in range(14):
        clear()
        for i in range(24):
            radius = 2 + (i * 1.1)
            a = angle + (i * 0.45)
            px = int(center_x + math.cos(a) * radius)
            py = int(center_y + math.sin(a) * radius * 0.4)
            char = VOID_CHARS[i % len(VOID_CHARS)]
            color = random.choice([Fore.MAGENTA, Fore.LIGHTMAGENTA_EX, Fore.LIGHTBLACK_EX])
            print(f"\033[{py};{px}H{color}{char}{Fore.RESET}", end="")
        sys.stdout.flush()
        time.sleep(0.045)
        angle += 0.5

    # ── Phase 4: Lightning Storm ──
    for _ in range(10):
        clear()
        if random.random() < 0.5:
            print(f"{Fore.WHITE}{Style.BRIGHT}{' ' * 2000}{Style.RESET_ALL}")
            sys.stdout.flush()
            time.sleep(0.03)
            clear()
        for _bolt in range(random.randint(2, 4)):
            x = random.randint(10, PANEL_WIDTH - 10)
            y = random.randint(2, 16)
            char = random.choice(LIGHTNING_CHARS)
            color = random.choice([Fore.LIGHTYELLOW_EX, Fore.YELLOW, Fore.WHITE])
            print(f"\033[{y};{x}H{color}{Style.BRIGHT}{char}{Style.RESET_ALL}{Fore.RESET}", end="")
        sys.stdout.flush()
        time.sleep(0.07)

    # ── Phase 5: Energy Convergence ──
    for frame in range(12):
        clear()
        for _p in range(18):
            angle = random.uniform(0, 6.283)
            dist = 22 - frame * 1.8
            px = int(center_x + math.cos(angle) * max(1, dist))
            py = int(center_y + math.sin(angle) * max(1, dist) * 0.4)
            color = random.choice([Fore.LIGHTCYAN_EX, Fore.CYAN, Fore.LIGHTYELLOW_EX])
            print(f"\033[{py};{px}H{color}•{Fore.RESET}", end="")
        sys.stdout.flush()
        time.sleep(0.05)

    # ── Phase 6: Whiteout Flash ──
    for _ in range(4):
        clear()
        print(f"{Fore.WHITE}{Style.BRIGHT}{' ' * 2000}{Style.RESET_ALL}")
        sys.stdout.flush()
        time.sleep(0.04)
        clear()
        time.sleep(0.03)

    # ── Phase 7: Shockwave Ring ──
    for ring in range(3, 30, 3):
        clear()
        for angle_deg in range(0, 360, 10):
            a = math.radians(angle_deg)
            px = int(center_x + math.cos(a) * ring)
            py = int(center_y + math.sin(a) * ring * 0.4)
            color = NEON_CYCLE[(angle_deg // 10) % len(NEON_CYCLE)]
            print(f"\033[{py};{px}H{color}✦{Fore.RESET}", end="")
        sys.stdout.flush()
        time.sleep(0.04)

    # ── Phase 8: Title Reveal ──
    for cycle in range(3):
        clear()
        color = RAINBOW_CYCLE[cycle % len(RAINBOW_CYCLE)]
        padding = " " * max(0, (PANEL_WIDTH - len(title_text)) // 2)
        print(f"\n\n{padding}{color}{Style.BRIGHT}{title_text}{Style.RESET_ALL}{Fore.RESET}")
        # floating embers
        for _e in range(12):
            ex = random.randint(1, PANEL_WIDTH)
            ey = random.randint(1, 18)
            ec = random.choice([Fore.LIGHTRED_EX, Fore.YELLOW, Fore.LIGHTYELLOW_EX])
            print(f"\033[{ey};{ex}H{ec}•{Fore.RESET}", end="")
        sys.stdout.flush()
        time.sleep(0.2)
    clear()


# ═══════════════════════════════════════════════════════════════════════════════
#  PHASE 1: NEW ANIMATION ARSENAL
# ═══════════════════════════════════════════════════════════════════════════════

# ── Progression & Reward Animations ──

def xp_gain_bar(current_xp: int, max_xp: int, width: int = 40) -> None:
    """Animated XP bar fill with trailing particle effect."""
    if max_xp <= 0:
        return
    percent = min(100, max(0, int((current_xp / max_xp) * 100)))
    filled = int(width * percent / 100)
    for i in range(filled + 1):
        current_filled = i
        bar_chars = []
        for j in range(width):
            if j < current_filled:
                # trailing particles near the edge
                if j == current_filled - 1:
                    bar_chars.append(f"{Fore.LIGHTYELLOW_EX}▓{Fore.RESET}")
                elif j >= current_filled - 3:
                    bar_chars.append(f"{Fore.YELLOW}▒{Fore.RESET}")
                else:
                    bar_chars.append(f"{Fore.LIGHTGREEN_EX}█{Fore.RESET}")
            else:
                bar_chars.append(f"{Fore.LIGHTBLACK_EX}░{Fore.RESET}")
        bar = "".join(bar_chars)
        sys.stdout.write(f"\r{Fore.CYAN}XP [{bar}]{Fore.RESET} {int((i / width) * 100)}%")
        sys.stdout.flush()
        time.sleep(0.02)
    print()


def level_up_celebration(level: int) -> None:
    """Rainbow spiral + stat burst for level-up events."""
    clear()
    # Rainbow spiral
    spiral_chars = "LEVEL UP!"
    center_x, center_y = PANEL_WIDTH // 2, 10
    for i, ch in enumerate(spiral_chars):
        x = int(center_x + (i * 1.2) * (i % 3 - 1))
        y = int(center_y + (i * 0.5) * 0.3)
        color = RAINBOW_CYCLE[i % len(RAINBOW_CYCLE)]
        print(f"\033[{y};{x}H{color}{Style.BRIGHT}{ch}{Style.RESET_ALL}{Fore.RESET}", end="")
        sys.stdout.flush()
        time.sleep(0.06)
    print()
    time.sleep(0.2)
    # Stat burst
    for _ in range(12):
        clear()
        px = center_x + random.randint(-25, 25)
        py = center_y + random.randint(-6, 6)
        char = random.choice(["+", "✦", "✧", "◆", "◇", "★"])
        color = random.choice(RAINBOW_CYCLE)
        print(f"\033[{py};{px}H{color}{char}{Fore.RESET}", end="")
        sys.stdout.flush()
        time.sleep(0.05)
    clear()
    sp(f"{Fore.LIGHTYELLOW_EX}{Style.BRIGHT}🎉 LEVEL {level} REACHED! {Style.RESET_ALL}{Fore.RESET}")
    fireworks(count=6, duration=0.8)


def loot_reveal(item_name: str, rarity: str = "Common") -> None:
    """Card-flip rarity reveal animation."""
    from config import RARITY_COLORS, ASCII_CINEMA_FRAMES
    color = RARITY_COLORS.get(rarity, Fore.WHITE)
    frames = ASCII_CINEMA_FRAMES.get("card_flip", [])
    clear()
    # Flip animation
    for frame in frames:
        clear()
        print(f"\n\n{color}{Style.BRIGHT}{frame}{Style.RESET_ALL}{Fore.RESET}")
        sys.stdout.flush()
        time.sleep(0.04)
    # Reveal
    clear()
    border = f"{color}╔{'═' * (len(item_name) + 8)}╗{Fore.RESET}"
    middle = f"{color}║{Fore.RESET}  {Style.BRIGHT}{item_name}{Style.RESET_ALL}  {color}║{Fore.RESET}"
    footer = f"{color}╚{'═' * (len(item_name) + 8)}╝{Fore.RESET}"
    print(f"\n\n{border}\n{middle}\n{footer}")
    sp(f"{color}{Style.BRIGHT}✨ {rarity} Item Revealed: {item_name}! ✨{Style.RESET_ALL}{Fore.RESET}")
    time.sleep(0.3)


def milestone_unlock(title: str) -> None:
    """Golden lock shatter animation for milestone unlocks."""
    from config import ASCII_CINEMA_FRAMES
    frames = ASCII_CINEMA_FRAMES.get("lock", [])
    clear()
    for frame in frames:
        clear()
        print(f"\n\n{Fore.LIGHTYELLOW_EX}{Style.BRIGHT}{frame}{Style.RESET_ALL}{Fore.RESET}")
        sys.stdout.flush()
        time.sleep(0.08)
    clear()
    sp(f"{Fore.LIGHTYELLOW_EX}{Style.BRIGHT}🔓 MILESTONE UNLOCKED: {title}{Style.RESET_ALL}{Fore.RESET}")
    emoji_explosion("✨", count=15)
    time.sleep(0.3)


def skill_unlock_burst(branch: str) -> None:
    """Elemental burst animation per skill branch."""
    from config import ELEMENT_BURST_COLORS
    colors = ELEMENT_BURST_COLORS.get(branch, (Fore.LIGHTCYAN_EX, Fore.CYAN, Fore.WHITE))
    clear()
    center_x, center_y = PANEL_WIDTH // 2, 10
    # Burst rays
    for _ in range(8):
        clear()
        for _ in range(10):
            angle = random.uniform(0, 6.28)
            dist = random.randint(3, 20)
            px = int(center_x + math.cos(angle) * dist)
            py = int(center_y + math.sin(angle) * dist * 0.4)
            color = random.choice(colors)
            char = random.choice(["✦", "✧", "◆", "◇", "•", "+"])
            print(f"\033[{py};{px}H{color}{char}{Fore.RESET}", end="")
        sys.stdout.flush()
        time.sleep(0.06)
    clear()
    sp(f"{colors[0]}{Style.BRIGHT}🔥 {branch} SKILL UNLOCKED! {Style.RESET_ALL}{Fore.RESET}")
    time.sleep(0.3)


# ── Environmental & Ambient Effects ──

def rain_effect(duration: float = 1.0, width: int = 118) -> None:
    """ASCII rain overlay effect."""
    from config import RAIN_CHARS
    end_time = time.time() + duration
    while time.time() < end_time:
        clear()
        lines = []
        for _ in range(20):
            line = ""
            for _ in range(width // 2):
                if random.random() < 0.15:
                    ch = random.choice(RAIN_CHARS)
                    color = random.choice([Fore.BLUE, Fore.LIGHTBLUE_EX, Fore.CYAN])
                    line += f"{color}{ch}{Fore.RESET}"
                else:
                    line += " "
            lines.append(line)
        print("\n".join(lines))
        sys.stdout.flush()
        time.sleep(0.08)
    clear()


def snow_effect(duration: float = 1.0, width: int = 118) -> None:
    """Falling snowflakes effect."""
    from config import SNOW_CHARS
    end_time = time.time() + duration
    while time.time() < end_time:
        clear()
        lines = []
        for _ in range(18):
            line = ""
            for _ in range(width // 2):
                if random.random() < 0.12:
                    ch = random.choice(SNOW_CHARS)
                    color = random.choice([Fore.WHITE, Fore.LIGHTWHITE_EX, Fore.LIGHTCYAN_EX])
                    line += f"{color}{ch}{Fore.RESET} "
                else:
                    line += "  "
            lines.append(line)
        print("\n".join(lines))
        sys.stdout.flush()
        time.sleep(0.12)
    clear()


def fog_scroll(duration: float = 1.0, width: int = 118) -> None:
    """Horizontal mist scrolling effect."""
    from config import FOG_CHARS
    end_time = time.time() + duration
    offset = 0
    while time.time() < end_time:
        clear()
        for row in range(8):
            line = ""
            for col in range(width):
                pos = (col + offset + row * 7) % width
                if random.random() < 0.25:
                    ch = random.choice(FOG_CHARS)
                    color = random.choice([Fore.LIGHTBLACK_EX, Fore.WHITE, Fore.LIGHTCYAN_EX])
                    line += f"{color}{ch}{Fore.RESET}"
                else:
                    line += " "
            print(line)
        sys.stdout.flush()
        time.sleep(0.06)
        offset += 2
    clear()


def lightning_storm(duration: float = 1.0) -> None:
    """Lightning + thunder combo effect."""
    from config import LIGHTNING_CHARS
    end_time = time.time() + duration
    while time.time() < end_time:
        clear()
        # Flash
        if random.random() < 0.3:
            print(f"{Fore.WHITE}{Style.BRIGHT}{' ' * 2000}{Style.RESET_ALL}")
            sys.stdout.flush()
            time.sleep(0.03)
            clear()
        # Lightning bolts
        for _ in range(random.randint(1, 3)):
            x = random.randint(10, PANEL_WIDTH - 10)
            y = random.randint(2, 15)
            char = random.choice(LIGHTNING_CHARS)
            color = random.choice([Fore.LIGHTYELLOW_EX, Fore.YELLOW, Fore.WHITE])
            print(f"\033[{y};{x}H{color}{Style.BRIGHT}{char}{Style.RESET_ALL}{Fore.RESET}", end="")
        sys.stdout.flush()
        time.sleep(0.1)
    clear()


def void_vortex(duration: float = 1.0) -> None:
    """Dark spiral vortex effect."""
    from config import VOID_CHARS
    center_x, center_y = PANEL_WIDTH // 2, 10
    end_time = time.time() + duration
    angle = 0
    while time.time() < end_time:
        clear()
        for i in range(20):
            radius = 2 + (i * 1.2)
            a = angle + (i * 0.4)
            px = int(center_x + math.cos(a) * radius)
            py = int(center_y + math.sin(a) * radius * 0.4)
            char = VOID_CHARS[i % len(VOID_CHARS)]
            color = random.choice([Fore.MAGENTA, Fore.LIGHTMAGENTA_EX, Fore.LIGHTBLACK_EX])
            print(f"\033[{py};{px}H{color}{char}{Fore.RESET}", end="")
        sys.stdout.flush()
        time.sleep(0.07)
        angle += 0.3
    clear()


# ── Text & Typography Enhancements ──

def karaoke_reveal(text: str, delay: float = 0.15) -> None:
    """Word-by-word reveal with blinking cursor."""
    words = text.split()
    for i, word in enumerate(words):
        displayed = " ".join(words[:i + 1])
        cursor = f"{Fore.LIGHTCYAN_EX}_{Fore.RESET}" if i < len(words) - 1 else ""
        sys.stdout.write(f"\r{displayed}{cursor}")
        sys.stdout.flush()
        time.sleep(delay)
    print()


def wavy_text(text: str, amplitude: int = 3, cycles: int = 2) -> None:
    """Sine-wave vertical offset text animation."""
    for cycle in range(cycles):
        for phase in range(0, 360, 15):
            clear()
            lines = [""] * (amplitude * 2 + 1)
            for i, ch in enumerate(text):
                y_offset = int(math.sin(math.radians(phase + i * 20)) * amplitude)
                line_idx = y_offset + amplitude
                # Pad to position
                while len(lines[line_idx]) < i:
                    lines[line_idx] += " "
                color = NEON_CYCLE[i % len(NEON_CYCLE)]
                lines[line_idx] += f"{color}{ch}{Fore.RESET}"
            print("\n".join(lines))
            sys.stdout.flush()
            time.sleep(0.04)
    clear()
    print(text)


def shaking_text(text: str, intensity: int = 3, duration: float = 0.8) -> None:
    """Violent shake effect for danger/warning text."""
    end_time = time.time() + duration
    while time.time() < end_time:
        offset_x = random.randint(-intensity, intensity)
        offset_y = random.randint(0, intensity)
        clear()
        print("\n" * offset_y + " " * max(0, offset_x) + f"{Fore.LIGHTRED_EX}{Style.BRIGHT}{text}{Style.RESET_ALL}{Fore.RESET}")
        sys.stdout.flush()
        time.sleep(0.04)
    clear()
    print(f"{Fore.LIGHTRED_EX}{Style.BRIGHT}{text}{Style.RESET_ALL}{Fore.RESET}")


def gradient_scroll(text: str, duration: float = 1.0) -> None:
    """Animated gradient text scrolling effect."""
    end_time = time.time() + duration
    offset = 0
    while time.time() < end_time:
        display = []
        for i, ch in enumerate(text):
            color_idx = (i + offset) % len(NEON_CYCLE)
            display.append(f"{NEON_CYCLE[color_idx]}{ch}{Fore.RESET}")
        sys.stdout.write(f"\r{''.join(display)}")
        sys.stdout.flush()
        time.sleep(0.06)
        offset += 1
    print()


# ── Interactive UI Enhancements ──


def animated_cursor_menu(title_text: str, options: list, footer: str | None = None) -> str:
    """Pulsing neon cursor menu with arrow-key-like feel."""
    clear()
    cursor = f"{Fore.LIGHTYELLOW_EX}{Style.BRIGHT}> {Style.RESET_ALL}{Fore.RESET}"
    selected = 0

    # Quick pulse intro
    for _ in range(2):
        for bright in (True, False):
            clear()
            title_color = Fore.LIGHTMAGENTA_EX if bright else Fore.MAGENTA
            print(f"\n{title_color}{Style.BRIGHT}  {title_text}{Style.RESET_ALL}{Fore.RESET}\n")
            sys.stdout.flush()
            time.sleep(0.1)

    # Static display with cursor
    clear()
    print(f"\n{Fore.LIGHTMAGENTA_EX}{Style.BRIGHT}  {title_text}{Style.RESET_ALL}{Fore.RESET}\n")
    for idx, opt in enumerate(options):
        if isinstance(opt, (list, tuple)):
            key, label = str(opt[0]), str(opt[1])
        else:
            key, label = str(idx + 1), str(opt)
        prefix = cursor if idx == selected else "  "
        print(f"{prefix}{Fore.LIGHTCYAN_EX}[{key}]{Fore.RESET} {label}")
    if footer:
        print(f"\n{Fore.LIGHTBLACK_EX}  {footer}{Fore.RESET}")
    else:
        print(f"\n{Fore.LIGHTYELLOW_EX}  Type the number and press ENTER{Fore.RESET}")
    sys.stdout.flush()

    # Get user input
    while True:
        try:
            choice = input(f"\n{Fore.CYAN}👉 {Fore.RESET}").strip()
            # Try to match by key first
            for idx, opt in enumerate(options):
                if isinstance(opt, (list, tuple)):
                    key = str(opt[0])
                else:
                    key = str(idx + 1)
                if choice == key:
                    return key
            # Fallback: try numeric index
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(options):
                    if isinstance(options[idx], (list, tuple)):
                        return str(options[idx][0])
                    return str(idx + 1)
            sp(f"{Fore.RED}  Invalid choice! Try again.{Fore.RESET}")
        except (EOFError, KeyboardInterrupt):
            return ""


def toast_notification(message: str, toast_type: str = "info", stack: list | None = None) -> None:
    """Display a stacking toast popup notification."""
    from config import TOAST_COLORS
    color = TOAST_COLORS.get(toast_type, Fore.LIGHTCYAN_EX)
    border = f"{color}╔{'═' * (len(message) + 4)}╗{Fore.RESET}"
    middle = f"{color}║{Fore.RESET}  {message}  {color}║{Fore.RESET}"
    footer = f"{color}╚{'═' * (len(message) + 4)}╝{Fore.RESET}"
    toast_text = f"{border}\n{middle}\n{footer}"
    if stack is not None:
        stack.append(toast_text)
        # Keep only last 5 toasts
        while len(stack) > 5:
            stack.pop(0)
        clear()
        for t in stack:
            print(t)
            print()
        sys.stdout.flush()
        time.sleep(0.4)
    else:
        print(toast_text)
        sys.stdout.flush()
        time.sleep(0.4)


def rarity_glow_border(text: str, rarity: str = "Common", cycles: int = 2) -> None:
    """Dynamic rarity border with glow effect."""
    from config import RARITY_COLORS, RARITY_GLOW_CHARS
    color = RARITY_COLORS.get(rarity, Fore.WHITE)
    chars = RARITY_GLOW_CHARS.get(rarity, ("─", "│", "┌", "┐", "└", "┘"))
    h, v, tl, tr, bl, br = chars
    width = min(PANEL_WIDTH, len(_strip_ansi(text)) + 8)
    for _ in range(cycles):
        for bright in (True, False):
            clear()
            border_color = color if bright else Fore.LIGHTBLACK_EX
            horizontal = border_color + h * width + Fore.RESET
            padding = " " * ((width - len(_strip_ansi(text)) - 2) // 2)
            print(f"{border_color}{tl}{horizontal[1:-1]}{tr}{Fore.RESET}")
            print(f"{border_color}{v}{Fore.RESET}{padding}{text}{padding}{border_color}{v}{Fore.RESET}")
            print(f"{border_color}{bl}{horizontal[1:-1]}{br}{Fore.RESET}")
            sys.stdout.flush()
            time.sleep(0.15)
    clear()


def animated_header_footer(text: str, style: str = "rune", cycles: int = 2) -> None:
    """Flowing rune animation for headers/footers."""
    from config import RUNE_CHARS
    width = PANEL_WIDTH
    for _ in range(cycles):
        for offset in range(0, len(RUNE_CHARS), 2):
            rune_line = ""
            for i in range(width):
                idx = (i + offset) % len(RUNE_CHARS)
                color = NEON_CYCLE[idx % len(NEON_CYCLE)]
                rune_line += f"{color}{RUNE_CHARS[idx]}{Fore.RESET}"
            sys.stdout.write(f"\r{rune_line}")
            sys.stdout.flush()
            time.sleep(0.08)
    print()
    print(f"{Fore.LIGHTMAGENTA_EX}{Style.BRIGHT}{text.center(width)}{Style.RESET_ALL}{Fore.RESET}")
    for _ in range(cycles):
        for offset in range(0, len(RUNE_CHARS), 2):
            rune_line = ""
            for i in range(width):
                idx = (i + offset) % len(RUNE_CHARS)
                color = NEON_CYCLE[idx % len(NEON_CYCLE)]
                rune_line += f"{color}{RUNE_CHARS[idx]}{Fore.RESET}"
            sys.stdout.write(f"\r{rune_line}")
            sys.stdout.flush()
            time.sleep(0.08)
    print()


# ═══════════════════════════════════════════════════════════════════════════════
#  LEGACY UI HELPERS (for backward compatibility with game_functions.py & utils.py)
# ═══════════════════════════════════════════════════════════════════════════════

def visible_len(text: str) -> int:
    """Return visible length of text after stripping ANSI codes."""
    return len(ANSI_PATTERN.sub("", text))


def pad(text: str, width: int) -> str:
    """Pad text to given visible width."""
    extra = max(0, width - visible_len(text))
    return f"{text}{' ' * extra}"


def line(char: str = "═", color: str = Fore.CYAN) -> str:
    """Return a horizontal line string."""
    return f"{color}{char * PANEL_WIDTH}{Fore.RESET}"


def title(text: str, color: str = Fore.LIGHTCYAN_EX) -> str:
    """Return a centered title with decorative borders."""
    visible = visible_len(text)
    if visible >= PANEL_WIDTH - 4:
        return f"{color}{Style.BRIGHT}{text}{Style.RESET_ALL}{Fore.RESET}"
    left = (PANEL_WIDTH - visible - 2) // 2
    right = PANEL_WIDTH - visible - left - 2
    return (
        f"{color}{Style.BRIGHT}"
        + "═" * left
        + f" {text} "
        + "═" * right
        + f"{Style.RESET_ALL}{Fore.RESET}"
    )


def panel(title_text: str, lines: List[str], color: str = Fore.CYAN) -> str:
    """Return a bordered panel string."""
    border = f"{color}╔{'═' * (PANEL_WIDTH - 2)}╗{Fore.RESET}"
    footer = f"{color}╚{'═' * (PANEL_WIDTH - 2)}╝{Fore.RESET}"
    title_line = f"{color}║{Fore.RESET}{Style.BRIGHT}{pad(title_text.center(PANEL_WIDTH - 2), PANEL_WIDTH - 2)}{Style.RESET_ALL}{color}║{Fore.RESET}"
    body = [f"{color}║{Fore.RESET}{pad(line, PANEL_WIDTH - 2)}{color}║{Fore.RESET}" for line in lines]
    return "\n".join([border, title_line, *body, footer])


def prompt(text: str) -> str:
    """Styled input prompt."""
    return input(f"{Fore.LIGHTCYAN_EX}{text}{Fore.RESET}").strip()


def choice_prompt(text: str) -> str:
    """Styled choice prompt."""
    return input(f"{Fore.LIGHTYELLOW_EX}{text}{Fore.RESET}").strip()


def progress_bar(percent: int, width: int = 40, fill: str = "█", empty: str = "░") -> str:
    """Return a progress bar string."""
    filled = int(width * percent / 100)
    bar = f"{Fore.LIGHTGREEN_EX}{fill * filled}{Fore.LIGHTBLACK_EX}{empty * (width - filled)}{Fore.RESET}"
    return f"[{bar}] {percent}%"


def header_art() -> str:
    """Return ASCII header art."""
    art = [
        f"{Fore.MAGENTA}    ╔══════════════════════════════════════════════════════════════════════╗{Fore.RESET}",
        f"{Fore.LIGHTMAGENTA_EX}    ║{Fore.LIGHTCYAN_EX}   █████╗ ██████╗  ██████╗ █████╗ ███╗   ██╗███████╗{Fore.MAGENTA}                ║{Fore.RESET}",
        f"{Fore.LIGHTMAGENTA_EX}    ║{Fore.LIGHTCYAN_EX}  ██╔══██╗██╔══██╗██╔════╝██╔══██╗████╗  ██║██╔════╝{Fore.MAGENTA}                ║{Fore.RESET}",
        f"{Fore.LIGHTMAGENTA_EX}    ║{Fore.LIGHTCYAN_EX}  ███████║██████╔╝██║     ███████║██╔██╗ ██║█████╗  {Fore.MAGENTA}                ║{Fore.RESET}",
        f"{Fore.LIGHTMAGENTA_EX}    ║{Fore.LIGHTCYAN_EX}  ██╔══██║██╔══██╗██║     ██╔══██║██║╚██╗██║██╔══╝  {Fore.MAGENTA}                ║{Fore.RESET}",
        f"{Fore.LIGHTMAGENTA_EX}    ║{Fore.LIGHTCYAN_EX}  ██║  ██║██║  ██║╚██████╗██║  ██║██║ ╚████║███████╗{Fore.MAGENTA}                ║{Fore.RESET}",
        f"{Fore.LIGHTMAGENTA_EX}    ║{Fore.LIGHTCYAN_EX}  ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝{Fore.MAGENTA}                ║{Fore.RESET}",
        f"{Fore.MAGENTA}    ╚══════════════════════════════════════════════════════════════════════╝{Fore.RESET}",
    ]
    return "\n".join(art)


def footer_art() -> str:
    """Return ASCII footer art."""
    return f"{Fore.MAGENTA}    ══════════════════════════════════════════════════════════════════════{Fore.RESET}"


def small_header(text: str) -> str:
    """Return a small header line."""
    return title(text, Fore.LIGHTMAGENTA_EX)


def status_bar(text: str) -> str:
    """Return a status bar string."""
    return f"{Fore.LIGHTBLACK_EX}  [{text}]{Fore.RESET}"


def menu_option(key: str, label: str, emoji: str = "", color: str = Fore.LIGHTWHITE_EX) -> str:
    """Return a formatted menu option string."""
    emoji_str = f"{emoji} " if emoji else ""
    return f"  {color}[{key}]{Fore.RESET} {emoji_str}{label}"


def info_line(text: str) -> str:
    """Return an info line string."""
    return f"{Fore.LIGHTBLACK_EX}  ℹ {text}{Fore.RESET}"


def divider() -> str:
    """Return a divider line."""
    return line("─", Fore.LIGHTBLACK_EX)


def _gradient_text(text: str, start_color: tuple = (255, 0, 255), end_color: tuple = (0, 255, 255)) -> str:
    """Return text with a gradient color effect."""
    out = []
    length = len(text)
    for i, ch in enumerate(text):
        ratio = i / max(1, length - 1)
        r = int(start_color[0] + (end_color[0] - start_color[0]) * ratio)
        g = int(start_color[1] + (end_color[1] - start_color[1]) * ratio)
        b = int(start_color[2] + (end_color[2] - start_color[2]) * ratio)
        out.append(f"\033[38;2;{r};{g};{b}m{ch}\033[0m")
    return "".join(out)


def screen_shake(duration: float = 0.5, intensity: int = 3) -> None:
    """Shake the screen violently."""
    end_time = time.time() + duration
    while time.time() < end_time:
        offset_x = random.randint(-intensity, intensity)
        offset_y = random.randint(-intensity, intensity)
        print(f"\033[{offset_y};{offset_x}H", end="")
        sys.stdout.flush()
        time.sleep(0.04)
    print("\033[H", end="")


# Aliases for compatibility
fancy_menu = animated_cursor_menu
interactive_menu = animated_cursor_menu

