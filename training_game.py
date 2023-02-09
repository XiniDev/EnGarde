import random

from collections import deque

# ACTION_SYMBOLS = ['x', 'X', 'b', 'B', '_', '-', '=', '>', '<']
# ACTION_SYMBOLS_NUM = [1, 2, 3, 4, 5, 6, 7, 8, 9]
ALL_MOVES_NUM = {
    1: [6,6,7,1,5,5],
    2: [4,4,4,4],
    3: [3,3,5,5,1,5],
    4: [6,1,5,5],
    5: [6,6,6,7,2,5,5,5],
    6: [6,6],
    7: [5,9],
    8: [5,8],
}

# action checking
# check = [SCORE, IS_X, CHARGE, PUSH, MOVE, BLOCK, STANCE]
ACTION_PROPERTIES = {
    # 0: [0, 0, 0, 0, 0, 1, 1],
    1: [2, 2, 0, 0, 0, 2, 2],
    2: [1.5, 1, 0, 1.5, 1, 1, 1],
    3: [0, 0, 0, 0, 0, 0, 1],
    4: [0, 0, 0, 0, 0, 0, 0],
    5: [0, 0, 0, 0, 0, 1, 1],
    6: [0, 0, 1, 0, 0, 1, 1],
    7: [0, 0, 1, 1, 1, 1, 1],
    8: [0, 0, 0, 0, 1, 1, 1],
    9: [0, 0, 0, 0, -1, 1, 1],
}

PISTE_LENGTH = 7


class SimpleAI():
    def __init__(self, id) -> None:
        self.id = id

        self.mat_pos = int((id - 1.5) * 2)

        self.deck = deque([1,2,3,4,5,6,7,8])
        self.hand = []

        random.shuffle(self.deck)
        self.hand.extend([self.deck.popleft() for i in range(4)])

        self.c_actions = []
        self.f_actions = []

        self.slots = 6
        self.done = False
    
    def full_reset(self) -> None:
        self.deck = deque([1,2,3,4,5,6,7,8])
        self.hand = []

        random.shuffle(self.deck)
        self.hand.extend([self.deck.popleft() for i in range(4)])
        self.score_reset()

    def score_reset(self) -> None:
        self.mat_pos = int((self.id - 1.5) * 2)
        self.c_actions = []
        self.f_actions = []
        self.slots = 6
        self.done = False
    
    def reset_actions(self) -> None:
        self.done = False
        # self.p_actions = self.c_actions
        self.c_actions = self.f_actions
        self.f_actions = []

    def decision(self) -> list[int]:
        move = self.move_selection()
        if self.done:
            result = self.c_actions
            self.reset_actions()
            print(f"AI {self.id} | Pos: {self.mat_pos} | Curr: {result} | Futr: {self.c_actions}")
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
            move_id = self.play_move(choice)
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

class SimpleGE():
    def __init__(self) -> None:
        self.ai_1 = SimpleAI(1)
        self.ai_2 = SimpleAI(2)

        self.curr1 = []
        self.curr2 = []

        self.score = [0, 0]

        self.states = [[0,0], [0,0], [0,0], [0,0]]

    def game_loop(self) -> None:
        scored = self.turn_loop()
        winner = 0
        if scored:
            self.ai_1.score_reset()
            self.ai_2.score_reset()
            print(f"Score: [{self.score[0]} : {self.score[1]}]")
        if 15 in self.score:
            if self.score[0] == 15:
                winner = 1
            if self.score[1] == 15:
                winner = 2
            self.reset()
        return winner
    
    def reset(self) -> None:
        self.ai_1.full_reset()
        self.ai_2.full_reset()
        self.curr1 = []
        self.curr2 = []
        self.score = [0, 0]
        self.states = [[0,0], [0,0], [0,0], [0,0]]

    def turn_loop(self) -> bool:
        self.curr1 = self.ai_1.decision()
        self.curr2 = self.ai_2.decision()
        # print(f"Curr 1: {self.curr1} | Curr 2: {self.curr2}")
        for i in range(6):
            distance = self.ai_2.mat_pos - self.ai_1.mat_pos - 1
            self.check_actions(i, distance)
            self.update_mat_pos(distance)
            score = self.update_score()
            if 1 in score:
                self.score[0] += score[0]
                self.score[1] += score[1]
                # something is bugging double scoring will fix
                return True
        return False

    def check_actions(self, i: int, distance: int) -> None:
        a_1 = self.curr1[i]
        a_2 = self.curr2[i]
        self.states = self.compute(a_1, a_2, distance)

    def update_mat_pos(self, distance: int) -> None:
        self.ai_1.mat_pos += self.states[2][0]
        self.ai_2.mat_pos -= self.states[2][1]
        if distance == 0:
            self.ai_1.mat_pos -= self.states[1][1]
            self.ai_2.mat_pos += self.states[1][0]

    def update_score(self) -> list[int]:
        score = self.states[0]
        if not 1 in score:
            if self.ai_1.mat_pos > (PISTE_LENGTH - 1) / 2 or self.ai_1.mat_pos < -1 * (PISTE_LENGTH - 1) / 2:
                score[1] = 1
            if self.ai_2.mat_pos > (PISTE_LENGTH - 1) / 2 or self.ai_2.mat_pos < -1 * (PISTE_LENGTH - 1) / 2:
                score[0] = 1
        return score


    def compute(self, a_1: int, a_2: int, distance: int) -> list[list[int]]:
        a_1_p = ACTION_PROPERTIES[a_1]
        a_2_p = ACTION_PROPERTIES[a_2]
        reach = self.set_reach(a_1_p[4], a_2_p[4], distance)
        score = self.score_function(a_1_p, a_1_p, reach, self.states[3])
        push = self.push_function(a_1_p, a_2_p, reach)
        move = self.move_function(a_1_p, a_2_p, reach, push)
        charge = self.set_charge(a_1_p[2], a_2_p[2], self.states[3])
        return [score, push, move, charge]

    def set_reach(self, m1: float, m2: float, distance: int) -> None:
        return -distance + m1 + m2

    def set_charge(self, c1: float, c2: float, charge_state: list[int]) -> list[int]:
        return [charge_state[0] + c1 if c1 == 1 else 0, charge_state[1] + c2 if c2 == 1 else 0]

    def score_function(self, a_1_p: list[float], a_2_p: list[float], reach: float, charge_state: list[int]) -> list[int]:
        scorer = (charge_state[0] + a_1_p[0]) * a_1_p[1] - (charge_state[1] + a_2_p[0]) * a_2_p[1]
        score_con = (a_1_p[1] + a_2_p[1]) * (reach + 1) * (a_1_p[5] * a_2_p[5])
        if score_con > 0:
            return [1, 1] if scorer == 0 else [1 if scorer > 0 else 0, 1 if scorer < 0 else 0]
        else:
            return [0, 0]

    def push_function(self, a_1_p: list[float], a_2_p: list[float], reach: float) -> list[int]:
        pusher = a_1_p[3] - a_2_p[3]
        push_con = reach * (a_1_p[6] * a_2_p[6])
        if push_con > 0:
            return [1 if pusher > 0 else 0, 1 if pusher < 0 else 0]
        else:
            return [0, 0]

    def move_function(self, a_1_p: list[float], a_2_p: list[float], reach: float, push: list[int]) -> list[int]:
        return push if 1 in push else [a_1_p[4] if reach <= 0 else 0, a_2_p[4] if reach <= 0 else 0]

ge = SimpleGE()
wins = [0, 0]
stop = False

while not stop:
    winner = ge.game_loop()
    if winner != 0:
        print(f"Winner : AI {winner}")
        wins[winner - 1] += 1
        print(f"Wins: {wins}")
    if 10 in wins:
        stop = True