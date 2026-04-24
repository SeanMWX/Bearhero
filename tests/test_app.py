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

    def test_index_renders_core_sections(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        page = response.get_data(as_text=True)
        self.assertIn("Beahero", page)
        self.assertIn("Actions", page)
        self.assertIn("Map", page)

    def test_action_route_updates_session_state(self) -> None:
        self.client.get("/")
        response = self.client.post("/action", data={"action": "move:path"}, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        page = response.get_data(as_text=True)
        self.assertIn("A narrow path cut into dead grass", page)

    def test_restart_route_resets_progress(self) -> None:
        self.client.get("/")
        self.client.post("/action", data={"action": "move:path"}, follow_redirects=True)
        response = self.client.post("/restart", follow_redirects=True)

        page = response.get_data(as_text=True)
        self.assertIn("A dark hut with a weak ember", page)


if __name__ == "__main__":
    unittest.main()
