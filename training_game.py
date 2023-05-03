import random

from collections import deque

import copy

import numpy as np
import dqn as dqn

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
    1: [1, 1, 0, 0, 0, 1, 1],
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

verbose = False

class Agent():
    def __init__(self, id: int, gamma: float) -> None:
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

        self.move_selected = None

        # freq stuff
        self.move_freq = [0,0,0,0,0,0,0,0,0]
        self.begin_freq = [0,0,0,0,0,0,0,0,0]
        
        self.begin_new = True

        self.first_score = 0
    
    def full_reset(self) -> None:
        self.reset_cards()
        self.score_reset()
        self.other_reset()
        self.reset_memory()

    def reset_cards(self) -> None:
        self.deck = deque([1,2,3,4,5,6,7,8])
        self.hand = []

        random.shuffle(self.deck)
        self.hand.extend([self.deck.popleft() for i in range(4)])

    def other_reset(self) -> None:
        self.first_score = 0

    def reset_memory(self) -> None:
        pass

    def score_reset(self) -> None:
        self.mat_pos = int((self.id - 1.5) * 2)
        self.c_actions = []
        self.f_actions = []
        self.slots = 6
        self.done = False

        # freq stuff
        self.begin_new = True
    
    def reset_actions(self) -> None:
        self.done = False
        # self.p_actions = self.c_actions
        self.c_actions = self.f_actions
        self.f_actions = []

    def decision(self, mat_pos: list[int], opp_past_actions: list[int]) -> list[int]:
        self.move_selected = self.move_selection(self.get_action())
        if self.done:
            result = self.c_actions
            self.reset_actions()
            if (verbose):
                print(f"AI {self.id} | Pos: {self.mat_pos} | Curr: {result} | Futr: {self.c_actions}")
            return result
        else:
            self.set_memory(0, mat_pos, opp_past_actions)
            return self.decision(mat_pos, opp_past_actions)

    def move_selection(self, choice: int) -> int:
        if self.slots <= 0:
            self.slots = 6 + self.slots
            self.done = True
            res = 0
        else:
            move_id = self.play_move(choice)
            move = ALL_MOVES_NUM[move_id]
            self.append_actions(move)
            self.update_slots(move)
            res = move_id

        # freq stuff
        self.move_freq[res] += 1
        if self.begin_new:
            self.begin_freq[res] += 1
            self.begin_new = False

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

    def set_memory(self, reward_score: int, mat_pos: list[int], opp_past_actions: list[int]) -> None:
        pass

    def get_action(self) -> int:
        return int(random.random() * 4)

    def convert_binary(self, numbers: list[int], size: int) -> None:
        res = []
        for n in numbers:
            b = []
            binary = n
            for i in range(size):
                b.append(binary & 1)
                binary = binary >> 1
            res.extend(b[::-1])
        return res

    def get_state(self, mat_pos: list[int], opp_past_actions: list[int]) -> list[int]:
        hand = sorted([h-1 for h in self.hand])
        hand = self.convert_binary(hand, 3)
        bin_mat_pos = self.convert_binary([p+4 for p in mat_pos], 3)

        o_actions = [0] * 6
        for i, a in enumerate(opp_past_actions):
            o_actions[i] = a
        bin_o_actions = self.convert_binary(o_actions, 4)

        c_actions = [0] * 6
        for i, a in enumerate(self.c_actions):
            c_actions[i] = a
        bin_c_actions = self.convert_binary(c_actions, 4)

        return [*hand, *bin_mat_pos, *bin_o_actions, *bin_c_actions]

    def get_reward(self, reward_score: int) -> int:
        reward = reward_score
        return reward

# basic Linear fc for DQN
class LinearDQNAgent(Agent):
    def __init__(self, id: int, gamma: float) -> None:
        super().__init__(id, gamma)

        self.reward = 0
        self.old_state = None
        self.state = None

        self.old_hand = None

        self.reset_memory()

        self.model = dqn.LinearQNetwork(66, 256, 8)
        self.trainer = dqn.LinearTrainer(self.model, 0.001, gamma, 1.0)
        # self.trainer.epsilon = 0.9

    def set_memory(self, reward_score: int, mat_pos: list[int], opp_past_actions: list[int]) -> None:
        opp_actions = opp_past_actions
        if len(opp_past_actions) == 0:
            opp_actions = [0] * 6

        self.old_state = self.state
        self.state = self.get_state(mat_pos, opp_actions)
        self.state = np.array(self.state, dtype=int)
        
        self.reward = self.get_reward(reward_score)

        state = self.old_state
        action = self.move_selected - 1
        reward = self.reward
        new_state = self.state

        self.trainer.memorise(state, action, reward, new_state, self.old_hand)

        self.old_hand = sorted([h-1 for h in self.hand])

    def reset_memory(self) -> None:
        hand = sorted([h-1 for h in self.hand])
        bin_hand = self.convert_binary(hand, 3) # 12 each
        mat_pos = [-1, 1]
        bin_mat_pos = self.convert_binary([p+4 for p in mat_pos], 3) # 6 instead of 2
        opp_actions = curr_actions = [0, 0, 0, 0] * 6 # 24 each! 24 * 2 = 48
        self.state = [*bin_hand, *bin_mat_pos, *opp_actions, *curr_actions]
        self.state = np.array(self.state, dtype=int)
        self.old_hand = hand

    def get_action(self) -> int:
        move = self.trainer.predict(self.state, self.hand)
        return move

# RNN for DQN
class RNNDQNAgent(Agent):
    def __init__(self, id: int, gamma: float) -> None:
        super().__init__(id, gamma)

        self.reward = 0
        self.old_state = None
        self.state = None

        self.old_hand = None

        self.sequence_length = 5

        self.reset_memory()

        self.model = dqn.RNNQNetwork(66, 256, 8)
        self.trainer = dqn.RNNTrainer(self.model, 0.001, gamma, 1.0)

    def set_memory(self, reward_score: int, mat_pos: list[int], opp_past_actions: list[int]) -> None:
        opp_actions = opp_past_actions
        if len(opp_past_actions) == 0:
            opp_actions = [0] * 6

        self.old_state = copy.deepcopy(self.state)
        state = self.get_state(mat_pos, opp_actions)
        self.state = np.roll(self.state, -1, axis=0)
        self.state[-1, :] = state
        
        self.reward = self.get_reward(reward_score)

        state = self.old_state
        action = self.move_selected - 1
        reward = self.reward
        new_state = self.state

        # print(self.id, state)
        self.trainer.memorise(state, action, reward, new_state, self.old_hand)

        self.old_hand = sorted([h-1 for h in self.hand])

    def reset_memory(self) -> None:
        hand = sorted([h-1 for h in self.hand])
        hand = self.convert_binary(hand, 3) # 12 each
        mat_pos = [-1, 1]
        bin_mat_pos = self.convert_binary([p+4 for p in mat_pos], 3) # 6 instead of 2
        opp_actions = curr_actions = [0, 0, 0, 0] * 6 # 24 each! 24 * 2 = 48
        state = [*hand, *bin_mat_pos, *opp_actions, *curr_actions]
        self.state = np.zeros((self.sequence_length, 66))
        self.state[-1, :] = state
        self.old_hand = hand

    def get_action(self) -> int:
        move = self.trainer.predict(self.state, self.hand)
        return move


class SimpleGE():
    def __init__(self, ai_1: Agent, ai_2: Agent) -> None:
        self.ai_1 = ai_1
        self.ai_2 = ai_2

        self.curr1 = []
        self.curr2 = []

        self.score = [0, 0]

        self.states = [[0,0], [0,0], [0,0], [0,0]]

        self.turn = 1

    def game_loop(self) -> tuple:
        scored = self.turn_loop()
        self.turn += 1
        winner = 0
        curr_score = self.score

        first_scores = [0, 0]

        if scored:
            self.ai_1.score_reset()
            self.ai_2.score_reset()
            self.turn = 1
            if (verbose):
                print(f"Score: [{self.score[0]} : {self.score[1]}]")
        if 15 in self.score:
            if self.score[0] == 15 and self.score[1] == 15:
                winner = 3
            elif self.score[0] == 15:
                winner = 1
            elif self.score[1] == 15:
                winner = 2

            first_scores = [self.ai_1.first_score, self.ai_2.first_score]

            self.reset()
        return winner, curr_score, first_scores
    
    def reset(self) -> None:
        self.ai_1.full_reset()
        self.ai_2.full_reset()
        self.curr1 = []
        self.curr2 = []
        self.score = [0, 0]
        self.states = [[0,0], [0,0], [0,0], [0,0]]

    def turn_loop(self) -> bool:
        past1 = self.ai_1.c_actions
        past2 = self.ai_2.c_actions
        self.curr1 = self.ai_1.decision([self.ai_1.mat_pos, self.ai_2.mat_pos], past2)
        self.curr2 = self.ai_2.decision([self.ai_1.mat_pos, self.ai_2.mat_pos], past1)

        r1 = 0
        r2 = 0

        # print(self.turn)

        # print(f"Curr 1: {self.curr1} | Curr 2: {self.curr2}")
        for i in range(6):
            distance = self.ai_2.mat_pos - self.ai_1.mat_pos - 1
            self.check_actions(i, distance)
            self.update_mat_pos(distance)
            score = self.update_score()
            if 1 in score:
                self.score[0] += score[0]
                self.score[1] += score[1]

                # try make the agent want to stay as long/short as possible in a turn? if rewards based on turn number
                # r1 = 10 * (score[0] * 2 - score[1]) + self.turn * 5 * (score[0] * 2 - score[1])
                # r2 = 10 * (score[1] * 2 - score[0]) + self.turn * 5 * (score[1] * 2 - score[0])

                # if score on first turn then get massive bonus
                # bonus = 2 if self.turn == 1 else 0
                # r1 = 10 * (score[0] * 2 * bonus - score[1])
                # r2 = 10 * (score[1] * 2 * bonus - score[0])

                # normal scoring rewards
                r1 = 10 * (score[0] * 2 - score[1])
                r2 = 10 * (score[1] * 2 - score[0])

                if self.turn == 1:
                    # if score happened in first turn account for that
                    self.ai_1.first_score += score[0]
                    self.ai_2.first_score += score[1]

                self.set_ai_states(1, r1)
                self.set_ai_states(2, r2)
                return True
            else:
                # add rewards for blocking attack!
                # blocking agent gets rewards, agent blocked loses rewards
                a_1 = self.curr1[i]
                a_2 = self.curr2[i]
                if ACTION_PROPERTIES[a_1][5] == 0 and distance == 0:
                    r1 += ACTION_PROPERTIES[a_2][0] * 4
                    # r2 -= ACTION_PROPERTIES[a_1][0] * 0
                if ACTION_PROPERTIES[a_2][5] == 0 and distance == 0:
                    # r2 += ACTION_PROPERTIES[a_1][0] * 4
                    r1 -= ACTION_PROPERTIES[a_2][0] * 0
        self.set_ai_states(1, r1)
        self.set_ai_states(2, r2)
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
        score = self.score_function(a_1_p, a_2_p, reach, self.states[3])
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

    def set_ai_states(self, id: int, reward_score: int) -> None:
        if id == 1:
            self.ai_1.set_memory(reward_score, [self.ai_1.mat_pos, self.ai_2.mat_pos], self.curr2)
        else:
            self.ai_2.set_memory(reward_score, [self.ai_1.mat_pos, self.ai_2.mat_pos], self.curr1)

class DoubleGE(SimpleGE):
    def __init__(self, ai_1: Agent, ai_2: Agent, model_strs: list[str], fixed_epsilon: int) -> None:
        super().__init__(ai_1, ai_2)
        self.loaded_models = model_strs
        self.curr_agent_id = -1
        self.fixed_epsilon = fixed_epsilon
        
    def reset(self) -> None:
        self.ai_1.full_reset()
        self.ai_2.full_reset()
        self.curr1 = []
        self.curr2 = []
        self.score = [0, 0]
        self.states = [[0,0], [0,0], [0,0], [0,0]]
        self.load_random()

    def load_random(self) -> None:
        self.curr_agent_id = random.randrange(0, len(self.loaded_models))
        self.ai_2.trainer.load(self.loaded_models[self.curr_agent_id])
        self.ai_2.trainer.epsilon = self.fixed_epsilon


def avg_sort(array: list[int]) -> dict:
    a_sum = sum(array) - array[0]
    sorted_dict = {
        'Lunge': array[1] / a_sum,
        'Parry': array[2] / a_sum,
        'Riposte': array[3] / a_sum,
        'Thrust': array[4] / a_sum,
        'Flèche': array[5] / a_sum,
        'Fake': array[6] / a_sum,
        'Dodge': array[7] / a_sum,
        'Move': array[8] / a_sum,
    }

    return dict(sorted(sorted_dict.items(), key=lambda x:x[1], reverse=True))

def rel_sort(array1: list[int], array2: list[int]) -> dict:
    sorted_dict = {
        'Lunge': array2[1] / array1[1] if array1[1] > 0 else 0,
        'Parry': array2[2] / array1[2] if array1[2] > 0 else 0,
        'Riposte': array2[3] / array1[3] if array1[3] > 0 else 0,
        'Thrust': array2[4] / array1[4] if array1[4] > 0 else 0,
        'Flèche': array2[5] / array1[5] if array1[5] > 0 else 0,
        'Fake': array2[6] / array1[6] if array1[6] > 0 else 0,
        'Dodge': array2[7] / array1[7] if array1[7] > 0 else 0,
        'Move': array2[8] / array1[8] if array1[8] > 0 else 0,
    }

    return dict(sorted(sorted_dict.items(), key=lambda x:x[1], reverse=True))

model_strs = ["trained_wder/fc_self_play/g070/agent2/checkpoint_epo50_eps099.pth", "trained_wder/fc_self_play/g070/agent1/checkpoint_epo50_eps099.pth"]

ai_1 = LinearDQNAgent(1, 0.7)
ai_2 = LinearDQNAgent(2, 0.7)

ge = SimpleGE(ai_1, ai_2)
# ge = DoubleGE(ai_1, ai_2, model_strs, 0.1)

testing = False
resume = 0
games = 0 + resume
wins = [0, 0]
stop = False
target_wins_100 = deque()
fs_chance_1, fs_chance_2 = 0, 0
total_games = 5000
# ge.ai_1.trainer.load("model/checkpoint_epo11_eps333.pth")
# ge.ai_1.trainer.load("trained_wder/fc_self_play/g090/agent1/checkpoint_epo50_eps099.pth")
ge.ai_1.trainer.load("trained_wder/fc_self_play_br/g070_40s/agent1/checkpoint_epo50_eps099.pth")
# ge.ai_1.trainer.load("trained_wder/rnn_self_play_dr/g070/agent2/checkpoint_epo50_eps099.pth")
# ge.ai_1.trainer.load("trained_wder/fc/g070/checkpoint_epo50_eps099.pth")
# ge.ai_1.trainer.load("trained_wd/fc_self_play_2nd/050/checkpoint_epo50_eps100.pth")
ge.ai_1.trainer.epsilon = 0
ge.ai_2.trainer.load("trained_wder/fc_self_play/g070/agent2/checkpoint_epo50_eps099.pth")
# ge.ai_2.trainer.load("trained_wd/fc_self_play/agent1/checkpoint_epo50_eps100.pth")
# ge.ai_2.trainer.load("trained/fc/checkpoint_epo50_eps010.pth")
ge.ai_2.trainer.epsilon = 0

testing = True

while not stop:
    winner, curr_score, first_scores = ge.game_loop()
    if winner != 0:
        games += 1
        # if ge.ai_1.trainer.epsilon > 0.1:
        #     ge.ai_1.trainer.update_epsilon(0.9999)
        #     ge.ai_2.trainer.update_epsilon(0.9999)

        # erb's training (experience relay buffer)
        if games % 100 == 0:
            if ge.ai_1.trainer.epsilon > 0.1:
                ge.ai_1.trainer.update_epsilon(0.99)
                ge.ai_1.trainer.train_er()
                ge.ai_2.trainer.update_epsilon(0.99)
                ge.ai_2.trainer.train_er()

        # add win
        if winner == 3:
            wins[0] += 1
            wins[1] += 1
        else:
            wins[winner - 1] += 1

        # p1 wins 100
        if winner == 1 or winner == 3:
            target_wins_100.append(1)
        else:
            target_wins_100.append(0)
        if games > 100 + resume:
            target_wins_100.popleft()

        # calc first score stat
        fs_chance_1 += first_scores[0] / curr_score[0] if curr_score[0] > 0 else 0
        fs_chance_2 += first_scores[1] / curr_score[1] if curr_score[1] > 0 else 0

        # if (verbose):
        print(f"Games: {games} | Winner : AI {winner} | Score : {curr_score} | Wins: {wins} | WR in 100: {sum(target_wins_100) / 100} | Eps: {ge.ai_1.trainer.epsilon}")
        # print(ge.curr_agent_id)
    # if games % 1000 == 0:
    #     ge.ai_1.trainer.save(1, games, 1000)
        # ge.ai_2.trainer.save(2, games, 1000)
    if games >= total_games:
        fs_chance_1 = fs_chance_1 / total_games
        fs_chance_2 = fs_chance_2 / total_games
        print(f"Total Wins: {wins}")
        if testing:
            print(f"AI 1 Move Freq: {ge.ai_1.move_freq}")
            print(f"AI 2 Move Freq: {ge.ai_2.move_freq}")
            
            print(f"AI 1 Begin Freq: {ge.ai_1.begin_freq}")
            print(f"AI 2 Begin Freq: {ge.ai_2.begin_freq}")

            print(f"\nWinrate: {round((wins[0] / total_games) * 100, 1)}%\n")

            print(f"AI 1 First Score Chance: {round(fs_chance_1 * 100, 1)}%")
            print(f"AI 2 First Score Chance: {round(fs_chance_2 * 100, 1)}%\n")

            mf1 = avg_sort(ge.ai_1.move_freq)
            print(f"Most abused moves are:")
            for (index, (key, value)) in enumerate(mf1.items()):
                print(f"{index+1}. {key} ({round(value, 3)})")

            print()

            bf1 = avg_sort(ge.ai_1.begin_freq)
            print(f"Most abused openers in general are:")
            for (index, (key, value)) in enumerate(bf1.items()):
                print(f"{index+1}. {key} ({round(value, 3)})")

            print()

            mbf1 = rel_sort(ge.ai_1.move_freq, ge.ai_1.begin_freq)
            print(f"Most abused openers relative to its uses:")
            for (index, (key, value)) in enumerate(mbf1.items()):
                print(f"{index+1}. {key} ({round(value, 3)})")
        stop = True
