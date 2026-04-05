from __future__ import annotations

from dataclasses import dataclass
import json
import re
import sys


class Color:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"


STAT_ORDER = ("ATK", "DEF", "HP", "SPD")
BLOCK_WIDTH = 26
FRAME_WIDTH = BLOCK_WIDTH - 4
BORDER = "+" + "-" * (BLOCK_WIDTH - 2) + "+"
LAYOUT_WIDTH = BLOCK_WIDTH * 4 + 6

STAT_COLORS = {
    "ATK": Color.RED,
    "DEF": Color.BLUE,
    "HP": Color.GREEN,
    "SPD": Color.CYAN,
}

BRANCH_LAYOUT = (
    ("ATK", "ATK / OFFENSE"),
    ("DEF", "DEF / GUARD"),
    ("HP", "HP / VITALITY"),
    ("SPD", "SPD / VELOCITY"),
)

ANSI_PATTERN = re.compile(r"\033\[[0-9;]*m")


def paint(text: str, *styles: str) -> str:
    return "".join(styles) + text + Color.RESET


def clear_screen() -> None:
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def frame(text: str) -> str:
    padding = max(0, FRAME_WIDTH - len(ANSI_PATTERN.sub("", text)))
    return f"| {text}{' ' * padding} |"


def center_line(text: str) -> str:
    return text.center(LAYOUT_WIDTH)


@dataclass(frozen=True)
class SkillNode:
    node_id: str
    name: str
    stat: str
    bonus: int
    cost: int
    description: str
    parents: tuple[str, ...]


class ArcaneSkillTree:
    def __init__(self, starting_points: int = 12) -> None:
        self.starting_points = starting_points
        self.nodes = self._build_nodes()
        self.unlocked = {"CORE"}
        self.skill_points = starting_points
        self.last_message = "The Arcane Core is awake. Tier-one nodes are ready."

    def _build_nodes(self) -> dict[str, SkillNode]:
        # Each branch is linear so the main game can later attach it to player progression cleanly.
        return {
            "CORE": SkillNode(
                "CORE",
                "Arcane Core",
                "CORE",
                0,
                0,
                "The heart of the tree. Every path draws its power from here.",
                (),
            ),
            "A1": SkillNode(
                "A1",
                "Ember Grip",
                "ATK",
                3,
                1,
                "Temper your strikes until every hit lands with sharper force.",
                ("CORE",),
            ),
            "A2": SkillNode(
                "A2",
                "War Drums",
                "ATK",
                5,
                2,
                "Battle rhythm surges through your team and turns aggression into pressure.",
                ("A1",),
            ),
            "A3": SkillNode(
                "A3",
                "Ruin Mark",
                "ATK",
                7,
                3,
                "Once enemies are tagged by your will, every follow-up strike bites harder.",
                ("A2",),
            ),
            "A4": SkillNode(
                "A4",
                "Cataclysm",
                "ATK",
                10,
                4,
                "A brutal finisher path that turns raw offense into a boss killer.",
                ("A3",),
            ),
            "D1": SkillNode(
                "D1",
                "Iron Skin",
                "DEF",
                3,
                1,
                "Your stance hardens, shaving damage off every incoming blow.",
                ("CORE",),
            ),
            "D2": SkillNode(
                "D2",
                "Stonewall",
                "DEF",
                5,
                2,
                "Anchor your footing and turn defense into a steady front line.",
                ("D1",),
            ),
            "D3": SkillNode(
                "D3",
                "Mirror Plate",
                "DEF",
                7,
                3,
                "Layered warding makes you absurdly difficult to crack.",
                ("D2",),
            ),
            "D4": SkillNode(
                "D4",
                "Last Bastion",
                "DEF",
                10,
                4,
                "A fortress-state capstone that keeps your squad standing deep into fights.",
                ("D3",),
            ),
            "H1": SkillNode(
                "H1",
                "Wild Heart",
                "HP",
                30,
                1,
                "A stronger pulse floods the body with more staying power.",
                ("CORE",),
            ),
            "H2": SkillNode(
                "H2",
                "Giant Blood",
                "HP",
                45,
                2,
                "Ancient vitality thickens your blood and expands your endurance.",
                ("H1",),
            ),
            "H3": SkillNode(
                "H3",
                "Phoenix Pulse",
                "HP",
                60,
                3,
                "Vital energy roars hotter, making you far harder to put down.",
                ("H2",),
            ),
            "H4": SkillNode(
                "H4",
                "Titan Soul",
                "HP",
                100,
                4,
                "A monstrous life pool that lets your build shrug off long encounters.",
                ("H3",),
            ),
            "S1": SkillNode(
                "S1",
                "Fleetstep",
                "SPD",
                3,
                1,
                "Your movement sharpens and the whole build starts feeling lighter.",
                ("CORE",),
            ),
            "S2": SkillNode(
                "S2",
                "Quickdraw",
                "SPD",
                5,
                2,
                "Faster reactions let you get ahead of enemy turns more often.",
                ("S1",),
            ),
            "S3": SkillNode(
                "S3",
                "Blurstride",
                "SPD",
                7,
                3,
                "You move so cleanly that enemies start reacting a beat too late.",
                ("S2",),
            ),
            "S4": SkillNode(
                "S4",
                "Time Split",
                "SPD",
                10,
                4,
                "A speed capstone that makes your commander feel almost unfair.",
                ("S3",),
            ),
        }

    def branch_nodes(self, stat: str) -> list[SkillNode]:
        return [node for node in self.nodes.values() if node.stat == stat]

    def buffs(self) -> dict[str, int]:
        totals = {stat: 0 for stat in STAT_ORDER}
        for node_id in self.unlocked:
            node = self.nodes[node_id]
            if node.stat in totals:
                totals[node.stat] += node.bonus
        return totals

    def branch_total(self, stat: str) -> int:
        return self.buffs()[stat]

    def status(self, node_id: str) -> str:
        node = self.nodes[node_id]
        if node_id in self.unlocked:
            return "unlocked"
        if not all(parent in self.unlocked for parent in node.parents):
            return "locked"
        if self.skill_points < node.cost:
            return "expensive"
        return "available"

    def missing_parents(self, node_id: str) -> list[str]:
        return [parent for parent in self.nodes[node_id].parents if parent not in self.unlocked]

    def unlock(self, node_id: str) -> tuple[bool, str]:
        node_id = node_id.upper()
        if node_id not in self.nodes or node_id == "CORE":
            return False, f"'{node_id}' is not a valid unlockable node."

        node = self.nodes[node_id]
        node_status = self.status(node_id)
        if node_status == "unlocked":
            return False, f"{node.name} is already unlocked."
        if node_status == "locked":
            missing = ", ".join(self.missing_parents(node_id))
            return False, f"{node.name} is locked. Unlock {missing} first."
        if node_status == "expensive":
            return False, f"{node.name} needs {node.cost} points, but you only have {self.skill_points}."

        self.unlocked.add(node_id)
        self.skill_points -= node.cost
        self.last_message = f"{node.name} unlocked. {node.stat} increased by {node.bonus}."
        return True, self.last_message

    def reset(self) -> str:
        self.unlocked = {"CORE"}
        self.skill_points = self.starting_points
        self.last_message = "The tree has been reset. Every point is back in your pool."
        return self.last_message

    def snapshot(self) -> dict[str, object]:
        unlocked_nodes = [node_id for node_id in self.nodes if node_id in self.unlocked and node_id != "CORE"]
        return {
            "Skill Points Left": self.skill_points,
            "Unlocked Nodes": unlocked_nodes,
            "Buffs": self.buffs(),
        }

    def _status_marker(self, node_id: str) -> str:
        markers = {
            "unlocked": paint("*", Color.GREEN, Color.BOLD),
            "available": paint("+", Color.YELLOW, Color.BOLD),
            "expensive": paint("!", Color.MAGENTA, Color.BOLD),
            "locked": paint("-", Color.DIM),
        }
        return markers[self.status(node_id)]

    def _node_name_line(self, node: SkillNode) -> str:
        return f"[{self._status_marker(node.node_id)}] {node.node_id:<3} {node.name[:13]:<13}"

    def _node_info_line(self, node: SkillNode) -> str:
        buff_text = paint(f"+{node.bonus} {node.stat}", STAT_COLORS[node.stat], Color.BOLD)
        return f"Cost {node.cost} | Buff {buff_text}"

    def _node_need_line(self, node: SkillNode) -> str:
        return f"Needs {node.parents[0]}"

    def _render_branch_blocks(self) -> str:
        # Fixed-height blocks keep the tree readable even in a basic terminal window.
        blocks: list[list[str]] = []
        for stat, title in BRANCH_LAYOUT:
            block = [
                paint(BORDER, STAT_COLORS[stat]),
                paint(frame(title.center(FRAME_WIDTH)), STAT_COLORS[stat], Color.BOLD),
                paint(BORDER, STAT_COLORS[stat]),
            ]
            for node in self.branch_nodes(stat):
                block.append(frame(self._node_name_line(node)))
                block.append(frame(self._node_info_line(node)))
                block.append(frame(self._node_need_line(node)))
                block.append(paint(BORDER, STAT_COLORS[stat]))
            total_line = paint(f"+{self.branch_total(stat)} {stat}", STAT_COLORS[stat], Color.BOLD)
            block.append(frame(f"Branch Total {total_line}"))
            block.append(paint(BORDER, STAT_COLORS[stat]))
            blocks.append(block)

        rows = []
        for line_index in range(len(blocks[0])):
            rows.append("  ".join(block[line_index] for block in blocks))
        return "\n".join(rows)

    def render(self) -> str:
        buffs = self.buffs()
        spent = self.starting_points - self.skill_points
        buff_line = " | ".join(
            paint(f"{stat} +{buffs[stat]}", STAT_COLORS[stat], Color.BOLD) for stat in STAT_ORDER
        )

        sections = [
            "=" * LAYOUT_WIDTH,
            paint(center_line("ARCANE HEROES :: CONSTELLATION SKILL TREE"), Color.BOLD, Color.WHITE),
            center_line("Spend points to shape your buff build across ATK, DEF, HP, and SPD."),
            "=" * LAYOUT_WIDTH,
            f"Skill Points Left: {self.skill_points:>2} / {self.starting_points}   Points Spent: {spent}",
            f"Total Buffs: {buff_line}",
            "Legend: [*] unlocked   [+] ready   [!] not enough points   [-] locked",
            "",
            paint(center_line("[*] CORE  Arcane Core"), Color.MAGENTA, Color.BOLD),
            center_line("Every branch begins here. Tier one nodes are open from the start."),
            "",
            self._render_branch_blocks(),
            "",
            "-" * LAYOUT_WIDTH,
            paint(self.last_message[:LAYOUT_WIDTH], Color.YELLOW),
            "Commands: unlock <id> | inspect <id> | export | reset | help | quit",
        ]
        return "\n".join(sections)

    def inspect_screen(self, node_id: str) -> str:
        node_id = node_id.upper()
        if node_id not in self.nodes:
            return f"'{node_id}' is not a valid node."

        node = self.nodes[node_id]
        status = self.status(node_id) if node_id != "CORE" else "unlocked"
        requires = ", ".join(node.parents) if node.parents else "none"
        lines = [
            "=" * LAYOUT_WIDTH,
            paint(center_line(f"NODE {node.node_id} :: {node.name}"), Color.BOLD, Color.WHITE),
            "=" * LAYOUT_WIDTH,
            f"Status: {status}",
            f"Stat: {node.stat}",
            f"Buff: +{node.bonus}",
            f"Cost: {node.cost}",
            f"Requires: {requires}",
            "",
            node.description,
            "",
            "Press ENTER to return to the tree.",
        ]
        return "\n".join(lines)

    def help_screen(self) -> str:
        lines = [
            "=" * LAYOUT_WIDTH,
            paint(center_line("COMMAND HELP"), Color.BOLD, Color.WHITE),
            "=" * LAYOUT_WIDTH,
            "unlock <id>   Unlock a node if its parent path is complete and you have enough points.",
            "inspect <id>  Show the flavor text, cost, and requirements for one node.",
            "export        Print the exact buff payload you can plug into the main game later.",
            "reset         Return every spent point and lock the branches again.",
            "quit          Exit the prototype and keep the final build summary on screen.",
            "",
            "Example: unlock A1",
            "Example: inspect S4",
            "",
            "Press ENTER to return to the tree.",
        ]
        return "\n".join(lines)

    def export_screen(self) -> str:
        payload = json.dumps(self.snapshot(), indent=4)
        lines = [
            "=" * LAYOUT_WIDTH,
            paint(center_line("BUILD EXPORT"), Color.BOLD, Color.WHITE),
            "=" * LAYOUT_WIDTH,
            payload,
            "",
            "Press ENTER to return to the tree.",
        ]
        return "\n".join(lines)

    def final_screen(self) -> str:
        summary = json.dumps(self.snapshot(), indent=4)
        lines = [
            "=" * LAYOUT_WIDTH,
            paint(center_line("FINAL BUILD"), Color.BOLD, Color.WHITE),
            "=" * LAYOUT_WIDTH,
            summary,
            "",
            "Prototype closed. You can now wire this data into Arcane_Heroes.py.",
        ]
        return "\n".join(lines)


def run_skill_tree() -> None:
    tree = ArcaneSkillTree()

    while True:
        clear_screen()
        print(tree.render())
        try:
            command = input("\n> ").strip()
        except EOFError:
            break

        if not command:
            tree.last_message = "No command entered. Type 'help' if you want the controls."
            continue

        parts = command.split()
        action = parts[0].lower()

        if action in {"quit", "q", "exit"}:
            break
        if action == "unlock":
            if len(parts) != 2:
                tree.last_message = "Use 'unlock <id>'. Example: unlock D2"
                continue
            _, message = tree.unlock(parts[1])
            tree.last_message = message
            continue
        if action == "inspect":
            if len(parts) != 2:
                tree.last_message = "Use 'inspect <id>'. Example: inspect H4"
                continue
            clear_screen()
            print(tree.inspect_screen(parts[1]))
            input()
            continue
        if action == "export":
            clear_screen()
            print(tree.export_screen())
            input()
            continue
        if action == "reset":
            tree.reset()
            continue
        if action == "help":
            clear_screen()
            print(tree.help_screen())
            input()
            continue

        tree.last_message = f"Unknown command: {command}"

    clear_screen()
    print(tree.final_screen())


if __name__ == "__main__":
    run_skill_tree()
