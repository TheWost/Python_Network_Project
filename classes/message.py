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
    """Formats an json object that represents msg between server and client"""
    aviable_msg_types = ["command", "query", "chat"]

    if not msg_type in aviable_msg_types:
        raise ValueError("Invalid msg type")

    return json.dumps(
        {
            "type": msg_type,
            "action": action,
            "data": data,
            "dst": dst,
            "src": src,
            "reason": reason,
        }
    )
