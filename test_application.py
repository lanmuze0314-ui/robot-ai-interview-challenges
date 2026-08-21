import unittest

from robot_application.application import RobotApplication
from robot_application.models import Event


class RobotApplicationTests(unittest.TestCase):
    def test_first_entry_greets_and_repeated_entry_is_ignored(self):
        app = RobotApplication()

        effects = app.handle_event(Event("PERSON_ENTERED", 0.0, "p1"))
        self.assertEqual([effect.value for effect in effects], ["wave_hand", "欢迎光临"])

        repeated = app.handle_event(Event("PERSON_ENTERED", 1.0, "p1"))
        self.assertEqual(repeated, [])

    def test_conversation_suppresses_actions_and_does_not_backfill(self):
        app = RobotApplication()

        self.assertTrue(app.handle_event(Event("PERSON_ENTERED", 0.0, "p1")))
        self.assertEqual(app.handle_event(Event("CONVERSATION_STARTED", 1.0)), [])
        self.assertEqual(app.handle_event(Event("PERSON_LEFT", 2.0, "p1")), [])

        self.assertEqual(app.handle_event(Event("TICK", 12.0)), [])

        self.assertEqual(app.handle_event(Event("CONVERSATION_ENDED", 13.0)), [])
        self.assertEqual(app.handle_event(Event("TICK", 14.0)), [])

    def test_meeting_suppresses_actions_and_does_not_backfill(self):
        app = RobotApplication()

        self.assertTrue(app.handle_event(Event("PERSON_ENTERED", 0.0, "p1")))
        self.assertEqual(app.handle_event(Event("MEETING_STARTED", 1.0)), [])
        self.assertEqual(app.handle_event(Event("PERSON_LEFT", 2.0, "p1")), [])

        self.assertEqual(app.handle_event(Event("TICK", 12.0)), [])

        self.assertEqual(app.handle_event(Event("MEETING_ENDED", 13.0)), [])
        self.assertEqual(app.handle_event(Event("TICK", 14.0)), [])

    def test_departure_after_timeout_only_emits_once(self):
        app = RobotApplication()

        self.assertTrue(app.handle_event(Event("PERSON_ENTERED", 0.0, "p1")))
        self.assertEqual(app.handle_event(Event("PERSON_LEFT", 5.0, "p1")), [])

        self.assertEqual(app.handle_event(Event("TICK", 14.0)), [])

        effects = app.handle_event(Event("TICK", 15.0))
        self.assertEqual([effect.value for effect in effects], ["send_off"])

        self.assertEqual(app.handle_event(Event("TICK", 16.0)), [])

    def test_brief_leave_and_return_stays_same_session(self):
        app = RobotApplication()

        self.assertTrue(app.handle_event(Event("PERSON_ENTERED", 0.0, "p1")))
        self.assertEqual(app.handle_event(Event("PERSON_LEFT", 5.0, "p1")), [])
        self.assertEqual(app.handle_event(Event("PERSON_ENTERED", 8.0, "p1")), [])

        self.assertEqual(app.handle_event(Event("PERSON_LEFT", 20.0, "p1")), [])
        self.assertEqual(app.handle_event(Event("TICK", 29.0)), [])

        effects = app.handle_event(Event("TICK", 30.0))
        self.assertEqual([effect.value for effect in effects], ["send_off"])

    def test_confirmed_departure_allows_new_entry_to_be_treated_as_new_session(self):
        app = RobotApplication()

        self.assertTrue(app.handle_event(Event("PERSON_ENTERED", 0.0, "p1")))
        self.assertEqual(app.handle_event(Event("PERSON_LEFT", 5.0, "p1")), [])
        self.assertEqual([effect.value for effect in app.handle_event(Event("TICK", 15.0))], ["send_off"])

        effects = app.handle_event(Event("PERSON_ENTERED", 20.0, "p1"))
        self.assertEqual([effect.value for effect in effects], ["wave_hand", "欢迎光临"])

    def test_snapshot_isolated_from_external_mutation(self):
        app = RobotApplication()
        app.handle_event(Event("PERSON_ENTERED", 0.0, "p1"))

        snapshot = app.snapshot()
        snapshot["present"] = False
        snapshot["current_person_id"] = "changed"

        fresh_snapshot = app.snapshot()
        self.assertTrue(fresh_snapshot["present"])
        self.assertEqual(fresh_snapshot["current_person_id"], "p1")


if __name__ == "__main__":
    unittest.main()
