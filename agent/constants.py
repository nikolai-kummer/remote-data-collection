class ActionNames:
    SLEEP = "Sleep"
    COLLECT = "Collect"
    SEND = "Send"

class Actions:
    SLEEP = 0
    COLLECT = 1
    SEND = 2


ACTION_IDX_TO_ACTION_MAP = {
    Actions.SLEEP: ActionNames.SLEEP,
    Actions.COLLECT: ActionNames.COLLECT,
    Actions.SEND: ActionNames.SEND
}

#reverse mapping
ACTION_TO_IDX_MAP = {ACTION_IDX_TO_ACTION_MAP[k]: k for k in ACTION_IDX_TO_ACTION_MAP}