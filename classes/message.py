#
#
#class Msg:
#    def __init__(self, data, msg_type):
#        self.data = data
#        self.msg_type = msg_type
#
#
#        self.aviable_msg_types = ["command", "query","chat"]
#
#
#    def 



def msg(msg_type, action, data=""):

    aviable_msg_types = ["command", "query", "chat"]


    if msg_type in aviable_msg_types:
        return {"type": msg_type,
                "action": action,
                "data": data
                }
    raise ValueError("Invalid msg type")
