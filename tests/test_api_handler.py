import pydantic
import pytest

from api_handler.api import NortecApiWrapper
from api_handler.exceptions import (
    NortecApiApplicationException,
    NortecApiServerException,
    NortecApiCorruptedSessionException,
    NortecApiSessionExpiredException,
    NortecApiLogicException,
)
from api_handler.models import Message, MessageRow, MessageColumn


def test_raise_for_response_code_success_and_errors():
    ok = {"Return": 100}
    NortecApiWrapper._raise_for_response_code(ok)

    with pytest.raises(NortecApiServerException):
        NortecApiWrapper._raise_for_response_code({"Return": 206})

    with pytest.raises(NortecApiSessionExpiredException):
        NortecApiWrapper._raise_for_response_code({"Return": 207})

    with pytest.raises(NortecApiCorruptedSessionException):
        NortecApiWrapper._raise_for_response_code({"Return": 208})

    with pytest.raises(NortecApiApplicationException):
        NortecApiWrapper._raise_for_response_code({"Return": 224})

    with pytest.raises(NortecApiLogicException):
        NortecApiWrapper._raise_for_response_code({})


def test_validate_session_triggers_login_on_expired_session(monkeypatch):
    calls = {"login": 0}

    def fake_make_api_call(self, endpoint, params):
        # Always simulate an expired session on validate
        raise NortecApiSessionExpiredException()

    def fake_login(self, username, password):
        calls["login"] += 1

    monkeypatch.setattr(NortecApiWrapper, "_make_api_call", fake_make_api_call)
    monkeypatch.setattr(NortecApiWrapper, "_login", fake_login)

    # Should not raise, but should call _login exactly once during __init__
    wrapper = NortecApiWrapper(username="user", password="pass", session="old")
    assert wrapper.username == "user"
    assert calls["login"] == 1


def test_get_messages_parses_sections(monkeypatch):
    def fake_make_api_call(self, endpoint, params):
        msg = Message(
            Name="n1",
            Title="t1",
            Description=[],
            Rows=[
                MessageRow(
                    Columns2=MessageColumn(
                        Cells=["Færdig"],
                        Type=11,
                    )
                )
            ],
            Collapsed=False,
        )
        return {"Sections": [msg.model_dump()] }

    monkeypatch.setattr(NortecApiWrapper, "_make_api_call", fake_make_api_call)

    wrapper = NortecApiWrapper(username="user", password="pass", session="sess")
    messages = wrapper.get_messages()

    assert len(messages) == 1
    assert messages[0].Name == "n1"


def test_get_messages_skips_sections_without_name(monkeypatch):
    def fake_make_api_call(self, endpoint, params):
        return {
            "Sections": [
                {
                    "Title": "Send en test besked",
                    "Description": [],
                    "Rows": [{"Tab": {"Text": "Send", "Pos": 1, "Sure": False}}],
                    "Collapsed": False,
                },
                {
                    "Name": "n1",
                    "Title": "t1",
                    "Description": [],
                    "Rows": [{"Columns2": {"Cells": ["Færdig"], "Type": 11}}],
                    "Collapsed": False,
                },
            ]
        }

    monkeypatch.setattr(NortecApiWrapper, "_make_api_call", fake_make_api_call)

    wrapper = NortecApiWrapper(username="user", password="pass", session="sess")
    messages = wrapper.get_messages()

    assert [message.Name for message in messages] == ["n1"]


def test_get_messages_raises_on_named_section_with_unknown_format(monkeypatch):
    def fake_make_api_call(self, endpoint, params):
        return {
            "Sections": [
                {
                    "Name": "n1",
                    "Title": "t1",
                    "Description": [],
                    "Rows": [{"Columns": {"Cells": ["Færdig"], "Type": 11}}],
                    "Collapsed": False,
                },
            ]
        }

    monkeypatch.setattr(NortecApiWrapper, "_make_api_call", fake_make_api_call)

    wrapper = NortecApiWrapper(username="user", password="pass", session="sess")

    with pytest.raises(pydantic.ValidationError):
        wrapper.get_messages()
