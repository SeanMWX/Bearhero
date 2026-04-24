import unittest
import random

from game import apply_action, available_actions, enemy_name, new_game_state, present_log, render_map_html


class GameStateTests(unittest.TestCase):
    def test_new_game_has_expected_baseline(self) -> None:
        state = new_game_state()

        self.assertEqual(state["location"], "hut")
        self.assertEqual(state["health"], 10)
        self.assertFalse(state["flags"]["game_over"])
        self.assertIn("move:path", {item["key"] for item in available_actions(state)})

    def test_movement_unlocks_room_visit(self) -> None:
        state = new_game_state()

        apply_action(state, "move:path")

        self.assertEqual(state["location"], "path")
        self.assertIn("path", state["visited"])

    def test_gate_requires_stronger_fire(self) -> None:
        state = new_game_state()
        state["location"] = "forest"
        state["fire"] = 1
        initial_log = list(state["log"])

        apply_action(state, "move:gate")

        self.assertNotIn("move:gate", {item["key"] for item in available_actions(state)})
        self.assertEqual(state["location"], "forest")
        self.assertEqual(state["log"], initial_log)

    def test_beast_encounter_can_be_won(self) -> None:
        state = new_game_state()
        apply_action(state, "move:path")
        apply_action(state, "investigate_path")

        self.assertIsNotNone(state["encounter"])
        apply_action(state, "attack")
        apply_action(state, "attack")
        apply_action(state, "attack")

        self.assertIsNone(state["encounter"])
        self.assertGreaterEqual(state["scrap"], 1)

    def test_herb_use_recovers_health_during_fight(self) -> None:
        state = new_game_state()
        state["location"] = "forest"
        state["health"] = 5
        state["herbs"] = 1
        apply_action(state, "hunt_noise")

        apply_action(state, "use_herb")

        self.assertEqual(state["herbs"], 0)
        self.assertGreaterEqual(state["health"], 6)

    def test_open_gate_starts_warden_encounter(self) -> None:
        state = new_game_state()
        state["location"] = "gate"
        state["scrap"] = 2

        apply_action(state, "open_gate")

        self.assertIsNotNone(state["encounter"])
        self.assertEqual(enemy_name(state["encounter"], "en"), "Gate Warden")
        self.assertEqual(state["scrap"], 0)

    def test_player_can_die_in_combat(self) -> None:
        state = new_game_state()
        state["location"] = "forest"
        state["health"] = 2
        apply_action(state, "hunt_noise")

        apply_action(state, "brace")
        apply_action(state, "attack")

        self.assertTrue(state["flags"]["game_over"])
        self.assertEqual(available_actions(state)[0]["key"], "restart")

    def test_crafting_spear_improves_attack_damage(self) -> None:
        state = new_game_state()
        state["scrap"] = 2

        apply_action(state, "craft_spear")
        self.assertTrue(state["gear"]["spear"])

        state["location"] = "forest"
        apply_action(state, "hunt_noise")
        apply_action(state, "attack")

        self.assertEqual(state["encounter"]["hp"], 2)

    def test_crafting_torch_consumes_resources(self) -> None:
        state = new_game_state()
        state["scrap"] = 1
        state["wood"] = 2

        apply_action(state, "craft_torch")

        self.assertTrue(state["gear"]["torch"])
        self.assertEqual(state["scrap"], 0)
        self.assertEqual(state["wood"], 1)

    def test_restart_action_returns_fresh_state(self) -> None:
        state = new_game_state()
        state["health"] = 1
        state["flags"]["game_over"] = True

        restarted = apply_action(state, "restart")

        self.assertEqual(restarted["location"], "hut")
        self.assertEqual(restarted["health"], 10)
        self.assertFalse(restarted["flags"]["game_over"])

    def test_actions_and_logs_can_be_localized_to_chinese(self) -> None:
        state = new_game_state()
        apply_action(state, "move:path")

        action_labels = {item["label"] for item in available_actions(state, "zh")}
        log_lines = present_log(state, "zh")

        self.assertIn("前往林缘", action_labels)
        self.assertTrue(any("旧径" in line for line in log_lines))

    def test_invalid_action_cannot_bypass_resource_or_progress_rules(self) -> None:
        state = new_game_state()

        apply_action(state, "craft_spear")
        apply_action(state, "open_gate")
        apply_action(state, "claim_banner")

        self.assertEqual(state["scrap"], 0)
        self.assertFalse(state["gear"]["spear"])
        self.assertIsNone(state["encounter"])
        self.assertFalse(state["flags"]["won"])

    def test_map_html_is_localized_with_language(self) -> None:
        state = new_game_state()

        english_map = render_map_html(state, "en")
        chinese_map = render_map_html(state, "zh")

        self.assertIn("Forest", english_map)
        self.assertIn("林缘", chinese_map)
        self.assertNotIn("Forest", chinese_map)

    def test_randomized_available_actions_preserve_core_invariants(self) -> None:
        random.seed(0)

        for _ in range(100):
            state = new_game_state()
            for _ in range(25):
                action = random.choice(available_actions(state))["key"]
                apply_action(state, action)

                self.assertGreaterEqual(state["fire"], 0)
                self.assertGreaterEqual(state["wood"], 0)
                self.assertGreaterEqual(state["scrap"], 0)
                self.assertGreaterEqual(state["herbs"], 0)
                self.assertGreaterEqual(state["health"], 0)

                if state["flags"]["won"]:
                    self.assertEqual(state["location"], "ruin")

                if state["flags"]["gate_open"]:
                    self.assertIn("gate", state["visited"])


if __name__ == "__main__":
    unittest.main()
