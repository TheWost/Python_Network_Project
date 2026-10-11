import json

import pytest

from classes.protocol import format_msg


def parse(*args, **kwargs):
    return json.loads(format_msg(*args, **kwargs))


def test_chat_whisper():
    assert parse(msg_type="chat", action="whisper", dst="kitty67", data="727") == {
        "msg_type": "chat",
        "action": "whisper",
        "data": "727",
        "dst": "kitty67",
        "src": "",
        "reason": "",
    }


def test_query_get_usernames():
    assert parse(msg_type="query", action="get_usernames") == {
        "msg_type": "query",
        "action": "get_usernames",
        "data": "",
        "dst": "",
        "src": "",
        "reason": "",
    }


def test_response_get_usernames():
    assert parse(
        msg_type="response",
        action="get_usersnames",
        data=["kitty67", "puppy67"],
    ) == {
        "msg_type": "response",
        "action": "get_usersnames",
        "data": ["kitty67", "puppy67"],
        "dst": "",
        "src": "",
        "reason": "",
    }


def test_response_register():
    assert parse(msg_type="response", action="register", data=False) == {
        "msg_type": "response",
        "action": "register",
        "data": False,
        "dst": "",
        "src": "",
        "reason": "",
    }


def test_invalid_msg_type():
    with pytest.raises(ValueError, match="Invalid msg type"):
        format_msg(msg_type="bogus", action="")
