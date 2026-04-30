import unittest
from collections import Counter

from hero_data import (
    ENCOUNTERED_CATALOG_STATE,
    HERO_ELEMENTS,
    HERO_RARITIES,
    OWNED_CATALOG_STATE,
    RARITY_COUNTS,
    build_default_codex,
    build_visible_rows,
    derive_power,
    element_bonus,
    filter_rows,
    load_hero_catalog,
    merge_owned_hero,
    sort_rows,
    validate_hero_catalog,
)


class TestHeroData(unittest.TestCase):
    def test_catalog_counts_and_schema(self) -> None:
        catalog = load_hero_catalog()
        self.assertEqual(len(catalog), 144)
        self.assertEqual(validate_hero_catalog(catalog), [])

        element_counts = Counter(hero["element"] for hero in catalog)
        rarity_counts = Counter(hero["rarity"] for hero in catalog)

        for element in HERO_ELEMENTS:
            self.assertEqual(element_counts[element], 24)
        for rarity in HERO_RARITIES:
            self.assertEqual(rarity_counts[rarity], RARITY_COUNTS[rarity])

    def test_power_and_element_bonus_are_deterministic(self) -> None:
        hero = load_hero_catalog()[0]
        first = derive_power(hero)
        second = derive_power(hero)
        self.assertEqual(first, second)
        self.assertGreater(first, 0)

        self.assertEqual(element_bonus("Fire", "Earth"), 20)
        self.assertEqual(element_bonus("Fire", "Electric"), 10)
        self.assertEqual(element_bonus("Fire", "Air"), -20)
        self.assertEqual(element_bonus("Fire", "Shadow"), -10)

    def test_visible_rows_filter_and_sort(self) -> None:
        codex = build_default_codex()
        codex["fire_01"]["state"] = OWNED_CATALOG_STATE
        codex["fire_02"]["state"] = ENCOUNTERED_CATALOG_STATE
        codex["fire_01"]["favorite"] = True
        owned = {"fire_01": {"id": "fire_01", "level": 1, "rank": 1, "soul_stones": 0}}

        rows = build_visible_rows(codex, owned)
        filtered = filter_rows(rows, element="Fire", ownership="owned", favorites_only=True)
        sorted_rows = sort_rows(filtered, mode="default")

        self.assertEqual(len(sorted_rows), 1)
        self.assertEqual(sorted_rows[0]["id"], "fire_01")
        self.assertEqual(sorted_rows[0]["state"], OWNED_CATALOG_STATE)

    def test_merge_owned_hero_adds_progression(self) -> None:
        merged = merge_owned_hero("fire_01", {"id": "fire_01", "level": 3, "rank": 2, "soul_stones": 14})
        self.assertEqual(merged["level"], 3)
        self.assertEqual(merged["rank"], 2)
        self.assertEqual(merged["soul_stones"], 14)
        self.assertGreater(merged["power"], 0)


if __name__ == "__main__":
    unittest.main()
