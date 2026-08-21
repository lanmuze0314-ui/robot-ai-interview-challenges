from __future__ import annotations

import copy
from dataclasses import asdict, dataclass
from typing import Optional

from .models import Effect, Event


@dataclass
class _State:
    current_person_id: Optional[str] = None
    present: bool = False
    greeted: bool = False
    left_at: Optional[float] = None
    departure_confirmed: bool = False
    departure_blocked_by_suppression: bool = False
    conversation_depth: int = 0
    meeting_depth: int = 0


class RobotApplication:
    def __init__(self, absence_timeout_s: float = 10.0):
        self.absence_timeout_s = absence_timeout_s
        self._state = _State()

    def handle_event(self, event: Event) -> list[Effect]:
        handlers = {
            "PERSON_ENTERED": self._handle_person_entered,
            "PERSON_LEFT": self._handle_person_left,
            "CONVERSATION_STARTED": self._handle_conversation_started,
            "CONVERSATION_ENDED": self._handle_conversation_ended,
            "MEETING_STARTED": self._handle_meeting_started,
            "MEETING_ENDED": self._handle_meeting_ended,
            "TICK": self._handle_tick,
        }
        handler = handlers.get(event.event_type)
        if handler is None:
            return []
        return handler(event)

    def snapshot(self):
        return copy.deepcopy(asdict(self._state))

    @property
    def _suppressed(self) -> bool:
        return self._state.conversation_depth > 0 or self._state.meeting_depth > 0

    def _handle_person_entered(self, event: Event) -> list[Effect]:
        if self._state.present:
            return []

        if self._state.left_at is not None and not self._state.departure_confirmed:
            self._state.present = True
            self._state.current_person_id = event.person_id
            self._state.left_at = None
            self._state.departure_blocked_by_suppression = False
            return []

        self._state.current_person_id = event.person_id
        self._state.present = True
        self._state.greeted = True
        self._state.left_at = None
        self._state.departure_confirmed = False
        self._state.departure_blocked_by_suppression = False

        if self._suppressed:
            return []

        return [
            Effect(
                effect_type="ROBOT_ACTION",
                value="wave_hand",
                reason="person entered while idle",
            ),
            Effect(
                effect_type="SPEECH",
                value="欢迎光临",
                reason="person entered while idle",
            ),
        ]

    def _handle_person_left(self, event: Event) -> list[Effect]:
        if not self._state.present:
            return []

        self._state.present = False
        self._state.left_at = event.timestamp
        self._state.departure_confirmed = False
        self._state.departure_blocked_by_suppression = False
        return []

    def _handle_conversation_started(self, event: Event) -> list[Effect]:
        self._state.conversation_depth += 1
        return []

    def _handle_conversation_ended(self, event: Event) -> list[Effect]:
        was_suppressed = self._suppressed
        if self._state.conversation_depth > 0:
            self._state.conversation_depth -= 1
        self._lock_expired_departure_after_suppression(event.timestamp, was_suppressed)
        return []

    def _handle_meeting_started(self, event: Event) -> list[Effect]:
        self._state.meeting_depth += 1
        return []

    def _handle_meeting_ended(self, event: Event) -> list[Effect]:
        was_suppressed = self._suppressed
        if self._state.meeting_depth > 0:
            self._state.meeting_depth -= 1
        self._lock_expired_departure_after_suppression(event.timestamp, was_suppressed)
        return []

    def _handle_tick(self, event: Event) -> list[Effect]:
        if self._state.left_at is None or self._state.departure_confirmed:
            return []

        elapsed = event.timestamp - self._state.left_at
        if elapsed < self.absence_timeout_s:
            return []

        if self._suppressed:
            self._state.departure_blocked_by_suppression = True
            return []

        if self._state.departure_blocked_by_suppression:
            return []

        self._state.departure_confirmed = True
        self._state.left_at = None
        return [
            Effect(
                effect_type="ROBOT_ACTION",
                value="send_off",
                reason="absence timeout elapsed",
            )
        ]

    def _lock_expired_departure_after_suppression(self, timestamp: float, was_suppressed: bool) -> None:
        if self._state.left_at is None or self._state.departure_confirmed:
            return

        if was_suppressed and not self._suppressed and timestamp - self._state.left_at >= self.absence_timeout_s:
            self._state.departure_blocked_by_suppression = True
