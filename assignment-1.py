def pre_core(TS, C, index_direction_target, index_direction_other, a=None):
    to = TS["to"]
    result = set()
    if type(C) == str:
        C = {C}

    for transition in to:
        if transition[index_direction_target] in C and (a is None or transition[1] == a):
            result.add(transition[index_direction_other])
    return result


def pre(TS, C, a=None):
    return pre_core(TS, C, 2, 0, a)


def post(TS, C, a=None):
    return pre_core(TS, C, 0, 2, a)


def is_action_deterministic(TS):
    if len(TS["I"]) > 1:
        return False

    transitions_key_set = set()
    for transition in TS["to"]:
        state_from, action, state_to = transition
        transition_key = (state_from, action)
        if transition_key in transitions_key_set:
            return False
        transitions_key_set.add(transition_key)

    return True


def is_label_deterministic(TS):
    if len(TS["I"]) > 1:
        return False

    L = TS["L"]
    for state in TS["S"]:
        state_post_labels_list = []
        state_post_set = post(TS, {state})
        for state_post in state_post_set:
            state_post_labels = L(state_post)
            for state_other_post_labels in state_post_labels_list:
                if state_post_labels == state_other_post_labels:
                    return False
            state_post_labels_list.append(state_post_labels)

    return True


if __name__ == '__main__':
    pass
