import unittest

try:
    from app import app
except ModuleNotFoundError:
    app = None


@unittest.skipIf(app is None, "Flask is not installed in this environment")
class AppRouteTests(unittest.TestCase):
    def setUp(self) -> None:
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_index_embeds_initial_state_and_script(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        page = response.get_data(as_text=True)
        self.assertIn("window.BEAHERO_INITIAL_STATE", page)
        self.assertIn("static/app.js", page)

    def test_api_action_updates_state_without_redirect(self) -> None:
        self.client.get("/")
        response = self.client.post("/api/action", json={"action": "move:path"})

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["room"]["name"], "Old Path")
        self.assertIn("move:forest", {item["key"] for item in payload["actions"]})
        self.assertIn('class="map-marker-x"', payload["map_html"])

    def test_api_restart_resets_progress(self) -> None:
        self.client.get("/")
        self.client.post("/api/action", json={"action": "move:path"})
        response = self.client.post("/api/restart")

        payload = response.get_json()
        self.assertEqual(payload["room"]["name"], "Dark Hut")
        self.assertEqual(payload["stats"][0]["value"], "1")

    def test_api_lang_switches_response_language_without_reload(self) -> None:
        self.client.get("/")
        response = self.client.post("/api/lang", json={"lang": "zh"})

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["ui"]["lang"], "zh")
        self.assertEqual(payload["room"]["name"], "黑屋")
        self.assertEqual(payload["actions"][0]["label"], "添火")

    def test_api_action_rejects_missing_action_payload(self) -> None:
        self.client.get("/")

        json_response = self.client.post("/api/action", json={})
        form_response = self.client.post("/api/action", data={})

        self.assertEqual(json_response.status_code, 400)
        self.assertEqual(form_response.status_code, 400)

    def test_api_action_unknown_action_is_a_no_op(self) -> None:
        self.client.get("/")
        before = self.client.get("/api/state").get_json()

        response = self.client.post("/api/action", json={"action": "unknown:action"})

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["won"], before["won"])
        self.assertEqual(payload["stats"], before["stats"])
        self.assertEqual(payload["room"], before["room"])

    def test_api_lang_defaults_to_english_when_missing(self) -> None:
        self.client.get("/")

        response = self.client.post("/api/lang", json={})

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload["ui"]["lang"], "en")
        self.assertEqual(payload["room"]["name"], "Dark Hut")


if __name__ == "__main__":
    unittest.main()
