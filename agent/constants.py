class Actions:
    SLEEP = 0
    COLLECT = 1
    SEND = 2


ACTION_IDX_TO_ACTION_MAP = {
    Actions.SLEEP: "Sleep",
    Actions.COLLECT: "Collect",
    Actions.SEND: "Send"
}

#reverse mapping
ACTION_TO_IDX_MAP = {ACTION_IDX_TO_ACTION_MAP[k]: k for k in ACTION_IDX_TO_ACTION_MAP}