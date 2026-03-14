import types
from datetime import datetime

import pytest

import main
from api_handler import Message, MessageRow, MessageColumn


class FixedDatetime(datetime):
    @classmethod
    def now(cls, tz=None):  # type: ignore[override]
        return cls(2024, 1, 1, 9, 0, 0, tzinfo=tz)


class NightDatetime(datetime):
    @classmethod
    def now(cls, tz=None):  # type: ignore[override]
        return cls(2024, 1, 1, 2, 0, 0, tzinfo=tz)


def make_message(name: str, status_text: str, device_text: str) -> Message:
    status_row = MessageRow(Columns2=MessageColumn(Cells=[status_text], Type=11))
    device_row = MessageRow(Columns2=MessageColumn(Cells=[device_text], Type=12))
    return Message(
        Name=name,
        Title="Title",
        Description=[],
        Rows=[status_row, device_row],
        Collapsed=False,
    )


def test_are_working_hours_respects_config(monkeypatch):
    # Simulate 09:00 Helsinki (inside default working hours 8-24)
    monkeypatch.setattr(main, "datetime", FixedDatetime)
    assert main.are_working_hours() is True

    # Simulate 02:00 Helsinki (outside working hours)
    monkeypatch.setattr(main, "datetime", NightDatetime)
    assert main.are_working_hours() is False


def test_build_notifications_from_messages():
    single = make_message(
        "test",
        status_text="Færdig",
        device_text="Vaskemaskine 1, Street 123 Pesula er færdig",
    )

    multiple = make_message(
        "test-multi",
        status_text="Færdig",
        device_text="Tørretumbler 4 & 6, Street 123 Pesula er færdig",
    )

    notifications = main.build_notifications([single, multiple])

    assert "Done: Washing machine 1" in notifications
    assert "Done: Dryers 4 & 6" in notifications


def test_get_new_messages_filters_seen_messages(monkeypatch):
    class DummyApi:
        def __init__(self, messages):
            self._messages = messages

        def get_messages(self):
            return self._messages

    messages = [make_message("m1", "Færdig", "Vaskemaskine 1, foo")]

    fake_db: dict = {}
    monkeypatch.setattr(main, "db", fake_db)

    api = DummyApi(messages)

    first_call = main.get_new_messages(api)
    second_call = main.get_new_messages(api)

    assert len(first_call) == 1
    assert len(second_call) == 0


def test_run_iteration_backoff_behavior(monkeypatch):
    # Start with no new messages to trigger backoff
    def fake_get_new_messages(api):
        return []

    monkeypatch.setattr(main, "get_new_messages", fake_get_new_messages)

    # Stub out notifications
    monkeypatch.setattr(main, "build_notifications", lambda messages: [])

    # Fake api with session attribute
    api = types.SimpleNamespace(session="abc")
    monkeypatch.setattr(main, "db", {})

    base = 10
    max_interval = 40
    monkeypatch.setattr(main.config, "POLL_INTERVAL_SEC", base, raising=False)
    monkeypatch.setattr(main.config, "MAX_POLL_INTERVAL_SEC", max_interval, raising=False)

    interval = base
    # First iteration: 10 -> 20
    interval, outside = main.run_iteration(api, interval)
    assert outside is False
    assert interval == 20

    # Second: 20 -> 40
    interval, outside = main.run_iteration(api, interval)
    assert outside is False
    assert interval == 40

    # Third: 40 -> capped at 40
    interval, outside = main.run_iteration(api, interval)
    assert outside is False
    assert interval == max_interval
