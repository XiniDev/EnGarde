import random

from collections import deque

ACTION_SYMBOLS_NUM = [1, 2, 3, 4, 5, 6, 7, 8, 9]
ALL_MOVES_NUM = {
    1: [6,6,7,1,5,5],
    2: [4,4,4,4],
    3: [3,3,5,5,1,5],
    4: [6,1,5,5],
    5: [6,6,6,7,2,5,5,5],
    6: [6,6],
    7: [5,9],
    8: [5,8]
}

class SimpleAI():
    def __init__(self, id) -> None:
        self.id = id

        self.deck = deque([1,2,3,4,5,6,7,8])
        self.hand = []

        random.shuffle(deck)
        hand.extend([self.deck.popleft() for i in range(4)])

        self.c_actions = []
        self.p_actions = []

        slots = 6
        done = False
    
    def reset_actions(self) -> None:
        self.done = False
        # self.p_actions = self.c_actions
        self.c_actions = self.f_actions
        self.f_actions = []


    def decision(self) -> list[int]:
        move = self.move_selection()
        if done:
            result = self.c_actions
            reset_actions()
            print(f"AI {self.id} Curr: {result} | AI {self.id} Futr: {self.c_actions}")
            return result
        else:
            return self.decision()

    def move_selection(self) -> int:
        if self.slots <= 0:
            self.slots = 6 + self.slots
            self.done = True
            res = -1
        else:
            choice = int(random.random() * 4)
            move_id = play_move(choice)
            move = ALL_MOVES_NUM[move_id]
            self.append_actions(move)
            self.update_slots(move)
            res = move_id
        return res

    def play_move(self, choice: int) -> int:
        move = self.hand[choice]
        self.hand[choice] = self.deck.popleft()
        self.deck.append(move)
        return move

    def append_actions(self, move: list[int]) -> None:
        value = 6 - len(self.c_actions)
        split = [move[0:value], move[value:]] if value > 0 else [move, []]
        self.c_actions.extend(split[0])
        self.f_actions.extend(split[1])

    def update_slots(self, move: list[int]) -> None:
        if len(move) >= self.slots:
            self.slots = 6 - (len(move) - self.slots)
            self.done = True
        else:
            self.slots = self.slots - len(move)

ai_1 = SimpleAI(1)
ai_2 = SimpleAI(2)

curr1 = []
curr2 = []

# def check_actions():
#     a_1 = curr1[self.action - 1]
#     a_2 = curr2[self.action - 1]
#     al.compute(a_1, a_2, self.distance)
#     states_1 = {**al.states[0], **{'mat_pos': self.playerModels[0].mat_pos}}
#     states_2 = {**al.states[1], **{'mat_pos': self.playerModels[1].mat_pos}}
#     print(f"User: {a_1} ; {states_1} | Opp: {a_2} ; {states_2} | Distance: {self.distance}")
#     self.action_check = (a_1, al.states[0], a_2, al.states[1])

while True:
    curr1 = ai_1.decision()
    curr2 = ai_2.decision()
    