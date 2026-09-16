import json

def msg(msg_type, action, data=""):

    aviable_msg_types = ["command", "query", "chat"]


    if not msg_type in aviable_msg_types:
        raise ValueError("Invalid msg type")



    return json.dumps({"type": msg_type,
            "action": action,
            "data": data
            })
