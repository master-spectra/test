class ActionSpace:
    def __init__(self):
        self.actions = [
            "move_forward",
            "move_backward",
            "turn_left",
            "turn_right",
            "attack",
            "defend",
            "collect_resource",
            "repair_base",
            "call_for_help",
            "use_special_ability"
        ]

    def get_action(self, index):
        return self.actions[index]

    def get_action_size(self):
        return len(self.actions)
