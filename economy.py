from __future__ import annotations

import json
import math
import random
import re
import time
from typing import Any, Dict, List, Tuple

from colorama import Fore, Style

from game_functions import clear, load_players, save_players, sync_player_data
from ui import (
    sp,
    crazy_transition,
    shimmer_line,
    neon_flicker,
    flash_screen,
    explosion_print,
    jitter_text,
    color_cycle_print,
    bounce_text,
    thunder_effect,
    fireworks,
    emoji_explosion,
    starfield_background,
    ANSI_PATTERN,
    loot_reveal,
    rarity_glow_border,
    toast_notification,
    scanline_reveal,
    pulsing_border,
)
from config import (
    SHOP_DATA_FILE,
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
)



def _visible_len(text: str) -> int:
    return len(ANSI_PATTERN.sub("", text))


def _pad(text: str, width: int) -> str:
    extra = max(0, width - _visible_len(text))
    return f"{text}{' ' * extra}"


def _line(char: str = "═", color: str = Fore.CYAN) -> str:
    return f"{color}{char * PANEL_WIDTH}{Fore.RESET}"


def _title(text: str, color: str = Fore.LIGHTCYAN_EX) -> str:
    visible = _visible_len(text)
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


def _panel(title: str, lines: List[str], color: str = Fore.CYAN) -> str:
    border = f"{color}╔{'═' * (PANEL_WIDTH - 2)}╗{Fore.RESET}"
    footer = f"{color}╚{'═' * (PANEL_WIDTH - 2)}╝{Fore.RESET}"
    title_line = f"{color}║{Fore.RESET}{Style.BRIGHT}{_pad(title.center(PANEL_WIDTH - 2), PANEL_WIDTH - 2)}{Style.RESET_ALL}{color}║{Fore.RESET}"
    body = [f"{color}║{Fore.RESET}{_pad(line, PANEL_WIDTH - 2)}{color}║{Fore.RESET}" for line in lines]
    return "\n".join([border, title_line, *body, footer])


def _prompt(text: str) -> str:
    return input(f"{Fore.LIGHTCYAN_EX}{text}{Fore.RESET}").strip()


def load_shop_data(filename: str = SHOP_DATA_FILE) -> Dict[str, Any]:
    with open(filename, "r", encoding="utf-8") as handle:
        return json.load(handle)


def persist_player(stats: Dict[str, Any]) -> None:
    sync_player_data(stats)
    players = load_players()
    if isinstance(players, dict) and "Account Name" in players and "Commander" in players:
        players = {players["Account Name"]: players}
    players[stats["Account Name"]] = stats
    save_players(players)


def item_map(shop_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {item["id"]: item for item in shop_data["items"]}


def add_ledger_entry(stats: Dict[str, Any], message: str, stamp: int | None = None) -> None:
    text = str(message).strip()
    if not text:
        return
    ledger = stats.setdefault("Economy Ledger", [])
    ledger.append({"at": int(stamp or time.time()), "message": text})
    if len(ledger) > LEDGER_LIMIT:
        del ledger[:-LEDGER_LIMIT]


def record_economy_event(stats: Dict[str, Any], message: str, reputation: int = 0, *, stamp: int | None = None) -> str:
    gained = max(0, int(reputation))
    if gained:
        stats["Economy Reputation"] = int(stats.get("Economy Reputation", 0)) + gained
        message = f"{message} (+{gained} Rep)"
    add_ledger_entry(stats, message, stamp=stamp)
    return message


def _resource_reward_item(stats: Dict[str, Any], reward_kind: str) -> str | None:
    commander = stats.get("Commander")
    return COMMANDER_RESOURCE_IDS.get(commander, {}).get(reward_kind)


def _resolve_reward_items(stats: Dict[str, Any], reward_def: Dict[str, Any]) -> Dict[str, int]:
    reward_items = dict(reward_def.get("items", {}))
    for reward_kind, qty in reward_def.get("commander_items", {}).items():
        item_id = _resource_reward_item(stats, reward_kind)
        if item_id:
            reward_items[item_id] = reward_items.get(item_id, 0) + int(qty)
    return reward_items


def shop_reputation_requirement(level: int) -> int:
    level = max(1, int(level))
    if level <= 1:
        return 0
    return (12 * level * level) - 8


def shop_level_progress(stats: Dict[str, Any]) -> Dict[str, Any]:
    current = int(stats.get("Shop Level", 1))
    if current >= 30:
        return {
            "next_level": current,
            "cost": 0,
            "required_reputation": int(stats.get("Economy Reputation", 0)),
            "ready": False,
            "message": "Shop Level is already capped at 30.",
            "missing_gold": 0,
            "missing_reputation": 0,
        }

    next_level = current + 1
    cost = shop_upgrade_cost(next_level)
    required_reputation = shop_reputation_requirement(next_level)
    gold = int(stats.get("Gold", 0))
    reputation = int(stats.get("Economy Reputation", 0))
    missing_gold = max(0, cost - gold)
    missing_reputation = max(0, required_reputation - reputation)
    if missing_gold and missing_reputation:
        message = f"Need {missing_gold} more Gold and {missing_reputation} more Reputation."
    elif missing_gold:
        message = f"Need {missing_gold} more Gold."
    elif missing_reputation:
        message = f"Need {missing_reputation} more Reputation."
    else:
        message = "Ready to upgrade."
    return {
        "next_level": next_level,
        "cost": cost,
        "required_reputation": required_reputation,
        "ready": not missing_gold and not missing_reputation,
        "message": message,
        "missing_gold": missing_gold,
        "missing_reputation": missing_reputation,
    }


def apply_shop_level_rewards(stats: Dict[str, Any], new_level: int, items: Dict[str, Dict[str, Any]]) -> List[str]:
    claimed = stats.setdefault("Claimed Shop Milestones", [1])
    if int(new_level) in claimed:
        return []

    reward_def = SHOP_MILESTONE_REWARDS.get(int(new_level), {})
    reward_notes: List[str] = []
    if reward_def.get("gold"):
        gold_reward = int(reward_def["gold"])
        stats["Gold"] = int(stats.get("Gold", 0)) + gold_reward
        reward_notes.append(f"{gold_reward} Gold")
    if reward_def.get("permit_hours"):
        permit_hours = int(reward_def["permit_hours"])
        expiry = int(time.time()) + (permit_hours * 3600)
        stats.setdefault("Active Permits", []).append(expiry)
        reward_notes.append(f"{permit_hours}h listing permit")

    reward_items = _resolve_reward_items(stats, reward_def)
    for item_id, qty in reward_items.items():
        add_item(stats, item_id, int(qty))
        item_name = items.get(item_id, {}).get("name", item_id)
        reward_notes.append(f"{item_name} x{qty}")

    claimed.append(int(new_level))
    claimed[:] = sorted({max(1, int(level)) for level in claimed})

    if reward_notes:
        summary = ", ".join(reward_notes)
        message = reward_def.get("message", f"Shop Level {new_level} rewards delivered.")
        return [record_economy_event(stats, f"{message} Rewards: {summary}.")]
    return []


def _market_state(stats: Dict[str, Any]) -> Dict[str, Any]:
    market_state = stats.setdefault("Market State", {})
    market_state.setdefault("bot_generated_at", 0)
    market_state.setdefault("bot_refresh_at", 0)
    market_state.setdefault("bot_listings", [])
    market_state.setdefault("player_listings", [])
    market_state.setdefault("resolved_messages", [])
    market_state.setdefault("next_listing_id", 1)
    market_state.setdefault("value_memory", {})
    market_state.setdefault("bot_traders", {})
    market_state.setdefault("value_tick", 0)
    return market_state


def _record_market_result(stats: Dict[str, Any], market_state: Dict[str, Any], message: str, reputation: int = 0) -> str:
    final_message = record_economy_event(stats, message, reputation)
    market_state.setdefault("resolved_messages", []).append(final_message)
    return final_message


def _style_voice(style: str) -> Tuple[str, str]:
    voices = {
        "sharp": ("I price by edge, not by pity.", "Bring me numbers worth hearing."),
        "calm": ("I trade in patterns, not panic.", "If you want a fair line, show me a fair offer."),
        "stubborn": ("I move stock, not my spine.", "A strong crate needs a strong price."),
        "playful": ("Fast hands make good markets.", "You can haggle, but keep up."),
        "sly": ("Every price hides a second story.", "Convince me you know the darker side of value."),
        "warm": ("Good trade leaves both sides stronger.", "I can bend, but not break the ledger."),
    }
    return voices.get(style, ("I trade by feel and figures.", "Show me a real offer."))


def _ensure_bot_traders(market_state: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    trader_book = market_state.setdefault("bot_traders", {})
    for trader in TRADER_ARCHETYPES:
        existing = trader_book.get(trader["id"], {})
        opener, closer = _style_voice(trader["style"])
        trader_book[trader["id"]] = {
            **trader,
            "mood": int(existing.get("mood", 0)),
            "deal_count": int(existing.get("deal_count", 0)),
            "last_seen": int(existing.get("last_seen", 0)),
            "opener": existing.get("opener", opener),
            "closer": existing.get("closer", closer),
        }
    return trader_book


def _value_entry(market_state: Dict[str, Any], item_id: str) -> Dict[str, Any]:
    return market_state.setdefault("value_memory", {}).setdefault(
        item_id,
        {
            "demand": 0,
            "supply": 0,
            "current_value": 0,
            "previous_value": 0,
            "trend_score": 0,
            "last_tick": 0,
            "trade_volume": 0,
            "last_trade_side": "none",
        },
    )


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _effect_value(item: Dict[str, Any]) -> float:
    total = 0.0
    for effect in item.get("use_effects", []):
        effect_type = effect.get("type")
        amount = float(effect.get("amount", 0))
        if effect_type == "grant_buff":
            stat = effect.get("stat")
            total += STAT_VALUE_WEIGHTS.get(stat, 18.0) * amount * 0.55
        elif effect_type == "grant_skill_points":
            total += 180.0 * amount
        elif effect_type == "grant_listing_permit_hours":
            total += 42.0 * amount
        else:
            total += 20.0 * amount
    return total


def _economy_value(item: Dict[str, Any]) -> float:
    total = 0.0
    for key, value in item.get("economy", {}).items():
        amount = float(value)
        if "discount" in key:
            total += 26.0 * amount
        elif "bonus" in key:
            total += 30.0 * amount
        else:
            total += 16.0 * amount
    return total


def _stat_value(item: Dict[str, Any]) -> float:
    total = 0.0
    for stat, amount in item.get("stats", {}).items():
        total += STAT_VALUE_WEIGHTS.get(stat, 14.0) * float(amount)
    return total


def item_market_value(stats: Dict[str, Any], market_state: Dict[str, Any], item: Dict[str, Any]) -> int:
    entry = _value_entry(market_state, item["id"])
    base_price = float(max(40, int(item.get("price_gold", 0))))
    rarity_mult = RARITY_VALUE_MULTIPLIERS.get(item.get("rarity"), 1.0)
    category_mult = CATEGORY_VALUE_MULTIPLIERS.get(item.get("category"), 1.0)
    commander_bonus = 1.0
    commander_element = COMMANDER_ELEMENT_NAMES.get(stats.get("Commander"))
    if commander_element and item.get("element") == commander_element:
        commander_bonus += 0.08
    if item.get("target") == "commander":
        commander_bonus += 0.04
    if item.get("stock_rule") == "one_time":
        commander_bonus += 0.12
    elif item.get("stock_rule") == "limited":
        commander_bonus += 0.06

    trend_factor = 1.0 + (_clamp(entry.get("demand", 0) - entry.get("supply", 0), -5, 5) * 0.045)
    branch_bonus = 1.0 + (len(item.get("branch_requirements", {})) * 0.035)
    derived = base_price + _stat_value(item) + _effect_value(item) + _economy_value(item)
    value = int(max(base_price * 0.55, derived * rarity_mult * category_mult * commander_bonus * trend_factor * branch_bonus))
    return value


def _trend_meta(entry: Dict[str, Any]) -> Tuple[str, str]:
    score = int(entry.get("trend_score", 0))
    for low, high, label, color in TREND_LABELS:
        if low <= score <= high:
            return label, color
    return "steady", Fore.WHITE


def _refresh_value_memory(stats: Dict[str, Any], shop_data: Dict[str, Any], market_state: Dict[str, Any]) -> None:
    now_tick = int(time.time() // 3600)
    if market_state.get("value_tick") == now_tick and market_state.get("value_memory"):
        return

    for item in shop_data["items"]:
        entry = _value_entry(market_state, item["id"])
        previous = int(entry.get("current_value", max(1, int(item.get("price_gold", 1)))))
        drift = random.randint(-1, 1)
        focus_bonus = 1 if item.get("rarity") in {"Mythic", "Legendary"} else 0
        entry["demand"] = int(_clamp(int(entry.get("demand", 0)) + drift + focus_bonus, -4, 6))
        entry["supply"] = int(_clamp(int(entry.get("supply", 0)) + random.randint(-1, 1), -4, 6))
        entry["previous_value"] = previous
        entry["current_value"] = item_market_value(stats, market_state, item)
        delta = entry["current_value"] - previous
        if previous <= 0:
            entry["trend_score"] = 0
        else:
            entry["trend_score"] = int(round((delta / previous) * 10))
        entry["last_tick"] = now_tick
    market_state["value_tick"] = now_tick


def _shift_market_signal(market_state: Dict[str, Any], item_id: str, demand_delta: int = 0, supply_delta: int = 0) -> None:
    entry = _value_entry(market_state, item_id)
    entry["demand"] = int(_clamp(int(entry.get("demand", 0)) + demand_delta, -4, 8))
    entry["supply"] = int(_clamp(int(entry.get("supply", 0)) + supply_delta, -4, 8))
    entry["trade_volume"] = int(entry.get("trade_volume", 0)) + abs(demand_delta) + abs(supply_delta)
    entry["last_trade_side"] = "demand" if demand_delta > supply_delta else "supply"


def _bundle_value(stats: Dict[str, Any], market_state: Dict[str, Any], bundle: List[Dict[str, int]], items: Dict[str, Dict[str, Any]]) -> int:
    total = 0
    for entry in bundle:
        item = items.get(entry["item_id"])
        if not item:
            continue
        total += item_market_value(stats, market_state, item) * int(entry["qty"])
    return total


def branch_point_total(shop_level: int) -> int:
    milestone_bonus = shop_level // 5
    return shop_level + milestone_bonus


def spent_branch_points(tree: Dict[str, int]) -> int:
    return sum(int(tree.get(branch, 0)) for branch in BRANCH_ORDER)


def economy_modifiers(stats: Dict[str, Any], items: Dict[str, Dict[str, Any]]) -> Dict[str, int]:
    mods = {
        "shop_discount_pct": 0,
        "sale_bonus_pct": 0,
        "market_fee_discount_pct": 0,
        "listing_cap_bonus": 0,
        "buy_order_bonus_pct": 0,
        "barter_bonus_pct": 0,
        "consumable_power_pct": 0,
        "gear_value_bonus_pct": 0,
        "prestige_access_tier": 0,
        "relic_access_tier": 0,
        "use_fee_discount_pct": 0,
    }
    tree = stats.get("Economy Tree", {})
    for branch in BRANCH_ORDER:
        rank = int(tree.get(branch, 0))
        for index in range(rank):
            if index < len(BRANCH_MODIFIERS[branch]):
                for key, value in BRANCH_MODIFIERS[branch][index].items():
                    mods[key] = mods.get(key, 0) + value

    equipped = stats.get("Equipped Items", {}).get("Commander", {})
    for item_id in equipped.values():
        if not item_id:
            continue
        item = items.get(item_id)
        if not item:
            continue
        for key, value in item.get("economy", {}).items():
            mods[key] = mods.get(key, 0) + int(value)

    now = int(time.time())
    active_permits = [expiry for expiry in stats.get("Active Permits", []) if expiry > now]
    stats["Active Permits"] = active_permits
    mods["listing_cap_bonus"] += len(active_permits)
    return mods


def listing_cap(stats: Dict[str, Any], items: Dict[str, Dict[str, Any]]) -> int:
    mods = economy_modifiers(stats, items)
    return 2 + mods.get("listing_cap_bonus", 0)


def shop_upgrade_cost(next_level: int) -> int:
    next_level = max(2, int(next_level))
    return 120 + (next_level * 90) + ((next_level // 4) * 60)


def next_shop_level_state(stats: Dict[str, Any]) -> Tuple[int, int, bool, str]:
    progress = shop_level_progress(stats)
    return progress["next_level"], progress["cost"], progress["ready"], progress["message"]


def _clean_history(history: List[int], window_seconds: int, now: int) -> List[int]:
    return [stamp for stamp in history if now - int(stamp) < window_seconds]


def purchase_history(stats: Dict[str, Any], item_id: str) -> List[int]:
    history = stats.setdefault("Shop Purchase History", {}).setdefault(item_id, [])
    return [int(stamp) for stamp in history]


def available_stock(stats: Dict[str, Any], item: Dict[str, Any], now: int) -> Tuple[int | None, str]:
    rule = item.get("stock_rule", "unlimited")
    history = purchase_history(stats, item["id"])
    if rule == "unlimited":
        return None, "Unlimited"
    if rule == "one_time":
        remaining = 0 if history else 1
        return remaining, "One-time"

    window_seconds = int(item.get("restock_seconds", 3600))
    limit = int(item.get("stock_limit", 1))
    live_history = _clean_history(history, window_seconds, now)
    stats["Shop Purchase History"][item["id"]] = live_history
    remaining = max(0, limit - len(live_history))
    minutes = max(1, math.ceil(window_seconds / 60))
    return remaining, f"{remaining}/{limit} this {minutes}m cycle"


def can_view_item(stats: Dict[str, Any], item: Dict[str, Any]) -> Tuple[bool, str]:
    if int(stats.get("Shop Level", 1)) < int(item.get("unlock_shop_level", 1)):
        return False, f"Shop Lv {item.get('unlock_shop_level', 1)}"

    tree = stats.get("Economy Tree", {})
    for branch, needed in item.get("branch_requirements", {}).items():
        if int(tree.get(branch, 0)) < int(needed):
            return False, f"{branch} {needed}"
    return True, ""


def _category_items(shop_data: Dict[str, Any], category: str) -> List[Dict[str, Any]]:
    return [item for item in shop_data["items"] if item["category"] == category]


def unlock_reason_text(reason: str) -> str:
    if reason.startswith("Shop Lv "):
        required = reason.replace("Shop Lv ", "")
        return f"Needs Shop Lv {required}"
    if " " in reason:
        branch, rank = reason.rsplit(" ", 1)
        if rank.isdigit():
            return f"Needs {branch} rank {rank}"
    return reason


def _owned_qty(stats: Dict[str, Any], item_id: str) -> int:
    return int(stats.get("Items", {}).get(item_id, 0))


def _meta(stats: Dict[str, Any], item_id: str) -> Dict[str, Any]:
    stats.setdefault("Item Meta", {})
    return stats["Item Meta"].setdefault(
        item_id,
        {
            "avg_acquired_at": float(time.time()),
            "action_age": 0.0,
            "use_count": 0.0,
            "reserved_qty": 0,
            "favorite": False,
        },
    )


def equipped_count(stats: Dict[str, Any], item_id: str) -> int:
    count = 0
    equipped = stats.get("Equipped Items", {})
    for slot_item in equipped.get("Commander", {}).values():
        if slot_item == item_id:
            count += 1
    for hero_slots in equipped.get("Heroes", {}).values():
        if isinstance(hero_slots, dict):
            for slot_item in hero_slots.values():
                if slot_item == item_id:
                    count += 1
    return count


def available_inventory_qty(stats: Dict[str, Any], item_id: str) -> int:
    meta = _meta(stats, item_id)
    qty = _owned_qty(stats, item_id)
    return max(0, qty - int(meta.get("reserved_qty", 0)) - equipped_count(stats, item_id))


def reserved_inventory_qty(stats: Dict[str, Any], item_id: str) -> int:
    return int(_meta(stats, item_id).get("reserved_qty", 0))


def commander_slot_item(stats: Dict[str, Any], slot: str) -> str | None:
    return stats.get("Equipped Items", {}).get("Commander", {}).get(slot)


def commander_slot_item_data(stats: Dict[str, Any], slot: str, items: Dict[str, Dict[str, Any]]) -> Dict[str, Any] | None:
    item_id = commander_slot_item(stats, slot)
    if not item_id:
        return None
    return items.get(item_id)


def item_score(item: Dict[str, Any] | None) -> int:
    if not item:
        return 0
    return int(round(_stat_value(item) + _economy_value(item)))


def _diff_map(candidate: Dict[str, Any] | None, current: Dict[str, Any] | None, field: str) -> Dict[str, int]:
    delta: Dict[str, int] = {}
    keys = set()
    if candidate:
        keys.update(candidate.get(field, {}).keys())
    if current:
        keys.update(current.get(field, {}).keys())
    for key in sorted(keys):
        candidate_value = int((candidate or {}).get(field, {}).get(key, 0))
        current_value = int((current or {}).get(field, {}).get(key, 0))
        change = candidate_value - current_value
        if change:
            delta[key] = change
    return delta


def _format_delta_map(delta: Dict[str, int], labels: Dict[str, str] | None = None) -> str:
    if not delta:
        return "no change"
    parts = []
    for key, value in delta.items():
        label = labels.get(key, key) if labels else key
        sign = "+" if value > 0 else ""
        suffix = "%" if key.endswith("_pct") else ""
        parts.append(f"{label} {sign}{value}{suffix}")
    return ", ".join(parts)


def _slot_upgrade_text(stats: Dict[str, Any], item: Dict[str, Any], items: Dict[str, Dict[str, Any]]) -> str:
    slot = item.get("slot")
    if not slot or item.get("target") not in {"commander", "any"}:
        return "Utility"
    current = commander_slot_item_data(stats, slot, items)
    if not current:
        return "New slot fill"
    delta = item_score(item) - item_score(current)
    if delta > 0:
        return f"Upgrade +{delta}"
    if delta < 0:
        return f"Downgrade {delta}"
    return "Sidegrade"


def _slot_delta_text(stats: Dict[str, Any], item: Dict[str, Any], items: Dict[str, Dict[str, Any]]) -> Tuple[str, str]:
    slot = item.get("slot")
    if not slot or item.get("target") not in {"commander", "any"}:
        return "Target: commander loadout only", "Economy delta: no slot comparison"
    current = commander_slot_item_data(stats, slot, items)
    if not current:
        stat_delta = _format_delta_map({key: int(value) for key, value in item.get("stats", {}).items()})
        economy_delta = _format_delta_map(
            {key: int(value) for key, value in item.get("economy", {}).items()},
            MODIFIER_LABELS,
        )
        return f"Slot delta vs empty: {stat_delta}", f"Economy delta vs empty: {economy_delta}"
    stat_delta = _format_delta_map(_diff_map(item, current, "stats"))
    economy_delta = _format_delta_map(_diff_map(item, current, "economy"), MODIFIER_LABELS)
    return f"Slot delta vs {current['name']}: {stat_delta}", f"Economy delta vs {current['name']}: {economy_delta}"


def loadout_summary(stats: Dict[str, Any], items: Dict[str, Dict[str, Any]]) -> str:
    equipped = stats.get("Equipped Items", {}).get("Commander", {})
    filled_slots = []
    for slot, item_id in equipped.items():
        if item_id:
            item_name = items.get(item_id, {}).get("name", item_id)
            filled_slots.append(f"{LOADOUT_SLOT_LABELS.get(slot, slot.title())}: {item_name}")
    if not filled_slots:
        return "No commander gear equipped."
    return " | ".join(filled_slots[:3]) + (" ..." if len(filled_slots) > 3 else "")


def _modifier_lines(mods: Dict[str, int]) -> List[str]:
    lines = []
    for key in [
        "shop_discount_pct",
        "sale_bonus_pct",
        "market_fee_discount_pct",
        "listing_cap_bonus",
        "buy_order_bonus_pct",
        "barter_bonus_pct",
        "consumable_power_pct",
        "gear_value_bonus_pct",
        "relic_access_tier",
        "prestige_access_tier",
    ]:
        value = int(mods.get(key, 0))
        if value:
            suffix = "%" if key.endswith("_pct") else ""
            lines.append(f"{MODIFIER_LABELS.get(key, key)}: +{value}{suffix}")
    return lines or ["No active economy modifiers yet."]


def commander_slot_candidates(stats: Dict[str, Any], items: Dict[str, Dict[str, Any]], slot: str) -> List[Tuple[str, Dict[str, Any]]]:
    candidates = []
    for item_id, item in _list_owned_items(stats, items):
        if item.get("slot") != slot:
            continue
        if item.get("target") not in {"commander", "any"}:
            continue
        if available_inventory_qty(stats, item_id) <= 0:
            continue
        candidates.append((item_id, item))
    candidates.sort(key=lambda pair: (-item_score(pair[1]), pair[1]["name"]))
    return candidates


def equip_commander_item(stats: Dict[str, Any], item_id: str, items: Dict[str, Dict[str, Any]]) -> Tuple[bool, str]:
    item = items.get(item_id)
    if not item:
        return False, "That item no longer exists."
    slot = item.get("slot")
    if not slot:
        return False, "This item cannot be equipped."
    if item.get("target") not in {"commander", "any"}:
        return False, "Commander loadouts only support commander-ready gear right now."
    if available_inventory_qty(stats, item_id) <= 0:
        return False, "No free copy available to equip."

    commander_slots = stats.setdefault("Equipped Items", {}).setdefault("Commander", {})
    previous_id = commander_slots.get(slot)
    commander_slots[slot] = item_id
    previous_name = items.get(previous_id, {}).get("name", previous_id) if previous_id else None
    if previous_id == item_id:
        message = f"{item['name']} remains equipped to {LOADOUT_SLOT_LABELS.get(slot, slot)}."
    elif previous_name:
        message = f"Equipped {item['name']} to {LOADOUT_SLOT_LABELS.get(slot, slot)} and stored {previous_name}."
    else:
        message = f"Equipped {item['name']} to {LOADOUT_SLOT_LABELS.get(slot, slot)}."
    return True, message


def unequip_commander_slot(stats: Dict[str, Any], slot: str, items: Dict[str, Dict[str, Any]]) -> Tuple[bool, str]:
    commander_slots = stats.setdefault("Equipped Items", {}).setdefault("Commander", {})
    item_id = commander_slots.get(slot)
    if not item_id:
        return False, f"{LOADOUT_SLOT_LABELS.get(slot, slot)} is already empty."
    commander_slots[slot] = None
    item_name = items.get(item_id, {}).get("name", item_id)
    return True, f"Unequipped {item_name} from {LOADOUT_SLOT_LABELS.get(slot, slot)}."


def commander_slots_for_item(stats: Dict[str, Any], item_id: str) -> List[str]:
    slots = []
    for slot, equipped_id in stats.get("Equipped Items", {}).get("Commander", {}).items():
        if equipped_id == item_id:
            slots.append(slot)
    return slots


def note_action(stats: Dict[str, Any], amount: int = 1) -> None:
    stats["Economy Actions"] = int(stats.get("Economy Actions", 0)) + amount
    items = stats.get("Items", {})
    for item_id, qty in items.items():
        if int(qty) <= 0:
            continue
        meta = _meta(stats, item_id)
        meta["action_age"] = float(meta.get("action_age", 0.0)) + amount


def add_item(stats: Dict[str, Any], item_id: str, qty: int, now: int | None = None) -> None:
    if qty <= 0:
        return
    now = int(now or time.time())
    stats.setdefault("Items", {})
    current_qty = int(stats["Items"].get(item_id, 0))
    stats["Items"][item_id] = current_qty + qty
    meta = _meta(stats, item_id)
    if current_qty <= 0:
        meta["avg_acquired_at"] = float(now)
        meta["action_age"] = 0.0
        meta["use_count"] = 0.0
        meta["reserved_qty"] = 0
    else:
        meta["avg_acquired_at"] = ((float(meta.get("avg_acquired_at", now)) * current_qty) + (now * qty)) / (current_qty + qty)
        meta["action_age"] = (float(meta.get("action_age", 0.0)) * current_qty) / (current_qty + qty)
        meta["use_count"] = (float(meta.get("use_count", 0.0)) * current_qty) / (current_qty + qty)


def remove_item(stats: Dict[str, Any], item_id: str, qty: int) -> bool:
    if qty <= 0 or _owned_qty(stats, item_id) < qty:
        return False
    remaining = _owned_qty(stats, item_id) - qty
    if remaining <= 0:
        stats.get("Items", {}).pop(item_id, None)
        stats.get("Item Meta", {}).pop(item_id, None)
    else:
        stats["Items"][item_id] = remaining
    return True


def sell_ratio(item: Dict[str, Any]) -> float:
    profile = item.get("sell_profile", "gear")
    if profile == "gear":
        return 0.65
    if profile in {"consumable", "material"}:
        return 0.55
    return 0.45


def sale_value(stats: Dict[str, Any], item: Dict[str, Any], items: Dict[str, Dict[str, Any]]) -> int:
    meta = _meta(stats, item["id"])
    market_state = _market_state(stats)
    base = item_market_value(stats, market_state, item)
    ratio = sell_ratio(item)
    hours_owned = max(0.0, (time.time() - float(meta.get("avg_acquired_at", time.time()))) / 3600)
    time_decay = min(0.25, (hours_owned / 6.0) * 0.01)
    action_decay = min(0.20, (float(meta.get("action_age", 0.0)) / 8.0) * 0.01)
    usage_decay = min(0.20, float(meta.get("use_count", 0.0)) * 0.03)
    modifier = max(0.15, 1.0 - time_decay - action_decay - usage_decay)
    mods = economy_modifiers(stats, items)
    bonus = 1.0 + (mods.get("sale_bonus_pct", 0) / 100.0)
    value = int(base * ratio * modifier * bonus)
    return max(int(base * 0.15), value)


def _format_item_line(stats: Dict[str, Any], item: Dict[str, Any], item_lookup: Dict[str, Dict[str, Any]]) -> str:
    rarity_color = RARITY_COLORS.get(item["rarity"], Fore.WHITE)
    element_color = ELEMENT_COLORS.get(item.get("element"), Fore.WHITE)
    available, note = can_view_item(stats, item)
    stock_left, stock_note = available_stock(stats, item, int(time.time()))
    items = item_lookup
    price = int(item["price_gold"])
    mods = economy_modifiers(stats, items)
    discounted_price = int(math.ceil(price * max(0.5, 1 - mods.get("shop_discount_pct", 0) / 100.0)))
    stock_text = stock_note if stock_left is None else f"{stock_left} left"
    if not available:
        stock_text = unlock_reason_text(note)
    affordability = "affordable" if int(stats.get("Gold", 0)) >= discounted_price else f"need {max(0, discounted_price - int(stats.get('Gold', 0)))}"
    owned = _owned_qty(stats, item["id"])
    free_qty = available_inventory_qty(stats, item["id"])
    equipped_marker = "equipped" if equipped_count(stats, item["id"]) else "bag"
    upgrade_text = _slot_upgrade_text(stats, item, items)
    return (
        f"{rarity_color}{item['name']}{Fore.RESET} | "
        f"{element_color}{item.get('element') or 'Arcane'}{Fore.RESET} | "
        f"{item['rarity']} | {discounted_price} Gold | {affordability} | "
        f"Owned {owned}/Free {free_qty} ({equipped_marker}) | {upgrade_text} | {stock_text}"
    )


def _item_summary(item: Dict[str, Any], stats: Dict[str, Any], item_lookup: Dict[str, Dict[str, Any]]) -> List[str]:
    market_state = _market_state(stats)
    _refresh_value_memory(stats, {"items": list(item_lookup.values())}, market_state)
    entry = _value_entry(market_state, item["id"])
    trend_label, trend_color = _trend_meta(entry)
    lines = [
        f"{RARITY_COLORS.get(item['rarity'], Fore.WHITE)}{item['name']}{Fore.RESET} [{item['category']}]",
        f"Target: {item['target']}    Slot: {item.get('slot') or 'n/a'}    Unlock: Shop Lv {item.get('unlock_shop_level', 1)}",
        item["description"],
    ]
    if item.get("branch_requirements"):
        req_text = ", ".join(f"{branch} rank {rank}" for branch, rank in item["branch_requirements"].items())
        lines.append(f"Requires: {req_text}")
    if item.get("stats"):
        stats_text = ", ".join(f"{stat} +{amount}" for stat, amount in item["stats"].items())
        lines.append(f"Stats: {stats_text}")
    if item.get("economy"):
        econ_text = ", ".join(f"{MODIFIER_LABELS.get(key, key)} +{value}" for key, value in item["economy"].items())
        lines.append(f"Economy: {econ_text}")
    if item.get("use_effects"):
        use_text = ", ".join(
            f"{effect['type']} {effect.get('stat', '')} +{effect.get('amount', 0)}".strip()
            for effect in item["use_effects"]
        )
        lines.append(f"Use: {use_text}")
    stat_delta_line, economy_delta_line = _slot_delta_text(stats, item, item_lookup)
    lines.append(stat_delta_line)
    lines.append(economy_delta_line)
    lines.append(
        f"Market Value: {item_market_value(stats, market_state, item)} Gold    Trend: {trend_color}{trend_label}{Fore.RESET}"
    )
    owned = _owned_qty(stats, item["id"])
    free_qty = available_inventory_qty(stats, item["id"])
    reserved_qty = reserved_inventory_qty(stats, item["id"])
    lines.append(
        f"Owned: {owned}    Free: {free_qty}    Reserved: {reserved_qty}    Equipped: {equipped_count(stats, item['id'])}"
    )
    if owned:
        lines.append(f"Estimated sale value: {sale_value(stats, item, item_lookup)} Gold each")
    visible, reason = can_view_item(stats, item)
    if not visible:
        lines.append(f"Progress gate: {unlock_reason_text(reason)}")
    return lines


def _choose_from_list(title: str, lines: List[str], allow_back: bool = True) -> int:
    while True:
        clear()
        prompt_lines = [f"[{index}] {line}" for index, line in enumerate(lines, start=1)]
        if allow_back:
            prompt_lines.append("[0] Back")
        sp(_panel(title, prompt_lines))
        choice = _prompt("Choose an option: ")
        if allow_back and choice == "0":
            return -1
        if choice.isdigit() and 1 <= int(choice) <= len(lines):
            return int(choice) - 1


def _quantity_prompt(max_qty: int, label: str = "Quantity") -> int:
    while True:
        raw = _prompt(f"{label} (1-{max_qty}, 0 cancel): ")
        if raw == "0":
            return 0
        if raw.isdigit() and 1 <= int(raw) <= max_qty:
            return int(raw)


def show_shop(stats: Dict[str, Any], shop_data: Dict[str, Any]) -> None:
    items = item_map(shop_data)
    categories = []
    for category in [
        "Consumables",
        "Weapons",
        "Armor",
        "Accessories",
        "Materials",
        "Shards",
        "Elemental Specials",
    ]:
        visible = [
            item
            for item in _category_items(shop_data, category)
            if can_view_item(stats, item)[0]
        ]
        categories.append(f"{CATEGORY_COLORS.get(category, Fore.WHITE)}{category}{Fore.RESET} ({len(visible)} visible)")

    while True:
        index = _choose_from_list("Arcane Market :: Shop", categories)
        if index < 0:
            return
        category = [
            "Consumables",
            "Weapons",
            "Armor",
            "Accessories",
            "Materials",
            "Shards",
            "Elemental Specials",
        ][index]
        category_items = _category_items(shop_data, category)
        while True:
            lines = [_format_item_line(stats, item, items) for item in category_items]
            item_index = _choose_from_list(f"Shop :: {category}", lines)
            if item_index < 0:
                break
            item = category_items[item_index]
            clear()
            sp(_panel(f"Item :: {item['name']}", _item_summary(item, stats, items), color=CATEGORY_COLORS.get(category, Fore.CYAN)))
            visible, reason = can_view_item(stats, item)
            if not visible:
                sp(f"{Fore.RED}Locked: {unlock_reason_text(reason)}{Fore.RESET}")
                _prompt("\nPress ENTER to continue...")
                continue

            stock_left, _ = available_stock(stats, item, int(time.time()))
            if stock_left == 0:
                sp(f"{Fore.RED}No stock available right now.{Fore.RESET}")
                _prompt("\nPress ENTER to continue...")
                continue
            max_qty = stock_left if stock_left is not None else 99
            qty = _quantity_prompt(max_qty, "Buy quantity")
            if qty == 0:
                continue
            mods = economy_modifiers(stats, items)
            discount = mods.get("shop_discount_pct", 0)
            total = int(math.ceil(item["price_gold"] * qty * max(0.5, 1 - discount / 100.0)))
            if int(stats.get("Gold", 0)) < total:
                sp(f"{Fore.RED}Not enough Gold. Need {total}.{Fore.RESET}")
                _prompt("\nPress ENTER to continue...")
                continue
            stats["Gold"] -= total
            add_item(stats, item["id"], qty)
            stats.setdefault("Shop Purchase History", {}).setdefault(item["id"], []).extend([int(time.time())] * qty)
            note_action(stats)
            purchase_message = record_economy_event(
                stats,
                f"Purchased {qty} x {item['name']} for {total} Gold.",
                max(3, int(math.ceil(total / 60.0))),
            )
            sync_player_data(stats)
            persist_player(stats)
            neon_flicker(f"🛒 {purchase_message}", cycles=2)
            emoji_explosion("💰", count=12)
            _prompt("\nPress ENTER to continue...")


def _list_owned_items(stats: Dict[str, Any], items: Dict[str, Dict[str, Any]], include_locked: bool = True) -> List[Tuple[str, Dict[str, Any]]]:
    owned = []
    for item_id, qty in stats.get("Items", {}).items():
        item = items.get(item_id)
        if not item or int(qty) <= 0:
            continue
        if not include_locked and available_inventory_qty(stats, item_id) <= 0:
            continue
        owned.append((item_id, item))
    def sort_key(pair: Tuple[str, Dict[str, Any]]) -> Tuple[int, int, int, str, str]:
        item_id, item = pair
        favorite = 0 if _meta(stats, item_id).get("favorite") else 1
        equipped = 0 if equipped_count(stats, item_id) else 1
        usable = 0 if item.get("use_effects") else 1
        return (favorite, equipped, usable, item["category"], item["name"])
    owned.sort(key=sort_key)
    return owned


def _apply_use_effect(stats: Dict[str, Any], item: Dict[str, Any], items: Dict[str, Dict[str, Any]]) -> str:
    mods = economy_modifiers(stats, items)
    potency = 1.0 + (mods.get("consumable_power_pct", 0) / 100.0)
    messages = []
    for effect in item.get("use_effects", []):
        amount = int(round(effect.get("amount", 0) * potency))
        if effect["type"] == "grant_buff":
            stats.setdefault("Consumable Buffs", {})
            stats["Consumable Buffs"][effect["stat"]] = int(stats["Consumable Buffs"].get(effect["stat"], 0)) + amount
            messages.append(f"{effect['stat']} +{amount}")
        elif effect["type"] == "grant_skill_points":
            stats["Skill Points"] = int(stats.get("Skill Points", 0)) + amount
            messages.append(f"Skill Points +{amount}")
        elif effect["type"] == "grant_listing_permit_hours":
            expiry = int(time.time()) + amount * 3600
            stats.setdefault("Active Permits", []).append(expiry)
            messages.append(f"listing cap permit for {amount}h")
    return ", ".join(messages) if messages else "Nothing happened."


def inventory_menu(stats: Dict[str, Any], shop_data: Dict[str, Any]) -> None:
    items = item_map(shop_data)
    while True:
        owned = _list_owned_items(stats, items)
        lines = []
        for item_id, item in owned:
            qty = _owned_qty(stats, item_id)
            available = available_inventory_qty(stats, item_id)
            favorite = "★ " if _meta(stats, item_id).get("favorite") else ""
            reserved = reserved_inventory_qty(stats, item_id)
            equipped_slots = commander_slots_for_item(stats, item_id)
            equipped_text = ", ".join(LOADOUT_SLOT_LABELS.get(slot, slot) for slot in equipped_slots) if equipped_slots else "bag"
            lines.append(
                f"{favorite}{item['name']} | Qty {qty} | Free {available} | Reserved {reserved} | "
                f"{item['category']} | {equipped_text}"
            )
        index = _choose_from_list("Inventory", lines or ["No items owned yet."])
        if index < 0:
            return
        if not owned:
            return
        item_id, item = owned[index]
        while True:
            clear()
            summary = _item_summary(item, stats, items)
            summary.append("")
            summary.append("[1] Use item" if item.get("use_effects") else "[1] Use item (unavailable)")
            summary.append("[2] Equip item" if item.get("slot") else "[2] Equip item (unavailable)")
            summary.append("[3] Unequip item" if commander_slots_for_item(stats, item_id) else "[3] Unequip item (unavailable)")
            summary.append("[4] Toggle favorite")
            summary.append("[5] Back")
            sp(_panel(f"Inventory :: {item['name']}", summary, color=CATEGORY_COLORS.get(item["category"], Fore.CYAN)))
            choice = _prompt("Choose: ")
            if choice == "5":
                break
            if choice == "4":
                meta = _meta(stats, item_id)
                meta["favorite"] = not bool(meta.get("favorite"))
                persist_player(stats)
                continue
            if choice == "1":
                if not item.get("use_effects"):
                    continue
                available = available_inventory_qty(stats, item_id)
                if available <= 0:
                    sp(f"{Fore.RED}No usable copies available.{Fore.RESET}")
                    _prompt("\nPress ENTER to continue...")
                    continue
                qty = _quantity_prompt(available)
                if qty == 0:
                    continue
                for _ in range(qty):
                    meta = _meta(stats, item_id)
                    meta["use_count"] = float(meta.get("use_count", 0.0)) + 1
                    remove_item(stats, item_id, 1)
                    message = _apply_use_effect(stats, item, items)
                note_action(stats)
                use_message = record_economy_event(
                    stats,
                    f"Used {qty} x {item['name']}: {message}.",
                    max(1, qty),
                )
                sync_player_data(stats)
                persist_player(stats)
                explosion_print(f"✨ {use_message}", color=Fore.LIGHTGREEN_EX, delay=0.015)
                _prompt("\nPress ENTER to continue...")
                continue
            if choice == "2":
                slot = item.get("slot")
                if not slot:
                    continue
                if item.get("target") not in {"commander", "any"}:
                    sp(f"{Fore.YELLOW}Only commander-ready equipment can be slotted in this milestone. This item stays in storage.{Fore.RESET}")
                    _prompt("\nPress ENTER to continue...")
                    continue
                success, message = equip_commander_item(stats, item_id, items)
                if not success:
                    sp(f"{Fore.RED}{message}{Fore.RESET}")
                    _prompt("\nPress ENTER to continue...")
                    continue
                note_action(stats)
                sync_player_data(stats)
                persist_player(stats)
                sp(f"{Fore.LIGHTGREEN_EX}{message}{Fore.RESET}")
                _prompt("\nPress ENTER to continue...")
                continue
            if choice == "3":
                equipped_slots = commander_slots_for_item(stats, item_id)
                if not equipped_slots:
                    continue
                if len(equipped_slots) == 1:
                    slot = equipped_slots[0]
                else:
                    slot_index = _choose_from_list(
                        "Unequip Which Slot",
                        [LOADOUT_SLOT_LABELS.get(slot_name, slot_name) for slot_name in equipped_slots],
                    )
                    if slot_index < 0:
                        continue
                    slot = equipped_slots[slot_index]
                success, message = unequip_commander_slot(stats, slot, items)
                if not success:
                    sp(f"{Fore.RED}{message}{Fore.RESET}")
                    _prompt("\nPress ENTER to continue...")
                    continue
                note_action(stats)
                sync_player_data(stats)
                persist_player(stats)
                sp(f"{Fore.LIGHTGREEN_EX}{message}{Fore.RESET}")
                _prompt("\nPress ENTER to continue...")


def loadout_menu(stats: Dict[str, Any], shop_data: Dict[str, Any]) -> None:
    items = item_map(shop_data)
    ordered_slots = list(LOADOUT_SLOT_LABELS.keys())
    while True:
        sync_player_data(stats)
        commander_slots = stats.setdefault("Equipped Items", {}).setdefault("Commander", {})
        mods = economy_modifiers(stats, items)
        overview_lines = [
            f"Loadout: {loadout_summary(stats, items)}",
            f"Active Modifiers: {' | '.join(_modifier_lines(mods)[:3])}",
        ]
        slot_options = []
        for slot in ordered_slots:
            item_id = commander_slots.get(slot)
            if item_id:
                item = items.get(item_id, {"name": item_id, "stats": {}, "economy": {}})
                stat_text = _format_delta_map({key: int(value) for key, value in item.get('stats', {}).items()})
                economy_text = _format_delta_map({key: int(value) for key, value in item.get('economy', {}).items()}, MODIFIER_LABELS)
                slot_options.append(
                    f"{LOADOUT_SLOT_LABELS.get(slot, slot)} :: {item['name']} | Stats {stat_text} | Economy {economy_text}"
                )
            else:
                candidates = commander_slot_candidates(stats, items, slot)
                slot_options.append(
                    f"{LOADOUT_SLOT_LABELS.get(slot, slot)} :: empty | {len(candidates)} candidate item(s) ready"
                )
        clear()
        menu_lines = overview_lines + [""] + [
            f"[{index}] {line}"
            for index, line in enumerate(slot_options, start=1)
        ] + ["[0] Back"]
        sp(_panel("Commander Loadout", menu_lines, color=Fore.LIGHTBLUE_EX))
        raw_choice = _prompt("Choose a slot: ")
        if raw_choice == "0":
            return
        if not raw_choice.isdigit() or not 1 <= int(raw_choice) <= len(ordered_slots):
            continue
        index = int(raw_choice) - 1
        slot = ordered_slots[index]
        current = commander_slot_item_data(stats, slot, items)
        slot_lines = [
            f"Slot: {LOADOUT_SLOT_LABELS.get(slot, slot)}",
            f"Current: {current['name'] if current else 'Empty'}",
        ]
        if current:
            slot_lines.append(f"Stats: {_format_delta_map({key: int(value) for key, value in current.get('stats', {}).items()})}")
            slot_lines.append(
                f"Economy: {_format_delta_map({key: int(value) for key, value in current.get('economy', {}).items()}, MODIFIER_LABELS)}"
            )
        candidates = commander_slot_candidates(stats, items, slot)
        slot_lines.append(f"Free candidates: {len(candidates)}")
        slot_lines.extend(["", "[1] Equip from inventory", "[2] Unequip slot", "[0] Back"])
        clear()
        sp(_panel(f"Loadout :: {LOADOUT_SLOT_LABELS.get(slot, slot)}", slot_lines, color=Fore.LIGHTBLUE_EX))
        choice = _prompt("Choose: ")
        if choice == "0":
            continue
        if choice == "1":
            candidate_index = _choose_from_list(
                "Equip to Slot",
                [
                    f"{item['name']} | Free {available_inventory_qty(stats, item_id)} | {_slot_upgrade_text(stats, item, items)}"
                    for item_id, item in candidates
                ] or ["No free matching items."],
            )
            if candidate_index < 0 or not candidates:
                continue
            item_id, _item = candidates[candidate_index]
            success, message = equip_commander_item(stats, item_id, items)
            if success:
                note_action(stats)
                sync_player_data(stats)
                persist_player(stats)
                sp(f"{Fore.LIGHTGREEN_EX}{message}{Fore.RESET}")
            else:
                sp(f"{Fore.RED}{message}{Fore.RESET}")
            _prompt("\nPress ENTER to continue...")
            continue
        if choice == "2":
            success, message = unequip_commander_slot(stats, slot, items)
            if success:
                note_action(stats)
                sync_player_data(stats)
                persist_player(stats)
                sp(f"{Fore.LIGHTGREEN_EX}{message}{Fore.RESET}")
            else:
                sp(f"{Fore.RED}{message}{Fore.RESET}")
            _prompt("\nPress ENTER to continue...")


def sell_menu(stats: Dict[str, Any], shop_data: Dict[str, Any]) -> None:
    items = item_map(shop_data)
    while True:
        sellable = [
            (item_id, item)
            for item_id, item in _list_owned_items(stats, items)
            if available_inventory_qty(stats, item_id) > 0
        ]
        lines = []
        for item_id, item in sellable:
            value = sale_value(stats, item, items)
            lines.append(f"{item['name']} | Qty {available_inventory_qty(stats, item_id)} | {value} Gold each")
        index = _choose_from_list("Sell Inventory", lines or ["Nothing sellable right now."])
        if index < 0:
            return
        if not sellable:
            return
        item_id, item = sellable[index]
        meta = _meta(stats, item_id)
        if meta.get("favorite"):
            sp(f"{Fore.YELLOW}Unfavorite the item before selling it.{Fore.RESET}")
            _prompt("\nPress ENTER to continue...")
            continue
        qty = _quantity_prompt(available_inventory_qty(stats, item_id))
        if qty == 0:
            continue
        gold = sale_value(stats, item, items) * qty
        remove_item(stats, item_id, qty)
        stats["Gold"] = int(stats.get("Gold", 0)) + gold
        note_action(stats)
        sale_message = record_economy_event(
            stats,
            f"Sold {qty} x {item['name']} for {gold} Gold.",
            max(2, int(math.ceil(gold / 90.0))),
        )
        sync_player_data(stats)
        persist_player(stats)
        sp(f"{Fore.LIGHTGREEN_EX}{sale_message}{Fore.RESET}")
        _prompt("\nPress ENTER to continue...")


def specialization_menu(stats: Dict[str, Any], shop_data: Dict[str, Any]) -> None:
    items = item_map(shop_data)
    while True:
        sync_player_data(stats)
        mods = economy_modifiers(stats, items)
        current_total = branch_point_total(int(stats.get("Shop Level", 1)))
        spent = spent_branch_points(stats.get("Economy Tree", {}))
        available_points = current_total - spent
        progress = shop_level_progress(stats)
        next_level = progress["next_level"]
        cost = progress["cost"]
        ready = progress["ready"]
        message = progress["message"]
        lines = [
            f"Shop Level: {stats['Shop Level']}    Reputation: {stats.get('Economy Reputation', 0)}    Gold: {stats['Gold']}",
            f"Economy Points: {available_points} available / {current_total} total",
            f"Next shop level: {next_level} for {cost} Gold and {progress['required_reputation']} Rep -> {message}",
            "",
        ]
        for branch in BRANCH_ORDER:
            rank = int(stats["Economy Tree"].get(branch, 0))
            max_rank = BRANCH_CONFIG[branch]["max_rank"]
            next_reward = "maxed"
            if rank < max_rank:
                next_reward = _format_delta_map(BRANCH_MODIFIERS[branch][rank], MODIFIER_LABELS)
            lines.append(f"[{branch}] Rank {rank}/{max_rank} :: {BRANCH_CONFIG[branch]['theme']} :: Next -> {next_reward}")
        lines.extend(
            [
                "",
                "[1] Upgrade Shop Level",
                "[2] Spend branch points",
                "[3] Respec branch points",
                "[0] Back",
            ]
        )
        clear()
        sp(_panel("Specializations", lines, color=Fore.LIGHTMAGENTA_EX))
        choice = _prompt("Choose: ")
        if choice == "0":
            return
        if choice == "1":
            if not ready:
                sp(f"{Fore.YELLOW}{message}{Fore.RESET}")
                _prompt("\nPress ENTER to continue...")
                continue
            stats["Gold"] -= cost
            stats["Shop Level"] += 1
            note_action(stats)
            upgrade_message = record_economy_event(
                stats,
                f"Shop Level increased to {stats['Shop Level']} for {cost} Gold.",
                4 + int(stats["Shop Level"]),
            )
            reward_messages = apply_shop_level_rewards(stats, stats["Shop Level"], items)
            sync_player_data(stats)
            persist_player(stats)
            sp(f"{Fore.LIGHTGREEN_EX}{upgrade_message}{Fore.RESET}")
            for reward_message in reward_messages:
                sp(f"{Fore.LIGHTYELLOW_EX}{reward_message}{Fore.RESET}")
            _prompt("\nPress ENTER to continue...")
            continue
        if choice == "2":
            if available_points <= 0:
                sp(f"{Fore.YELLOW}No branch points available right now.{Fore.RESET}")
                _prompt("\nPress ENTER to continue...")
                continue
            branch_index = _choose_from_list(
                "Spend Branch Points",
                [
                    f"{branch} :: Rank {stats['Economy Tree'][branch]}/{BRANCH_CONFIG[branch]['max_rank']}"
                    for branch in BRANCH_ORDER
                ],
            )
            if branch_index < 0:
                continue
            branch = BRANCH_ORDER[branch_index]
            if stats["Economy Tree"][branch] >= BRANCH_CONFIG[branch]["max_rank"]:
                sp(f"{Fore.YELLOW}{branch} is already capped.{Fore.RESET}")
                _prompt("\nPress ENTER to continue...")
                continue
            stats["Economy Tree"][branch] += 1
            note_action(stats)
            branch_message = record_economy_event(
                stats,
                f"{branch} advanced to rank {stats['Economy Tree'][branch]}.",
                4,
            )
            sync_player_data(stats)
            persist_player(stats)
            sp(f"{Fore.LIGHTGREEN_EX}{branch_message}{Fore.RESET}")
            _prompt("\nPress ENTER to continue...")
            continue
        if choice == "3":
            resets = int(stats.get("Economy Respec Count", 0))
            respec_cost = 300 + (resets * 180) + (int(stats.get("Shop Level", 1)) * 90)
            if int(stats.get("Gold", 0)) < respec_cost:
                sp(f"{Fore.YELLOW}Need {respec_cost} Gold to respec.{Fore.RESET}")
                _prompt("\nPress ENTER to continue...")
                continue
            confirm = _prompt(f"Spend {respec_cost} Gold to reset all branch points? (y/n): ").lower()
            if confirm != "y":
                continue
            stats["Gold"] -= respec_cost
            stats["Economy Respec Count"] = resets + 1
            stats["Economy Tree"] = {branch: 0 for branch in BRANCH_ORDER}
            note_action(stats)
            respec_message = record_economy_event(
                stats,
                f"Economy specialization reset for {respec_cost} Gold.",
                2,
            )
            sync_player_data(stats)
            persist_player(stats)
            sp(f"{Fore.LIGHTGREEN_EX}{respec_message}{Fore.RESET}")
            _prompt("\nPress ENTER to continue...")


def _rand_qty(item: Dict[str, Any]) -> int:
    if item["category"] in {"Materials", "Consumables"}:
        return random.randint(1, 4)
    if item["category"] == "Shards":
        return random.randint(1, 2)
    return 1


def _trader_focus_score(trader: Dict[str, Any], item: Dict[str, Any], market_state: Dict[str, Any]) -> float:
    focus = 1.0
    if item["category"] in trader.get("focus_categories", []):
        focus += 0.24
    if item.get("element") in trader.get("focus_elements", []):
        focus += 0.20
    entry = _value_entry(market_state, item["id"])
    focus += max(-0.18, min(0.22, (entry.get("demand", 0) - entry.get("supply", 0)) * 0.04))
    return max(0.3, focus)


def _choose_bot_listing_type(trader: Dict[str, Any], item: Dict[str, Any], market_state: Dict[str, Any]) -> str:
    entry = _value_entry(market_state, item["id"])
    demand = int(entry.get("demand", 0))
    supply = int(entry.get("supply", 0))
    styles = {
        "sharp": [("sell", 5), ("buy_order", 2), ("mixed", 3), ("barter", 1)],
        "calm": [("sell", 3), ("buy_order", 3), ("mixed", 2), ("barter", 2)],
        "stubborn": [("sell", 4), ("buy_order", 3), ("mixed", 1), ("barter", 2)],
        "playful": [("sell", 3), ("buy_order", 2), ("mixed", 3), ("barter", 2)],
        "sly": [("sell", 2), ("buy_order", 2), ("mixed", 3), ("barter", 4)],
        "warm": [("sell", 3), ("buy_order", 3), ("mixed", 2), ("barter", 2)],
    }
    weighted = []
    for listing_type, weight in styles.get(trader["style"], styles["calm"]):
        adjusted = weight
        if listing_type == "sell" and demand > supply:
            adjusted += 2
        if listing_type == "buy_order" and supply > demand:
            adjusted += 2
        if listing_type == "barter" and item["category"] in {"Shards", "Materials", "Elemental Specials"}:
            adjusted += 2
        weighted.extend([listing_type] * max(1, adjusted))
    return random.choice(weighted)


def _counter_bundle(
    stats: Dict[str, Any],
    market_state: Dict[str, Any],
    source_item: Dict[str, Any],
    source_qty: int,
    pool: List[Dict[str, Any]],
) -> Tuple[List[Dict[str, int]], int]:
    source_value = item_market_value(stats, market_state, source_item) * source_qty
    candidates = [item for item in pool if item["id"] != source_item["id"]]
    if not candidates:
        return [], max(0, int(source_value * 0.25))
    candidates.sort(
        key=lambda item: (
            abs(item_market_value(stats, market_state, item) - source_value),
            item["name"],
        )
    )
    chosen = random.choice(candidates[: min(4, len(candidates))])
    chosen_value = max(1, item_market_value(stats, market_state, chosen))
    qty = max(1, min(3, round(source_value / chosen_value)))
    gold_delta = source_value - (chosen_value * qty)
    return [{"item_id": chosen["id"], "qty": qty}], max(0, int(gold_delta))


def _make_bot_listing(
    stats: Dict[str, Any],
    item: Dict[str, Any],
    listing_type: str,
    listing_id: int,
    now: int,
    expires_at: int,
    trader: Dict[str, Any],
    market_state: Dict[str, Any],
    visible_items: List[Dict[str, Any]],
) -> Dict[str, Any]:
    qty = _rand_qty(item)
    unit_value = item_market_value(stats, market_state, item)
    greed = float(trader.get("greed", 0.1))
    demand_bias = (int(_value_entry(market_state, item["id"]).get("demand", 0)) - int(_value_entry(market_state, item["id"]).get("supply", 0))) * 0.03
    listing = {
        "id": f"B-{listing_id}",
        "source": "bot",
        "type": listing_type,
        "trader_id": trader["id"],
        "trader_name": trader["name"],
        "trader_title": trader["title"],
        "offer_items": [],
        "ask_items": [],
        "offer_gold": 0,
        "ask_gold": 0,
        "created_at": now,
        "expires_at": expires_at,
        "chat_log": [],
        "negotiation_rounds": 0,
        "quoted_value": unit_value,
        "mood": 0,
    }
    if listing_type == "sell":
        ask_total = int(math.ceil(unit_value * qty * (1.02 + greed + max(-0.08, demand_bias))))
        listing["offer_items"] = [{"item_id": item["id"], "qty": qty}]
        listing["ask_gold"] = max(1, ask_total)
        return listing
    if listing_type == "buy_order":
        bid_ratio = max(0.68, min(1.02, float(trader.get("buy_bias", 0.95)) - max(0.0, demand_bias)))
        offer_total = int(unit_value * qty * bid_ratio)
        listing["ask_items"] = [{"item_id": item["id"], "qty": qty}]
        listing["offer_gold"] = max(1, offer_total)
        return listing
    if listing_type == "barter":
        listing["offer_items"] = [{"item_id": item["id"], "qty": 1}]
        ask_items, ask_gold = _counter_bundle(stats, market_state, item, 1, visible_items)
        listing["ask_items"] = ask_items
        listing["ask_gold"] = max(0, int(ask_gold * (0.40 + greed)))
        return listing

    listing["offer_items"] = [{"item_id": item["id"], "qty": 1}]
    ask_items, ask_gold = _counter_bundle(stats, market_state, item, 1, visible_items)
    listing["ask_items"] = ask_items
    listing["ask_gold"] = max(1, int(ask_gold + (unit_value * (0.10 + greed * 0.5))))
    return listing


def _barter_recipe_for_output(shop_data: Dict[str, Any], item_id: str) -> Dict[str, Any] | None:
    for recipe in shop_data.get("barter_recipes", []):
        if recipe["output_item_id"] == item_id:
            return recipe
    return None


def _listing_text(listing: Dict[str, Any], items: Dict[str, Dict[str, Any]], shop_data: Dict[str, Any]) -> str:
    offer_items = ", ".join(
        f"{items.get(entry['item_id'], {'name': entry['item_id']})['name']} x{entry['qty']}" for entry in listing.get("offer_items", [])
    ) or "No items"
    ask_items = ", ".join(
        f"{items.get(entry['item_id'], {'name': entry['item_id']})['name']} x{entry['qty']}" for entry in listing.get("ask_items", [])
    ) or "No items"
    trader_tag = listing.get("trader_name", "Market Board")
    if listing["type"] == "sell":
        return f"{listing['id']} :: {trader_tag} :: SELL {offer_items} for {listing['ask_gold']} Gold"
    if listing["type"] == "buy_order":
        return f"{listing['id']} :: {trader_tag} :: BUY ORDER wants {ask_items} and pays {listing['offer_gold']} Gold"
    if listing["type"] == "barter":
        extra = f" + {listing['ask_gold']} Gold" if listing.get("ask_gold", 0) else ""
        return f"{listing['id']} :: {trader_tag} :: BARTER gives {offer_items} for {ask_items}{extra}"
    return f"{listing['id']} :: {trader_tag} :: MIXED gives {offer_items} for {ask_items} + {listing['ask_gold']} Gold"


def _generate_bot_board(stats: Dict[str, Any], shop_data: Dict[str, Any], items: Dict[str, Dict[str, Any]], market_state: Dict[str, Any]) -> None:
    current_level = int(stats.get("Shop Level", 1))
    visible_items = [
        item
        for item in shop_data["items"]
        if item.get("market_allowed", False) and can_view_item(stats, item)[0]
    ]
    if not visible_items:
        market_state["bot_listings"] = []
        market_state["bot_refresh_at"] = int(time.time()) + 3600
        return
    trader_book = _ensure_bot_traders(market_state)
    count = random.randint(4, 6) if current_level <= 1 else random.randint(6, 12)
    now = int(time.time())
    next_id = int(market_state.get("next_listing_id", 1))
    listings = []
    for _ in range(count):
        trader = random.choice(list(trader_book.values()))
        weighted_items = []
        for item in visible_items:
            weighted_items.extend([item] * max(1, int(round(_trader_focus_score(trader, item, market_state) * 3))))
        item = random.choice(weighted_items)
        listing_type = _choose_bot_listing_type(trader, item, market_state)
        listing = _make_bot_listing(stats, item, listing_type, next_id, now, now + 3600, trader, market_state, visible_items)
        next_id += 1
        listings.append(listing)
        trader_book[trader["id"]]["last_seen"] = now
    market_state["bot_generated_at"] = now
    market_state["bot_refresh_at"] = now + 3600
    market_state["bot_listings"] = listings
    market_state["next_listing_id"] = next_id


def _resolve_player_listings(stats: Dict[str, Any], shop_data: Dict[str, Any], items: Dict[str, Dict[str, Any]], market_state: Dict[str, Any]) -> None:
    now = int(time.time())
    active = []
    for listing in market_state.get("player_listings", []):
        if now < int(listing.get("expires_at", now)):
            active.append(listing)
            continue

        listing_type = listing["type"]
        offer_value = _bundle_value(stats, market_state, listing.get("offer_items", []), items)
        ask_value = _bundle_value(stats, market_state, listing.get("ask_items", []), items) + int(listing.get("ask_gold", 0))
        offer_gold = int(listing.get("offer_gold", 0))
        if listing_type in {"sell", "buy_order"}:
            qty = int(listing.get("qty", 1))
            if listing_type == "sell":
                item_id = listing["offer_items"][0]["item_id"]
                item = items[item_id]
                market_total = item_market_value(stats, market_state, item) * qty
                ratio = listing["ask_gold"] / max(1, market_total)
                demand_bias = int(_value_entry(market_state, item_id).get("demand", 0)) - int(_value_entry(market_state, item_id).get("supply", 0))
                fill_factor = _clamp(0.9 - max(0.0, ratio - 1.0) * 1.4 + demand_bias * 0.05, 0.05, 0.98)
            else:
                item_id = listing["ask_items"][0]["item_id"]
                item = items[item_id]
                market_total = item_market_value(stats, market_state, item) * qty
                ratio = listing["offer_gold"] / max(1, market_total)
                demand_bias = int(_value_entry(market_state, item_id).get("supply", 0)) - int(_value_entry(market_state, item_id).get("demand", 0))
                fill_factor = _clamp(0.65 + max(0.0, ratio - 0.8) * 0.9 + demand_bias * 0.04, 0.05, 0.98)
            fill = max(0, min(qty, int(round(qty * fill_factor * random.uniform(0.5, 1.0)))))
            if fill > 0:
                if listing_type == "sell":
                    value = int((listing["ask_gold"] / max(1, qty)) * fill)
                    tax_pct = max(0, 8 - economy_modifiers(stats, items).get("market_fee_discount_pct", 0))
                    taxed = max(0, int(value * (1 - tax_pct / 100.0)))
                    stats["Gold"] = int(stats.get("Gold", 0)) + taxed
                    item_id = listing["offer_items"][0]["item_id"]
                    meta = _meta(stats, item_id)
                    meta["reserved_qty"] = max(0, int(meta.get("reserved_qty", 0)) - fill)
                    remove_item(stats, item_id, fill)
                    _shift_market_signal(market_state, item_id, demand_delta=fill, supply_delta=-fill)
                    remaining = qty - fill
                    if remaining > 0:
                        active.append(
                            {
                                **listing,
                                "qty": remaining,
                                "offer_items": [{"item_id": item_id, "qty": remaining}],
                                "ask_gold": int((listing["ask_gold"] / qty) * remaining),
                                "expires_at": now + 3600,
                            }
                        )
                    _record_market_result(
                        stats,
                        market_state,
                        f"{listing['id']} sold {fill} unit(s) for {taxed} Gold after tax.",
                        max(4, int(math.ceil(taxed / 130.0))),
                    )
                else:
                    spent = int((listing["reserved_gold"] / max(1, qty)) * fill)
                    refund = listing["reserved_gold"] - spent
                    add_item(stats, listing["ask_items"][0]["item_id"], fill)
                    _shift_market_signal(market_state, listing["ask_items"][0]["item_id"], demand_delta=-fill, supply_delta=fill)
                    stats["Gold"] = int(stats.get("Gold", 0)) + refund
                    _record_market_result(
                        stats,
                        market_state,
                        f"{listing['id']} filled {fill} unit(s); unused Gold refunded: {refund}.",
                        max(4, int(math.ceil(spent / 140.0))),
                    )
            else:
                if listing_type == "sell":
                    item_id = listing["offer_items"][0]["item_id"]
                    meta = _meta(stats, item_id)
                    meta["reserved_qty"] = max(0, int(meta.get("reserved_qty", 0)) - qty)
                    _record_market_result(stats, market_state, f"{listing['id']} expired with no sale. Reserved items returned.")
                else:
                    stats["Gold"] = int(stats.get("Gold", 0)) + int(listing["reserved_gold"])
                    _record_market_result(stats, market_state, f"{listing['id']} expired with no fill. Reserved Gold refunded.")
            continue

        quality_ratio = offer_value / max(1, ask_value if listing_type != "buy_order" else offer_gold)
        success_roll = _clamp(0.55 + ((quality_ratio - 1.0) * 0.45), 0.08, 0.92)
        if random.random() < success_roll:
            if listing_type == "barter":
                for ask in listing["ask_items"]:
                    add_item(stats, ask["item_id"], ask["qty"])
                    _shift_market_signal(market_state, ask["item_id"], supply_delta=ask["qty"])
                for offer in listing["offer_items"]:
                    meta = _meta(stats, offer["item_id"])
                    meta["reserved_qty"] = max(0, int(meta.get("reserved_qty", 0)) - offer["qty"])
                    remove_item(stats, offer["item_id"], offer["qty"])
                    _shift_market_signal(market_state, offer["item_id"], demand_delta=offer["qty"])
                _record_market_result(stats, market_state, f"{listing['id']} completed as a barter exchange.", 6)
            else:
                for offer in listing["offer_items"]:
                    meta = _meta(stats, offer["item_id"])
                    meta["reserved_qty"] = max(0, int(meta.get("reserved_qty", 0)) - offer["qty"])
                    remove_item(stats, offer["item_id"], offer["qty"])
                    _shift_market_signal(market_state, offer["item_id"], demand_delta=offer["qty"])
                for ask in listing["ask_items"]:
                    add_item(stats, ask["item_id"], ask["qty"])
                    _shift_market_signal(market_state, ask["item_id"], supply_delta=ask["qty"])
                stats["Gold"] = int(stats.get("Gold", 0)) + int(listing.get("ask_gold", 0)) + int(listing.get("reserved_refund_gold", 0))
                _record_market_result(stats, market_state, f"{listing['id']} resolved as a mixed trade.", 7)
        else:
            for offer in listing.get("offer_items", []):
                meta = _meta(stats, offer["item_id"])
                meta["reserved_qty"] = max(0, int(meta.get("reserved_qty", 0)) - offer["qty"])
            stats["Gold"] = int(stats.get("Gold", 0)) + int(listing.get("reserved_gold", 0))
            _record_market_result(stats, market_state, f"{listing['id']} expired and reserves were returned.")
    market_state["player_listings"] = active


def ensure_market(stats: Dict[str, Any], shop_data: Dict[str, Any], items: Dict[str, Dict[str, Any]]) -> None:
    market_state = _market_state(stats)
    _ensure_bot_traders(market_state)
    _refresh_value_memory(stats, shop_data, market_state)
    _resolve_player_listings(stats, shop_data, items, market_state)
    if int(time.time()) >= int(market_state.get("bot_refresh_at", 0)) or not market_state.get("bot_listings"):
        _generate_bot_board(stats, shop_data, items, market_state)


def _can_afford_bundle(stats: Dict[str, Any], ask_items: List[Dict[str, int]], ask_gold: int) -> Tuple[bool, str]:
    if int(stats.get("Gold", 0)) < int(ask_gold):
        return False, "Not enough Gold."
    for ask in ask_items:
        if available_inventory_qty(stats, ask["item_id"]) < int(ask["qty"]):
            return False, f"Need {ask['qty']} x {ask['item_id']}."
    return True, ""


def _trader_for_listing(market_state: Dict[str, Any], listing: Dict[str, Any]) -> Dict[str, Any]:
    trader_book = _ensure_bot_traders(market_state)
    return trader_book.get(listing.get("trader_id"), random.choice(list(trader_book.values())))


def _listing_value_snapshot(stats: Dict[str, Any], market_state: Dict[str, Any], listing: Dict[str, Any], items: Dict[str, Dict[str, Any]]) -> Tuple[int, int]:
    offer_value = _bundle_value(stats, market_state, listing.get("offer_items", []), items)
    ask_value = _bundle_value(stats, market_state, listing.get("ask_items", []), items) + int(listing.get("ask_gold", 0))
    if listing["type"] == "buy_order":
        ask_value = _bundle_value(stats, market_state, listing.get("ask_items", []), items)
        offer_value = int(listing.get("offer_gold", 0))
    return offer_value, ask_value


def _listing_detail_lines(stats: Dict[str, Any], listing: Dict[str, Any], shop_data: Dict[str, Any], items: Dict[str, Dict[str, Any]]) -> List[str]:
    market_state = _market_state(stats)
    trader = _trader_for_listing(market_state, listing)
    offer_value, ask_value = _listing_value_snapshot(stats, market_state, listing, items)
    primary_id = None
    if listing.get("offer_items"):
        primary_id = listing["offer_items"][0]["item_id"]
    elif listing.get("ask_items"):
        primary_id = listing["ask_items"][0]["item_id"]
    trend_text = "steady"
    trend_color = Fore.WHITE
    if primary_id:
        entry = _value_entry(market_state, primary_id)
        trend_text, trend_color = _trend_meta(entry)
    value_gap = offer_value - ask_value
    if listing["type"] == "buy_order":
        value_gap = int(listing.get("offer_gold", 0)) - _bundle_value(stats, market_state, listing.get("ask_items", []), items)
    edge_text = "neutral"
    if value_gap > 0:
        edge_text = f"favours you by {value_gap} Gold"
    elif value_gap < 0:
        edge_text = f"favours trader by {abs(value_gap)} Gold"
    lines = [
        f"Trader: {Fore.LIGHTYELLOW_EX}{trader['name']}{Fore.RESET} [{trader['title']}]    Style: {trader['style']}",
        f"{trader['opener']}",
        f"Market value snapshot -> offer side: {offer_value} Gold    ask side: {ask_value} Gold    trend: {trend_color}{trend_text}{Fore.RESET}",
        f"Value edge: {edge_text}",
        _listing_text(listing, items, shop_data),
    ]
    if listing.get("chat_log"):
        lines.append("")
        lines.append(f"{Fore.LIGHTGREEN_EX}Recent chat:{Fore.RESET}")
        for speaker, message in listing["chat_log"][-4:]:
            lines.append(f"{speaker}: {message}")
    return lines


def _chat_response(stats: Dict[str, Any], listing: Dict[str, Any], message: str, items: Dict[str, Dict[str, Any]]) -> str:
    market_state = _market_state(stats)
    trader = _trader_for_listing(market_state, listing)
    lower = message.lower()
    tokens = set(re.findall(r"[a-z']+", lower))
    primary_item = None
    if listing.get("offer_items"):
        primary_item = items.get(listing["offer_items"][0]["item_id"])
    elif listing.get("ask_items"):
        primary_item = items.get(listing["ask_items"][0]["item_id"])

    if tokens.intersection({"hi", "hello", "hey"}):
        return trader["closer"]
    if tokens.intersection({"why", "price", "value", "worth", "expensive", "cheap", "high", "cost"}):
        if primary_item:
            value = item_market_value(stats, market_state, primary_item)
            entry = _value_entry(market_state, primary_item["id"])
            trend_text, _ = _trend_meta(entry)
            return f"I mark {primary_item['name']} around {value} Gold right now. The market feels {trend_text}, so I will not ignore that."
        return "Price follows demand, stock, and how badly people want the item today."
    if tokens.intersection({"discount", "deal", "bargain", "lower", "raise", "cheaper"}):
        patience_left = max(0, int(trader.get("patience", 3)) - int(listing.get("negotiation_rounds", 0)))
        return f"I still have patience for {patience_left} real offers. Put a number on the table and we can talk."
    if tokens.intersection({"rare", "legendary", "mythic", "relic", "shard"}):
        if primary_item:
            return f"{primary_item['rarity']} stock moves on reputation alone. I watch who wants it, not just what it cost the shop."
        return "High-end goods live or die by scarcity."
    if tokens.intersection({"fire", "water", "earth", "air", "electric", "shadow"}):
        if primary_item and primary_item.get("element"):
            return f"Element matters. {primary_item['element']} pieces swing harder whenever commanders lean that way."
        return "Elemental swings move prices faster than most new traders expect."
    if tokens.intersection({"thanks", "thank", "bye", "later"}):
        return "Keep your purse ready and your numbers cleaner next time."
    return "I heard you. If you want movement, bring me a sharper offer than talk alone."


def _gold_offer_prompt(label: str, ceiling: int) -> int:
    while True:
        raw = _prompt(f"{label} (0-{ceiling}, 0 cancel): ")
        if raw == "0":
            return 0
        if raw.isdigit() and 0 < int(raw) <= ceiling:
            return int(raw)


def _bargain_sell_listing(stats: Dict[str, Any], listing: Dict[str, Any], items: Dict[str, Dict[str, Any]], market_state: Dict[str, Any]) -> Tuple[str, bool]:
    trader = _trader_for_listing(market_state, listing)
    entry = listing["offer_items"][0]
    qty = _quantity_prompt(entry["qty"], "Negotiate for how many")
    if qty == 0:
        return "Cancelled.", False
    item = items[entry["item_id"]]
    unit_quote = listing["ask_gold"] / max(1, entry["qty"])
    market_unit = item_market_value(stats, market_state, item)
    floor_total = int(math.ceil(market_unit * qty * (0.90 + trader["greed"] * 0.40)))
    offer = _gold_offer_prompt("Your offer in Gold", max(1, int(unit_quote * qty * 2)))
    if offer == 0:
        return "Cancelled.", False
    listing["negotiation_rounds"] = int(listing.get("negotiation_rounds", 0)) + 1
    if offer >= floor_total and int(stats.get("Gold", 0)) >= offer:
        stats["Gold"] -= offer
        add_item(stats, entry["item_id"], qty)
        _shift_market_signal(market_state, entry["item_id"], demand_delta=qty, supply_delta=-qty)
        if qty == entry["qty"]:
            return f"{trader['name']} accepts. You bought {qty} x {item['name']} for {offer} Gold.", True
        entry["qty"] -= qty
        listing["ask_gold"] -= int(unit_quote * qty)
        return f"{trader['name']} accepts. You bought {qty} x {item['name']} for {offer} Gold.", False
    counter = max(floor_total, int((offer + floor_total) / 2))
    if int(listing.get("negotiation_rounds", 0)) > trader["patience"]:
        return f"{trader['name']}: Enough. That number wastes both our time.", False
    accept = _prompt(f"{trader['name']} counters at {counter} Gold. Accept? (y/n): ").lower()
    if accept == "y":
        if int(stats.get("Gold", 0)) < counter:
            return "Not enough Gold for the counteroffer.", False
        stats["Gold"] -= counter
        add_item(stats, entry["item_id"], qty)
        _shift_market_signal(market_state, entry["item_id"], demand_delta=qty, supply_delta=-qty)
        if qty == entry["qty"]:
            return f"You accepted {trader['name']}'s counter and bought {item['name']}.", True
        entry["qty"] -= qty
        listing["ask_gold"] -= int(unit_quote * qty)
        return f"You accepted {trader['name']}'s counter and bought {qty} units.", False
    return f"{trader['name']}: Then we hold where we stand.", False


def _bargain_buy_listing(stats: Dict[str, Any], listing: Dict[str, Any], items: Dict[str, Dict[str, Any]], market_state: Dict[str, Any]) -> Tuple[str, bool]:
    trader = _trader_for_listing(market_state, listing)
    ask = listing["ask_items"][0]
    max_qty = min(ask["qty"], available_inventory_qty(stats, ask["item_id"]))
    if max_qty <= 0:
        return "No available copies to negotiate with.", False
    qty = _quantity_prompt(max_qty, "Negotiate for how many")
    if qty == 0:
        return "Cancelled.", False
    item = items[ask["item_id"]]
    market_unit = item_market_value(stats, market_state, item)
    unit_bid = listing["offer_gold"] / max(1, ask["qty"])
    ceiling = int(market_unit * qty * (1.03 - trader["greed"] * 0.10))
    desired = _gold_offer_prompt("Ask payout in Gold", max(1, int(unit_bid * qty * 2)))
    if desired == 0:
        return "Cancelled.", False
    listing["negotiation_rounds"] = int(listing.get("negotiation_rounds", 0)) + 1
    if desired <= ceiling:
        remove_item(stats, ask["item_id"], qty)
        stats["Gold"] = int(stats.get("Gold", 0)) + desired
        _shift_market_signal(market_state, ask["item_id"], demand_delta=-qty, supply_delta=qty)
        if qty == ask["qty"]:
            return f"{trader['name']} agrees. You sold {qty} x {item['name']} for {desired} Gold.", True
        ask["qty"] -= qty
        listing["offer_gold"] -= int(unit_bid * qty)
        return f"{trader['name']} agrees. You sold {qty} x {item['name']} for {desired} Gold.", False
    counter = min(desired, max(int(unit_bid * qty), ceiling))
    if int(listing.get("negotiation_rounds", 0)) > trader["patience"]:
        return f"{trader['name']}: I pay no higher. Keep your stock if you like.", False
    accept = _prompt(f"{trader['name']} counters at {counter} Gold. Accept? (y/n): ").lower()
    if accept == "y":
        remove_item(stats, ask["item_id"], qty)
        stats["Gold"] = int(stats.get("Gold", 0)) + counter
        _shift_market_signal(market_state, ask["item_id"], demand_delta=-qty, supply_delta=qty)
        if qty == ask["qty"]:
            return f"You accepted the counter and sold {item['name']}.", True
        ask["qty"] -= qty
        listing["offer_gold"] -= int(unit_bid * qty)
        return f"You accepted the counter and sold {qty} units.", False
    return f"{trader['name']}: Then we wait for a saner ask.", False


def _bargain_bundle_listing(stats: Dict[str, Any], listing: Dict[str, Any], items: Dict[str, Dict[str, Any]], market_state: Dict[str, Any]) -> Tuple[str, bool]:
    trader = _trader_for_listing(market_state, listing)
    if not listing.get("offer_items"):
        return "This listing cannot be bargained right now.", False
    item = items[listing["offer_items"][0]["item_id"]]
    offer_value, ask_value = _listing_value_snapshot(stats, market_state, listing, items)
    sweetener = _gold_offer_prompt("Extra Gold you will add to your side", max(1, max(ask_value * 2, 2000)))
    if sweetener == 0:
        return "Cancelled.", False
    listing["negotiation_rounds"] = int(listing.get("negotiation_rounds", 0)) + 1
    proposed_value = _bundle_value(stats, market_state, listing.get("ask_items", []), items) + sweetener
    reserve_value = int(offer_value * (0.94 + trader["greed"] * 0.18))
    if proposed_value >= reserve_value:
        can_pay, reason = _can_afford_bundle(stats, listing.get("ask_items", []), sweetener)
        if not can_pay:
            return reason, False
        for ask in listing.get("ask_items", []):
            remove_item(stats, ask["item_id"], ask["qty"])
            _shift_market_signal(market_state, ask["item_id"], supply_delta=ask["qty"])
        stats["Gold"] -= sweetener
        for offer in listing.get("offer_items", []):
            add_item(stats, offer["item_id"], offer["qty"])
            _shift_market_signal(market_state, offer["item_id"], demand_delta=offer["qty"])
        return f"{trader['name']} accepts the sweeter deal. You receive {item['name']}.", True
    counter = max(0, reserve_value - _bundle_value(stats, market_state, listing.get("ask_items", []), items))
    if int(listing.get("negotiation_rounds", 0)) > trader["patience"]:
        return f"{trader['name']}: Add more value or walk away.", False
    accept = _prompt(f"{trader['name']} wants {counter} Gold on top. Accept? (y/n): ").lower()
    if accept == "y":
        can_pay, reason = _can_afford_bundle(stats, listing.get("ask_items", []), counter)
        if not can_pay:
            return reason, False
        for ask in listing.get("ask_items", []):
            remove_item(stats, ask["item_id"], ask["qty"])
            _shift_market_signal(market_state, ask["item_id"], supply_delta=ask["qty"])
        stats["Gold"] -= counter
        for offer in listing.get("offer_items", []):
            add_item(stats, offer["item_id"], offer["qty"])
            _shift_market_signal(market_state, offer["item_id"], demand_delta=offer["qty"])
        return f"You accepted the counter and secured {item['name']}.", True
    return f"{trader['name']}: Then the board keeps its price.", False


def bargain_with_bot(stats: Dict[str, Any], listing: Dict[str, Any], shop_data: Dict[str, Any], items: Dict[str, Dict[str, Any]]) -> Tuple[str, bool]:
    market_state = _market_state(stats)
    if listing["type"] == "sell":
        return _bargain_sell_listing(stats, listing, items, market_state)
    if listing["type"] == "buy_order":
        return _bargain_buy_listing(stats, listing, items, market_state)
    return _bargain_bundle_listing(stats, listing, items, market_state)


def _apply_bot_listing(stats: Dict[str, Any], listing: Dict[str, Any], shop_data: Dict[str, Any], items: Dict[str, Dict[str, Any]]) -> str:
    market_state = _market_state(stats)
    if listing["type"] == "sell":
        entry = listing["offer_items"][0]
        max_qty = entry["qty"]
        qty = _quantity_prompt(max_qty, "Buy how many")
        if qty == 0:
            return "Cancelled."
        unit_price = listing["ask_gold"] / max(1, entry["qty"])
        total_price = int(math.ceil(unit_price * qty))
        if int(stats.get("Gold", 0)) < total_price:
            return "Not enough Gold."
        stats["Gold"] -= total_price
        add_item(stats, entry["item_id"], qty)
        _shift_market_signal(market_state, entry["item_id"], demand_delta=qty, supply_delta=-qty)
        if qty == max_qty:
            return f"Bought {qty} x {items[entry['item_id']]['name']} for {total_price} Gold."
        entry["qty"] -= qty
        listing["ask_gold"] = int(unit_price * entry["qty"])
        return f"Bought {qty} x {items[entry['item_id']]['name']} for {total_price} Gold."

    if listing["type"] == "buy_order":
        ask = listing["ask_items"][0]
        max_qty = min(ask["qty"], available_inventory_qty(stats, ask["item_id"]))
        if max_qty <= 0:
            return "No available copies to sell into this order."
        qty = _quantity_prompt(max_qty, "Sell how many")
        if qty == 0:
            return "Cancelled."
        unit_value = listing["offer_gold"] / max(1, ask["qty"])
        payout = int(unit_value * qty)
        remove_item(stats, ask["item_id"], qty)
        stats["Gold"] = int(stats.get("Gold", 0)) + payout
        _shift_market_signal(market_state, ask["item_id"], demand_delta=-qty, supply_delta=qty)
        if qty == ask["qty"]:
            return f"Filled buy order for {qty} units and earned {payout} Gold."
        ask["qty"] -= qty
        listing["offer_gold"] = int(unit_value * ask["qty"])
        return f"Partially filled buy order for {qty} units and earned {payout} Gold."

    if listing["type"] == "barter":
        can_pay, reason = _can_afford_bundle(stats, listing.get("ask_items", []), int(listing.get("ask_gold", 0)))
        if not can_pay:
            return reason
        for ask in listing.get("ask_items", []):
            remove_item(stats, ask["item_id"], ask["qty"])
            _shift_market_signal(market_state, ask["item_id"], supply_delta=ask["qty"])
        stats["Gold"] -= int(listing.get("ask_gold", 0))
        output = listing["offer_items"][0]
        add_item(stats, output["item_id"], output["qty"])
        _shift_market_signal(market_state, output["item_id"], demand_delta=output["qty"])
        return f"Completed barter and received {items[output['item_id']]['name']}."

    offer = listing["offer_items"][0]
    ask_items = listing.get("ask_items", [])
    ask_gold = int(listing.get("ask_gold", 0))
    can_pay, reason = _can_afford_bundle(stats, ask_items, ask_gold)
    if not can_pay:
        return reason
    for ask in ask_items:
        remove_item(stats, ask["item_id"], ask["qty"])
        _shift_market_signal(market_state, ask["item_id"], supply_delta=ask["qty"])
    stats["Gold"] -= ask_gold
    add_item(stats, offer["item_id"], offer["qty"])
    _shift_market_signal(market_state, offer["item_id"], demand_delta=offer["qty"])
    return f"Completed mixed deal and received {items[offer['item_id']]['name']}."


def _select_owned_item(stats: Dict[str, Any], items: Dict[str, Dict[str, Any]], prompt_title: str, allow_reserved: bool = False) -> Tuple[str, Dict[str, Any]] | None:
    candidates = []
    for item_id, item in _list_owned_items(stats, items):
        free_qty = _owned_qty(stats, item_id) if allow_reserved else available_inventory_qty(stats, item_id)
        if free_qty <= 0:
            continue
        candidates.append((item_id, item))
    index = _choose_from_list(
        prompt_title,
        [f"{item['name']} | Qty {_owned_qty(stats, item_id)} | Free {available_inventory_qty(stats, item_id)}" for item_id, item in candidates] or ["No valid items."],
    )
    if index < 0 or not candidates:
        return None
    return candidates[index]


def listing_posting_fee(stats: Dict[str, Any], items: Dict[str, Dict[str, Any]]) -> int:
    fee_base = 40
    fee_discount = economy_modifiers(stats, items).get("market_fee_discount_pct", 0)
    return max(5, int(fee_base * (1 - fee_discount / 100.0)))


def _bundle_label(bundle: List[Dict[str, int]], items: Dict[str, Dict[str, Any]]) -> str:
    if not bundle:
        return "none"
    return ", ".join(
        f"{entry['qty']} x {items.get(entry['item_id'], {'name': entry['item_id']})['name']}"
        for entry in bundle
    )


def build_listing_preview(
    stats: Dict[str, Any],
    listing_type: str,
    duration_label: str,
    offer_items: List[Dict[str, int]],
    ask_items: List[Dict[str, int]],
    ask_gold: int,
    offer_gold: int,
    items: Dict[str, Dict[str, Any]],
) -> List[str]:
    market_state = _market_state(stats)
    fee = listing_posting_fee(stats, items)
    offer_value = _bundle_value(stats, market_state, offer_items, items) + int(offer_gold)
    ask_value = _bundle_value(stats, market_state, ask_items, items) + int(ask_gold)
    if listing_type == "buy_order":
        offer_value = int(offer_gold)
        ask_value = _bundle_value(stats, market_state, ask_items, items)
    edge = offer_value - ask_value
    if edge > 0:
        edge_text = f"You are overpaying the current snapshot by about {edge} Gold."
    elif edge < 0:
        edge_text = f"Your ask sits about {abs(edge)} Gold above current market value."
    else:
        edge_text = "This listing is close to the current market snapshot."
    return [
        f"Type: {listing_type.replace('_', ' ').title()}    Duration: {duration_label}    Posting fee: {fee} Gold",
        f"Offer: {_bundle_label(offer_items, items)}{' + ' + str(offer_gold) + ' Gold' if offer_gold else ''}",
        f"Ask: {_bundle_label(ask_items, items)}{' + ' + str(ask_gold) + ' Gold' if ask_gold else ''}",
        f"Market snapshot -> your side: {offer_value} Gold    other side: {ask_value} Gold",
        edge_text,
    ]


def _create_player_listing(stats: Dict[str, Any], shop_data: Dict[str, Any], items: Dict[str, Dict[str, Any]]) -> str:
    market_state = _market_state(stats)
    current_active = len(market_state.get("player_listings", []))
    cap = listing_cap(stats, items)
    if current_active >= cap:
        return f"Listing cap reached ({current_active}/{cap}). Use permits or upgrade Logistics/Exchange."
    posting_fee = listing_posting_fee(stats, items)
    if int(stats.get("Gold", 0)) < posting_fee:
        return f"Need {posting_fee} Gold for the listing fee."
    choice = _choose_from_list(
        "Create Listing",
        [
            "Sell listing",
            "Buy order",
            "Barter listing",
            "Mixed deal",
        ],
    )
    if choice < 0:
        return "Cancelled."
    duration_index = _choose_from_list("Choose Duration", [label for label, _seconds in PRESET_DURATIONS])
    if duration_index < 0:
        return "Cancelled."
    duration_label, duration_seconds = PRESET_DURATIONS[duration_index]
    next_id = int(market_state.get("next_listing_id", 1))
    now = int(time.time())
    listing_payload: Dict[str, Any] | None = None
    preview_lines: List[str] = []

    if choice == 0:
        selection = _select_owned_item(stats, items, "Choose item to sell")
        if not selection:
            return "Cancelled."
        item_id, item = selection
        free_qty = available_inventory_qty(stats, item_id)
        qty = _quantity_prompt(free_qty)
        if qty == 0:
            return "Cancelled."
        ask_gold = int(math.ceil(item_market_value(stats, market_state, item) * qty * 1.06))
        offer_items = [{"item_id": item_id, "qty": qty}]
        preview_lines = build_listing_preview(stats, "sell", duration_label, offer_items, [], ask_gold, 0, items)
        listing_payload = {
            "id": f"P-{next_id}",
            "source": "player",
            "type": "sell",
            "offer_items": offer_items,
            "ask_items": [],
            "ask_gold": ask_gold,
            "offer_gold": 0,
            "qty": qty,
            "created_at": now,
            "expires_at": now + duration_seconds,
        }
    elif choice == 1:
        selection = _choose_from_list("Choose wanted item", [item["name"] for item in shop_data["items"]])
        if selection < 0:
            return "Cancelled."
        wanted = shop_data["items"][selection]
        qty = _quantity_prompt(5)
        if qty == 0:
            return "Cancelled."
        offer_gold = int(math.ceil(item_market_value(stats, market_state, wanted) * qty * 0.94))
        if int(stats.get("Gold", 0)) < offer_gold + posting_fee:
            return f"Need {offer_gold + posting_fee} Gold to reserve this buy order."
        ask_items = [{"item_id": wanted["id"], "qty": qty}]
        preview_lines = build_listing_preview(stats, "buy_order", duration_label, [], ask_items, 0, offer_gold, items)
        listing_payload = {
            "id": f"P-{next_id}",
            "source": "player",
            "type": "buy_order",
            "offer_items": [],
            "ask_items": ask_items,
            "ask_gold": 0,
            "offer_gold": offer_gold,
            "qty": qty,
            "reserved_gold": offer_gold,
            "created_at": now,
            "expires_at": now + duration_seconds,
        }
    elif choice == 2:
        offer = _select_owned_item(stats, items, "Choose offered item")
        if not offer:
            return "Cancelled."
        offer_item_id, offer_item = offer
        offer_qty = _quantity_prompt(available_inventory_qty(stats, offer_item_id))
        if offer_qty == 0:
            return "Cancelled."
        ask_index = _choose_from_list("Choose requested item", [item["name"] for item in shop_data["items"]])
        if ask_index < 0:
            return "Cancelled."
        ask_item = shop_data["items"][ask_index]
        ask_qty = _quantity_prompt(3)
        if ask_qty == 0:
            return "Cancelled."
        offer_items = [{"item_id": offer_item_id, "qty": offer_qty}]
        ask_items = [{"item_id": ask_item["id"], "qty": ask_qty}]
        preview_lines = build_listing_preview(stats, "barter", duration_label, offer_items, ask_items, 0, 0, items)
        listing_payload = {
            "id": f"P-{next_id}",
            "source": "player",
            "type": "barter",
            "offer_items": offer_items,
            "ask_items": ask_items,
            "ask_gold": 0,
            "offer_gold": 0,
            "created_at": now,
            "expires_at": now + duration_seconds,
        }
    else:
        offer = _select_owned_item(stats, items, "Choose offered item")
        if not offer:
            return "Cancelled."
        offer_item_id, offer_item = offer
        offer_qty = _quantity_prompt(available_inventory_qty(stats, offer_item_id))
        if offer_qty == 0:
            return "Cancelled."
        ask_index = _choose_from_list("Choose requested bonus item", [item["name"] for item in shop_data["items"]])
        if ask_index < 0:
            return "Cancelled."
        ask_item = shop_data["items"][ask_index]
        ask_qty = _quantity_prompt(2)
        if ask_qty == 0:
            return "Cancelled."
        offer_value = item_market_value(stats, market_state, offer_item) * offer_qty
        ask_value = item_market_value(stats, market_state, ask_item) * ask_qty
        extra_gold = max(0, int(math.ceil(max(0, offer_value - ask_value) * 0.35)))
        offer_items = [{"item_id": offer_item_id, "qty": offer_qty}]
        ask_items = [{"item_id": ask_item["id"], "qty": ask_qty}]
        preview_lines = build_listing_preview(stats, "mixed", duration_label, offer_items, ask_items, extra_gold, 0, items)
        listing_payload = {
            "id": f"P-{next_id}",
            "source": "player",
            "type": "mixed",
            "offer_items": offer_items,
            "ask_items": ask_items,
            "ask_gold": extra_gold,
            "offer_gold": 0,
            "created_at": now,
            "expires_at": now + duration_seconds,
        }

    if not listing_payload:
        return "Cancelled."

    clear()
    sp(_panel("Listing Preview", preview_lines + ["", "Confirm this listing? (y/n)"], color=Fore.LIGHTYELLOW_EX))
    confirm = _prompt("Confirm: ").lower()
    if confirm != "y":
        return "Cancelled."

    if listing_payload["type"] in {"sell", "barter", "mixed"}:
        for offer in listing_payload.get("offer_items", []):
            meta = _meta(stats, offer["item_id"])
            meta["reserved_qty"] = int(meta.get("reserved_qty", 0)) + int(offer["qty"])
    if listing_payload["type"] == "buy_order":
        stats["Gold"] -= int(listing_payload.get("reserved_gold", 0))

    stats["Gold"] -= posting_fee
    market_state["player_listings"].append(listing_payload)
    market_state["next_listing_id"] = next_id + 1
    note_action(stats)
    return record_economy_event(
        stats,
        f"Listing {listing_payload['id']} posted for {duration_label}. Fee paid: {posting_fee} Gold.",
        5,
    )


def trading_hall(stats: Dict[str, Any], shop_data: Dict[str, Any]) -> None:
    items = item_map(shop_data)
    while True:
        ensure_market(stats, shop_data, items)
        persist_player(stats)
        market_state = stats["Market State"]
        clear()
        lines = [
            f"Gold: {stats['Gold']}    Reputation: {stats.get('Economy Reputation', 0)}    Active listings: {len(market_state['player_listings'])}/{listing_cap(stats, items)}",
            f"Bot refresh at: {time.strftime('%H:%M:%S', time.localtime(market_state['bot_refresh_at']))}    Posting fee right now: {listing_posting_fee(stats, items)} Gold",
        ]
        if market_state.get("resolved_messages"):
            lines.append(f"{Fore.LIGHTGREEN_EX}Resolved since last visit:{Fore.RESET}")
            for message in market_state["resolved_messages"][:5]:
                lines.append(f"- {message}")
            market_state["resolved_messages"] = []
        lines.extend(
            [
                "",
                "[1] View bot board",
                "[2] View my listings",
                "[3] Create listing",
                "[4] Refresh status",
                "[0] Back",
            ]
        )
        sp(_panel("Trading Hall", lines, color=Fore.LIGHTYELLOW_EX))
        choice = _prompt("Choose: ")
        if choice == "0":
            persist_player(stats)
            return
        if choice == "1":
            while True:
                bot_lines = [_listing_text(listing, items, shop_data) for listing in market_state["bot_listings"]]
                index = _choose_from_list("Bot Board", bot_lines or ["No bot listings."])
                if index < 0 or not market_state["bot_listings"]:
                    break
                listing = market_state["bot_listings"][index]
                while True:
                    clear()
                    detail_lines = _listing_detail_lines(stats, listing, shop_data, items)
                    detail_lines.extend(
                        [
                            "",
                            "[1] Accept trade",
                            "[2] Chat",
                            "[3] Bargain",
                            "[0] Back",
                        ]
                    )
                    sp(_panel("Bot Listing", detail_lines, color=Fore.YELLOW))
                    action = _prompt("Choose: ")
                    if action == "0":
                        break
                    if action == "1":
                        offer_value, ask_value = _listing_value_snapshot(stats, market_state, listing, items)
                        message = _apply_bot_listing(stats, listing, shop_data, items)
                        if listing["type"] in {"sell", "buy_order"}:
                            if listing["offer_items"] and listing["offer_items"][0]["qty"] <= 0:
                                market_state["bot_listings"].pop(index)
                                removed = True
                            elif listing["ask_items"] and listing["ask_items"][0]["qty"] <= 0:
                                market_state["bot_listings"].pop(index)
                                removed = True
                            else:
                                removed = False
                        else:
                            market_state["bot_listings"].pop(index)
                            removed = True
                        if not any(message.startswith(prefix) for prefix in ["Cancelled", "Not enough", "Need ", "No available"]):
                            message = record_economy_event(
                                stats,
                                message,
                                max(4, int(math.ceil(max(offer_value, ask_value, 1) / 120.0))),
                            )
                        note_action(stats)
                        sync_player_data(stats)
                        persist_player(stats)
                        sp(f"{Fore.LIGHTGREEN_EX}{message}{Fore.RESET}")
                        _prompt("\nPress ENTER to continue...")
                        if removed:
                            break
                    elif action == "2":
                        said = _prompt("Say something to the trader (blank to cancel): ")
                        if not said:
                            continue
                        response = _chat_response(stats, listing, said, items)
                        listing.setdefault("chat_log", []).append(("You", said))
                        listing.setdefault("chat_log", []).append((listing.get("trader_name", "Trader"), response))
                        note_action(stats)
                        sync_player_data(stats)
                        persist_player(stats)
                    elif action == "3":
                        message, remove_listing = bargain_with_bot(stats, listing, shop_data, items)
                        if remove_listing or "accept" in message.lower():
                            offer_value, ask_value = _listing_value_snapshot(stats, market_state, listing, items)
                            message = record_economy_event(
                                stats,
                                message,
                                max(4, int(math.ceil(max(offer_value, ask_value, 1) / 140.0))),
                            )
                        note_action(stats)
                        sync_player_data(stats)
                        persist_player(stats)
                        sp(f"{Fore.LIGHTGREEN_EX}{message}{Fore.RESET}")
                        _prompt("\nPress ENTER to continue...")
                        if remove_listing:
                            market_state["bot_listings"].pop(index)
                            break
        elif choice == "2":
            while True:
                my_lines = [_listing_text(listing, items, shop_data) for listing in market_state["player_listings"]]
                index = _choose_from_list("My Listings", my_lines or ["No active player listings."])
                if index < 0 or not market_state["player_listings"]:
                    break
                listing = market_state["player_listings"][index]
                clear()
                sp(_panel("Player Listing", [_listing_text(listing, items, shop_data)], color=Fore.MAGENTA))
                confirm = _prompt("Cancel this listing? (y/n): ").lower()
                if confirm != "y":
                    continue
                for offer in listing.get("offer_items", []):
                    meta = _meta(stats, offer["item_id"])
                    meta["reserved_qty"] = max(0, int(meta.get("reserved_qty", 0)) - offer["qty"])
                if listing["type"] == "buy_order":
                    stats["Gold"] = int(stats.get("Gold", 0)) + int(listing.get("reserved_gold", 0))
                market_state["player_listings"].pop(index)
                note_action(stats)
                cancel_message = record_economy_event(stats, "Listing cancelled and reserves returned where applicable.")
                sync_player_data(stats)
                persist_player(stats)
                sp(f"{Fore.LIGHTGREEN_EX}{cancel_message}{Fore.RESET}")
                _prompt("\nPress ENTER to continue...")
        elif choice == "3":
            message = _create_player_listing(stats, shop_data, items)
            sync_player_data(stats)
            persist_player(stats)
            sp(f"{Fore.LIGHTGREEN_EX}{message}{Fore.RESET}")
            _prompt("\nPress ENTER to continue...")
        elif choice == "4":
            ensure_market(stats, shop_data, items)
            persist_player(stats)


def _ledger_entry_text(entry: Dict[str, Any]) -> str:
    timestamp = int(entry.get("at", 0))
    message = entry.get("message", "")
    if timestamp <= 0:
        return message
    return f"[{time.strftime('%H:%M', time.localtime(timestamp))}] {message}"


def ledger_menu(stats: Dict[str, Any]) -> None:
    entries = list(reversed(stats.get("Economy Ledger", [])))
    lines = [_ledger_entry_text(entry) for entry in entries] or ["No economy history recorded yet."]
    clear()
    sp(_panel("Economy Ledger", lines[:LEDGER_LIMIT], color=Fore.LIGHTYELLOW_EX))
    _prompt("Press ENTER to go back: ")


def economy_overview_lines(stats: Dict[str, Any], shop_data: Dict[str, Any]) -> List[str]:
    items = item_map(shop_data)
    mods = economy_modifiers(stats, items)
    active_listings = len(stats.get("Market State", {}).get("player_listings", []))
    progress = shop_level_progress(stats)
    lines = [
        f"Commander: {stats['Account Name']} ({stats['Commander']})    Gold: {stats['Gold']}    Reputation: {stats.get('Economy Reputation', 0)}    Skill Points: {stats['Skill Points']}",
        f"Loadout: {loadout_summary(stats, items)}",
        f"Shop Level: {stats['Shop Level']}    Next: Lv {progress['next_level']} for {progress['cost']} Gold and {progress['required_reputation']} Rep",
        f"Economy Points: {branch_point_total(stats['Shop Level']) - spent_branch_points(stats['Economy Tree'])} available    Listing Cap: {listing_cap(stats, items)}    Posting Fee: {listing_posting_fee(stats, items)} Gold",
        f"Active Listings: {active_listings}    Active Permits: {len(stats.get('Active Permits', []))}    Economy Actions: {stats['Economy Actions']}",
        f"Modifiers: {' | '.join(_modifier_lines(mods)[:4])}",
        "",
        "Recent Activity:",
    ]
    recent_entries = list(reversed(stats.get("Economy Ledger", [])))[:3]
    if recent_entries:
        lines.extend(_ledger_entry_text(entry) for entry in recent_entries)
    else:
        lines.append("No economy activity yet. Visit the shop or trading hall to get moving.")
    return lines


def run_economy_hub(stats: Dict[str, Any]) -> None:
    shop_data = load_shop_data()
    sync_player_data(stats)
    persist_player(stats)

    # Entry animation
    crazy_transition(effect="random", duration=0.6)

    while True:
        clear()
        lines = economy_overview_lines(stats, shop_data)
        lines.extend(
            [
                "",
                "[1] Shop",
                "[2] Trading Hall",
                "[3] Inventory",
                "[4] Loadout",
                "[5] Ledger",
                "[6] Sell",
                "[7] Specializations",
                "[0] Exit Economy",
            ]
        )
        sp(_title("ARCANE HEROES :: ECONOMY HUB", Fore.LIGHTCYAN_EX))
        sp(_panel("Economy Hub", lines, color=Fore.CYAN))
        choice = _prompt("Choose: ")
        if choice == "0":
            persist_player(stats)
            return
        if choice == "1":
            show_shop(stats, shop_data)
        elif choice == "2":
            trading_hall(stats, shop_data)
        elif choice == "3":
            inventory_menu(stats, shop_data)
        elif choice == "4":
            loadout_menu(stats, shop_data)
        elif choice == "5":
            ledger_menu(stats)
        elif choice == "6":
            sell_menu(stats, shop_data)
        elif choice == "7":
            specialization_menu(stats, shop_data)
