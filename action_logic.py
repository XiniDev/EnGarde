from action import *

states = [{
            'score' : 0,
            'push' : 0,
            'move' : 0,
            'charge' : 0
          } for i in range(2)]

def compute(a_1: Action, a_2: Action, distance: int) -> None:
    global states
    score = score_function(a_1, a_2, distance)
    push = push_function(a_1, a_2, distance)
    move = move_function(a_1, a_2, distance, push)
    charge = set_charge(a_1, a_2)
    for i in range(2):
        states[i]['score'] = score[i]
        states[i]['push'] = push[i]
        states[i]['move'] = move[i]
        states[i]['charge'] = charge[i]

def set_reach(a_1: Action, a_2: Action, distance: int, buffer: int) -> None:
    return -distance + a_1.MOVE + a_2.MOVE + buffer

def set_charge(a_1: Action, a_2: Action) -> list[int]:
    return [states[0]['charge'] + a_1.CHARGE if a_1.CHARGE == 1 else 0, states[1]['charge'] + a_2.CHARGE if a_2.CHARGE == 1 else 0]

def score_function(a_1: Action, a_2: Action, distance: int) -> list[int]:
    winner = (states[0]['charge'] + a_1.SCORE) * a_1.IS_X - (states[1]['charge'] + a_2.SCORE) * a_2.IS_X
    reach = set_reach(a_1, a_2, distance, 1)
    res = winner * reach
    check_condition = (a_1.IS_X + a_2.IS_X) * reach * (a_1.BLOCK * a_2.BLOCK)
    if check_condition > 0:
        return [1, 1] if res == 0 else [1 if res > 0 else 0, 1 if res < 0 else 0]
    else:
        return [0, 0]

def push_function(a_1: Action, a_2: Action, distance: int) -> list[int]:
    winner = a_1.PUSH - a_2.PUSH
    reach = set_reach(a_1, a_2, distance, 0)
    res = winner * reach
    check_condition = reach * (a_1.STANCE * a_2.STANCE)
    if check_condition > 0:
        return [1 if res > 0 else 0, 1 if res < 0 else 0]
    else:
        return [0, 0]

def move_function(a_1: Action, a_2: Action, distance: int, push: list[int]) -> list[int]:
    reach = -set_reach(a_1, a_2, distance, -1)
    return push if 1 in push else [a_1.MOVE if reach > 0 else 0, a_2.MOVE if reach > 0 else 0]