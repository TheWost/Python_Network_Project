import json
from typing import Any


def format_msg(
    msg_type: str,
    action: str,
    dst: str | int = "",
    src: str | int = "",
    reason: str = "",
    data: Any = "",
    filename: str = "",
) -> str:
    """Formats a JSON object that represents a message between a server and a client.

    Args:
        msg_type: The category of the message. Must be one of the allowed types.
        action: The specific operation or subtype being performed (e.g., "group",
          "get_usernames").
        dst: The destination identifier (Client username or Ip Address)
        src: The source identifier (Client username or Ip Address)
        reason: An optional explanation, typically used for errors, warnings, or
          auth failures.
        data: The payload or core content of the message (can be of any type,
          such as a dict, bool, or str).
        filename: An optional file name if the message relates to file transfer
          or storage.

    Returns:
        str: A **JSON string** (a string formatted according to JavaScript Object
        Notation, used here for serializing data structures so they can be sent
        across a network).

    Raises:
        ValueError: If `msg_type` is not in the list of allowed message types.

    Example:
        >>> format_msg(msg_type="chat", action="group", src="127.0.0.1", data=True)
        '{"msg_type": "chat", "action": "group", "data": true, "dst": "", "src": "d1", "reason": "", "filename": ""}'
    """
    aviable_msg_types = [
        "command",
        "query",
        "chat",
        "response",
        "auth",
        "warning",
        "remote",
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
            "filename": filename,
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
