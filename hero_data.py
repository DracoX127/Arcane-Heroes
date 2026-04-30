from __future__ import annotations

import json
from functools import lru_cache
from typing import Any, Dict, Iterable, List

from config import COMMANDER_ELEMENT_NAMES, HEROES_FILE


HERO_ELEMENTS = ["Fire", "Water", "Earth", "Air", "Electric", "Shadow"]
HERO_RARITIES = [
    "Common",
    "Uncommon",
    "Rare",
    "Elite",
    "Epic",
    "Mythic",
    "Legendary",
    "Ancient",
    "Celestial",
    "Divine",
    "Eternal",
]
HERO_STYLE_TAGS = ["Burst", "Tanky", "Healer", "Control", "Fast", "Summoner", "Support", "DoT"]
TARGET_TYPES = ["self", "single_enemy", "all_enemies", "single_ally", "all_allies"]
EFFECT_TYPES = ["damage", "heal", "shield", "buff", "debuff", "stun", "dot", "cleanse", "summon"]
STATUS_VOCAB = [
    "Burn",
    "Poison",
    "Freeze",
    "Stun",
    "Silence",
    "Slow",
    "Weaken",
    "Armor Break",
    "Regen",
    "Shield",
]
RARITY_COUNTS = {rarity: 13 for rarity in HERO_RARITIES}
RARITY_COUNTS["Legendary"] = 14
RARITY_RANK = {rarity: index for index, rarity in enumerate(HERO_RARITIES)}
ELEMENT_WHEEL = ["Fire", "Earth", "Electric", "Water", "Shadow", "Air"]
ELEMENT_INDEX = {element: index for index, element in enumerate(ELEMENT_WHEEL)}
DEFAULT_CATALOG_STATE = "unknown"
ENCOUNTERED_CATALOG_STATE = "encountered"
OWNED_CATALOG_STATE = "owned"

SKILL_COUNT_BY_RARITY = {
    "Common": 1,
    "Uncommon": 1,
    "Rare": 1,
    "Elite": 2,
    "Epic": 2,
    "Mythic": 2,
    "Legendary": 2,
    "Ancient": 3,
    "Celestial": 3,
    "Divine": 3,
    "Eternal": 3,
}

STARTER_HERO_IDS = {
    "Pyronis": ["fire_01", "fire_07", "earth_02", "air_03", "electric_04"],
    "Aquaryn": ["water_01", "water_07", "shadow_02", "air_04", "earth_03"],
    "Terradon": ["earth_01", "earth_07", "fire_03", "air_02", "water_04"],
    "Zephyros": ["air_01", "air_07", "fire_04", "electric_03", "shadow_05"],
    "Voltaris": ["electric_01", "electric_07", "fire_02", "earth_04", "shadow_03"],
    "Noctyra": ["shadow_01", "shadow_07", "water_03", "air_05", "electric_02"],
}


@lru_cache(maxsize=1)
def load_hero_catalog() -> List[Dict[str, Any]]:
    heroes = _read_catalog_file()
    errors = validate_hero_catalog(heroes)
    if errors:
        raise ValueError("Invalid hero catalog:\n" + "\n".join(errors))
    return heroes


@lru_cache(maxsize=1)
def hero_lookup() -> Dict[str, Dict[str, Any]]:
    return {hero["id"]: hero for hero in load_hero_catalog()}


def expected_skill_count(rarity: str) -> int:
    return SKILL_COUNT_BY_RARITY[rarity]


def rarity_sort_value(rarity: str) -> int:
    return RARITY_RANK.get(rarity, -1)


def derive_power(hero: Dict[str, Any]) -> int:
    stats = hero.get("base_stats", {})
    hp = float(stats.get("hp", 0))
    atk = float(stats.get("atk", 0))
    defense = float(stats.get("def", 0))
    spd = float(stats.get("spd", 0))
    crit = float(stats.get("crit", 0))
    acc = float(stats.get("acc", 0))
    resist = float(stats.get("resist", 0))

    stat_score = (
        (hp * 0.18)
        + (atk * 4.6)
        + (defense * 3.4)
        + (spd * 5.2)
        + (crit * 2.8)
        + (acc * 2.6)
        + (resist * 2.4)
    )
    synergy = (
        (atk * crit * 0.012)
        + (spd * acc * 0.018)
        + (defense * resist * 0.014)
        + ((hp / 10.0) * resist * 0.01)
    )
    skill_score = sum(_skill_score(skill) for skill in hero.get("skills", []))
    return int(round(stat_score + synergy + skill_score))


def _skill_score(skill: Dict[str, Any]) -> float:
    effect_weight = {
        "damage": 1.00,
        "heal": 0.93,
        "shield": 0.90,
        "buff": 0.84,
        "debuff": 0.86,
        "stun": 0.96,
        "dot": 0.90,
        "cleanse": 0.76,
        "summon": 1.08,
    }
    target_weight = {
        "self": 0.74,
        "single_enemy": 1.00,
        "all_enemies": 1.46,
        "single_ally": 0.92,
        "all_allies": 1.28,
    }
    base = float(skill.get("power_value", 0))
    cooldown = max(0, int(skill.get("cooldown", 0)))
    status_chance = float(skill.get("status_chance", 0))
    duration = float(skill.get("duration", 0))
    hit_count = float(skill.get("hit_count", 1))
    weight = effect_weight.get(skill.get("effect_type"), 0.8)
    target = target_weight.get(skill.get("target_type"), 1.0)
    score = (base * weight * target) + (status_chance * 0.48) + (duration * 6.0) + (hit_count * 4.0)
    if skill.get("status_name") in {"Stun", "Freeze", "Silence"}:
        score += 8.0
    if skill.get("effect_type") == "summon":
        score += 14.0
    if skill.get("self_condition"):
        score += 6.0
    if skill.get("self_cost"):
        score -= 5.0
    if cooldown > 0:
        score /= 1.0 + (0.18 * max(0, cooldown - 1))
    return score


def element_bonus(attacker_element: str | None, defender_element: str | None) -> int:
    if attacker_element not in ELEMENT_INDEX or defender_element not in ELEMENT_INDEX:
        return 0
    diff = (ELEMENT_INDEX[defender_element] - ELEMENT_INDEX[attacker_element]) % len(ELEMENT_WHEEL)
    if diff == 1:
        return 20
    if diff == 2:
        return 10
    if diff == 5:
        return -20
    if diff == 4:
        return -10
    return 0


def starter_hero_ids(commander: str) -> List[str]:
    return list(STARTER_HERO_IDS.get(commander, STARTER_HERO_IDS["Pyronis"]))


def build_default_codex() -> Dict[str, Dict[str, Any]]:
    return {
        hero["id"]: {
            "state": DEFAULT_CATALOG_STATE,
            "favorite": False,
            "encountered_at": 0,
        }
        for hero in load_hero_catalog()
    }


def normalize_owned_hero(hero_id: str, payload: Any) -> Dict[str, Any]:
    if not isinstance(payload, dict):
        return {"id": hero_id, "level": 1, "rank": 1, "soul_stones": 0}

    level = payload.get("level", payload.get("Level", payload.get("lvl", 1)))
    rank = payload.get("rank", payload.get("Rank", 1))
    soul_stones = payload.get("soul_stones", payload.get("Soul Stones", 0))
    normalized = {
        "id": hero_id,
        "level": max(1, int(level)),
        "rank": max(1, int(rank)),
        "soul_stones": max(0, int(soul_stones)),
    }
    if payload.get("name"):
        normalized["legacy_name"] = str(payload["name"])
    if payload.get("title"):
        normalized["legacy_title"] = str(payload["title"])
    return normalized


def fallback_hero_record(hero_id: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    payload = payload or {}
    return {
        "id": hero_id,
        "name": payload.get("legacy_name", str(hero_id).replace("_", " ").title()),
        "title": payload.get("legacy_title", "Recovered Legacy Recruit"),
        "element": "Arcane",
        "rarity": "Rare",
        "style_tags": ["Support"],
        "lore": "A legacy hero preserved from an older save format.",
        "base_stats": {
            "hp": 148,
            "atk": 28,
            "def": 14,
            "spd": 14,
            "crit": 7,
            "acc": 8,
            "resist": 8,
        },
        "skills": [
            {
                "name": "Legacy Strike",
                "description": "A restored combat technique from an older roster archive.",
                "cooldown": 2,
                "target_type": "single_enemy",
                "effect_type": "damage",
                "power_value": 96,
                "status_chance": 0,
                "duration": 0,
                "hit_count": 1,
            }
        ],
    }


def get_hero_record(hero_id: str, payload: Dict[str, Any] | None = None) -> Dict[str, Any]:
    return hero_lookup().get(hero_id, fallback_hero_record(hero_id, payload))


def merge_owned_hero(hero_id: str, owned_payload: Dict[str, Any]) -> Dict[str, Any]:
    master = dict(get_hero_record(hero_id, owned_payload))
    merged = {
        **master,
        "level": int(owned_payload.get("level", 1)),
        "rank": int(owned_payload.get("rank", 1)),
        "soul_stones": int(owned_payload.get("soul_stones", 0)),
    }
    merged["power"] = display_power(merged)
    return merged


def display_power(hero: Dict[str, Any]) -> int:
    base_power = derive_power(hero)
    return base_power + (max(1, int(hero.get("level", 1))) - 1) * 12 + (max(1, int(hero.get("rank", 1))) - 1) * 35


def build_visible_rows(
    codex: Dict[str, Dict[str, Any]],
    owned_heroes: Dict[str, Dict[str, Any]],
    *,
    include_legacy_owned: bool = True,
) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    known_ids = set(hero_lookup().keys())
    for hero in load_hero_catalog():
        hero_id = hero["id"]
        codex_entry = codex.get(hero_id, {"state": DEFAULT_CATALOG_STATE, "favorite": False})
        state = codex_entry.get("state", DEFAULT_CATALOG_STATE)
        owned_payload = owned_heroes.get(hero_id)
        if owned_payload:
            state = OWNED_CATALOG_STATE
        row = dict(hero)
        row["state"] = state
        row["favorite"] = bool(codex_entry.get("favorite", False))
        row["power"] = derive_power(hero)
        if owned_payload:
            row.update(normalize_owned_hero(hero_id, owned_payload))
            row["power"] = display_power(row)
        rows.append(row)

    if include_legacy_owned:
        for hero_id, owned_payload in owned_heroes.items():
            if hero_id in known_ids:
                continue
            merged = merge_owned_hero(hero_id, normalize_owned_hero(hero_id, owned_payload))
            merged["state"] = OWNED_CATALOG_STATE
            merged["favorite"] = bool(codex.get(hero_id, {}).get("favorite", False))
            rows.append(merged)
    return rows


def filter_rows(
    rows: Iterable[Dict[str, Any]],
    *,
    element: str | None = None,
    rarity: str | None = None,
    style_tag: str | None = None,
    ownership: str = "all",
    search: str = "",
    favorites_only: bool = False,
) -> List[Dict[str, Any]]:
    filtered = []
    needle = search.strip().lower()
    for row in rows:
        state = row.get("state", DEFAULT_CATALOG_STATE)
        owned = state == OWNED_CATALOG_STATE
        if element and row.get("element") != element:
            continue
        if rarity and row.get("rarity") != rarity:
            continue
        if style_tag and style_tag not in row.get("style_tags", []):
            continue
        if ownership == "owned" and not owned:
            continue
        if ownership == "unowned" and owned:
            continue
        if favorites_only and not row.get("favorite"):
            continue
        if needle and needle not in row.get("name", "").lower():
            continue
        filtered.append(row)
    return filtered


def sort_rows(rows: Iterable[Dict[str, Any]], mode: str = "default") -> List[Dict[str, Any]]:
    rows = list(rows)
    if mode == "power":
        rows.sort(key=lambda row: (-int(row.get("power", 0)), row.get("name", "")))
    elif mode == "name":
        rows.sort(key=lambda row: (row.get("name", ""), -int(row.get("power", 0))))
    elif mode == "rarity":
        rows.sort(key=lambda row: (-rarity_sort_value(row.get("rarity", "")), row.get("element", ""), -int(row.get("power", 0))))
    else:
        rows.sort(
            key=lambda row: (
                HERO_ELEMENTS.index(row.get("element", HERO_ELEMENTS[0])) if row.get("element") in HERO_ELEMENTS else 999,
                -rarity_sort_value(row.get("rarity", "")),
                -int(row.get("power", 0)),
                row.get("name", ""),
            )
        )
    return rows


def validate_hero_catalog(catalog: Iterable[Dict[str, Any]] | None = None) -> List[str]:
    heroes = list(_read_catalog_file() if catalog is None else catalog)
    errors: List[str] = []
    ids = [hero.get("id") for hero in heroes]
    if len(heroes) != 144:
        errors.append(f"Expected 144 heroes, found {len(heroes)}.")
    if len(set(ids)) != len(ids):
        errors.append("Hero ids must be unique.")

    element_counts = {element: 0 for element in HERO_ELEMENTS}
    rarity_counts = {rarity: 0 for rarity in HERO_RARITIES}

    for hero in heroes:
        hero_id = hero.get("id", "<missing>")
        for field in ["id", "name", "title", "element", "rarity", "style_tags", "lore", "base_stats", "skills"]:
            if field not in hero:
                errors.append(f"{hero_id} missing field {field}.")
        element = hero.get("element")
        rarity = hero.get("rarity")
        if element not in HERO_ELEMENTS:
            errors.append(f"{hero_id} has invalid element {element}.")
        else:
            element_counts[element] += 1
        if rarity not in HERO_RARITIES:
            errors.append(f"{hero_id} has invalid rarity {rarity}.")
        else:
            rarity_counts[rarity] += 1

        tags = hero.get("style_tags", [])
        if not isinstance(tags, list) or not tags:
            errors.append(f"{hero_id} must have at least one style tag.")
        else:
            for tag in tags:
                if tag not in HERO_STYLE_TAGS:
                    errors.append(f"{hero_id} uses invalid style tag {tag}.")

        stats = hero.get("base_stats", {})
        for stat_field in ["hp", "atk", "def", "spd", "crit", "acc", "resist"]:
            if stat_field not in stats:
                errors.append(f"{hero_id} missing base stat {stat_field}.")

        skills = hero.get("skills", [])
        expected = expected_skill_count(rarity) if rarity in HERO_RARITIES else None
        if expected is not None and len(skills) != expected:
            errors.append(f"{hero_id} should have {expected} skills for {rarity}, found {len(skills)}.")
        for skill in skills:
            for field in [
                "name",
                "description",
                "cooldown",
                "target_type",
                "effect_type",
                "power_value",
                "status_chance",
                "duration",
                "hit_count",
            ]:
                if field not in skill:
                    errors.append(f"{hero_id} skill {skill.get('name', '<unnamed>')} missing {field}.")
            if skill.get("target_type") not in TARGET_TYPES:
                errors.append(f"{hero_id} skill {skill.get('name', '<unnamed>')} has invalid target_type.")
            if skill.get("effect_type") not in EFFECT_TYPES:
                errors.append(f"{hero_id} skill {skill.get('name', '<unnamed>')} has invalid effect_type.")
            if skill.get("status_name") and skill["status_name"] not in STATUS_VOCAB:
                errors.append(f"{hero_id} skill {skill.get('name', '<unnamed>')} has invalid status_name.")

    for element, count in element_counts.items():
        if count != 24:
            errors.append(f"{element} should have 24 heroes, found {count}.")
    for rarity, expected in RARITY_COUNTS.items():
        actual = rarity_counts.get(rarity, 0)
        if actual != expected:
            errors.append(f"{rarity} should have {expected} heroes, found {actual}.")
    return errors


def commander_focus_element(commander: str) -> str:
    return COMMANDER_ELEMENT_NAMES.get(commander, "Fire")


def _read_catalog_file() -> List[Dict[str, Any]]:
    with open(HEROES_FILE, "r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload.get("heroes", [])
