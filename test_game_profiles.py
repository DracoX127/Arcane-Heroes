import unittest

from game_functions import build_player_stats, sync_player_data
from hero_data import get_hero_record


class TestGameProfiles(unittest.TestCase):
    def test_new_player_stats_include_hero_hub_fields(self) -> None:
        stats = build_player_stats("Nova", "Pyronis")

        self.assertEqual(stats["Account Name"], "Nova")
        self.assertIn("Heroes", stats)
        self.assertEqual(len(stats["Heroes"]), 5)
        self.assertIn("Hero Codex", stats)
        starter_elements = {get_hero_record(hero_id)["element"] for hero_id in stats["Heroes"]}
        self.assertEqual(len(starter_elements), 4)
        self.assertIn("Mailbox", stats)
        self.assertGreaterEqual(len(stats["Mailbox"]), 2)
        self.assertEqual(stats["AI Bot"]["name"], "ASTRA")
        self.assertIn("Battle Record", stats)

    def test_sync_player_data_migrates_legacy_profile(self) -> None:
        legacy = {
            "Account Name": "Legacy",
            "Commander": "Aquaryn",
            "Lvl": 1,
            "Exp": 0,
            "Gold": 1000,
            "Skill Tree": {},
        }

        changed = sync_player_data(legacy)

        self.assertTrue(changed)
        self.assertIn("Heroes", legacy)
        self.assertEqual(len(legacy["Heroes"]), 5)
        self.assertIn("Hero Codex", legacy)
        starter_elements = {get_hero_record(hero_id)["element"] for hero_id in legacy["Heroes"]}
        self.assertEqual(len(starter_elements), 4)
        self.assertIn("Mailbox", legacy)
        self.assertEqual(legacy["AI Bot"]["status"], "Online")
        self.assertIn("Battle Record", legacy)
        owned_states = {hero_id for hero_id, entry in legacy["Hero Codex"].items() if entry.get("state") == "owned"}
        self.assertGreaterEqual(len(owned_states), 5)


if __name__ == "__main__":
    unittest.main()
