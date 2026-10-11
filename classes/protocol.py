import json
from typing import Any


def format_msg(
    msg_type: str,
    action: str,
    dst: str | int = "",
    src: str | int = "",
    reason: str = "",
    data: Any = "",
) -> str:
    """Formats an json object that represents msg between server and client. Returns str
    e.g. format_msg(msg_type="chat", action="group", src="127.0.0.1", data=True)  -> json.dumps("msg_type": "chat", "action": "group", "src": "127.0.0.1", "data": True)
    Avaiable msg types = [command, query, chat, response, auth, warning]
    """
    aviable_msg_types = [
        "command",
        "query",
        "chat",
        "response",
        "auth",
        "warning",
    ]

    if not msg_type in aviable_msg_types:
        raise ValueError("Invalid msg type")

    return json.dumps(
        {
            "msg_type": msg_type,
            "action": action,
            "data": data,
            "dst": dst,
            "src": src,
            "reason": reason,
        }
    )


def main():
    msg = format_msg(msg_type="chat", action="whisper", dst="kitty67", data="727")
    print(json.loads(msg))
    msg = format_msg(msg_type="query", action="get_usernames")
    print(json.loads(msg))
    msg = format_msg(
        msg_type="response", action="get_usersnames", data=["kitty67", "puppy67"]
    )
    print(json.loads(msg))
    msg = format_msg(msg_type="response", action="register", data=False)
    print(json.loads(msg))


if __name__ == "__main__":
    main()
