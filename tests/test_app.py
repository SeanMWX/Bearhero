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

    def test_api_restart_resets_progress(self) -> None:
        self.client.get("/")
        self.client.post("/api/action", json={"action": "move:path"})
        response = self.client.post("/api/restart")

        payload = response.get_json()
        self.assertEqual(payload["room"]["name"], "Dark Hut")
        self.assertEqual(payload["stats"][0]["value"], "1")


if __name__ == "__main__":
    unittest.main()
