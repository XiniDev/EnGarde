import random
import numpy as np

import copy

import utils as U

from collections import deque

from action import *
from card_engine import *

import dqn as dqn

# ai engine class

ACTIONS_MAX = 6

class AI_Engine():
    def __init__(self) -> None:
        self.card_engine = Card_Engine(no_shuffle=False)

        self.is_ai_done = False
        
        self.available_slots = ACTIONS_MAX

        self.past_actions = []
        self.curr_actions = []
        self.futr_actions = []

        # memory

        self.reward = 0
        self.old_state = None
        self.state = None

        self.move_selected = -1


    def reset(self) -> None:
        self.card_engine.reset()
        self.reset_memory()

    def start(self) -> None:
        self.card_engine.start(U.ALL_MOVES)
    
    def reset_turn(self) -> None:
        # on score etc...
        self.available_slots = ACTIONS_MAX
        self.reset_actions()
    
    def reset_actions(self) -> None:
        self.is_ai_done = False
        self.past_actions = self.curr_actions
        self.curr_actions = self.futr_actions
        self.futr_actions = []

    # decision stuff

    def debug_decision(self) -> list[Action]:
        return [Charge(), Charge(), Charge(), Push(), Smash(), Blank()]

    def decision(self, mat_pos: list[int], opp_past_actions: list[Action], scores: list[int], turn: int) -> list[Action]:
        # print(self.card_engine.deck)
        print(f"p_pos: {mat_pos[0]} | a_pos: {mat_pos[1]} | p_past: {opp_past_actions} | score: {scores[0]} : {scores[1]}")

        # move selection (returns the id of the move)
        self.move_selected = self.move_selection()
        print(f"AI Done: {self.is_ai_done}")
        if self.is_ai_done:
            result = self.curr_actions
            self.reset_actions()
            print(f"AI Curr: {result} | AI Fut: {self.curr_actions} | AI Fut2: {self.futr_actions}")
            return result
        else:
            self.set_memory(0, mat_pos, opp_past_actions)
            return self.decision(mat_pos, opp_past_actions, scores, turn)
        

    def get_state(self, mat_pos: list[int], opp_past_actions: list[Action]) -> list[int]:
        # sorted hand so same hand of different order literally means the same thing to the agent, then convert to binary so its easily differentiable for the agent
        hand = sorted([move.id - 1 for move in self.card_engine.hand])
        bin_hand = U.convert_binary(hand, 3)

        # convert mat positions to binary
        bin_mat_pos = U.convert_binary([p+4 for p in mat_pos], 3)

        # convert to numeric so that the actions are stored much better in memory, then convert them to binary
        opp_actions = self.actions_to_numeric(opp_past_actions)
        bin_o_actions = U.convert_binary(opp_actions, 4)

        # here, self.curr_actions = future actions, and self.past_actions = current actions, because this is checked after reset
        # convert to numeric for memory reasons, then convert them to binary
        curr_actions = self.actions_to_numeric(self.past_actions)
        bin_c_actions = U.convert_binary(curr_actions, 4)

        # not sure if keeping futr actions
        # futr_actions = self.actions_to_numeric(self.curr_actions)
        # bin_f_actions = U.convert_binary(futr_actions, 4)

        # , *futr_actions, *scores, turn, self.total_moves???
        return [*bin_hand, *bin_mat_pos, *bin_o_actions, *bin_c_actions]
    
    def actions_to_numeric(self, actions: list[Action]) -> list[int]:
        actions_num = [0] * U.ACTIONS_MAX

        # ensures there are 6 actions
        for i, action in enumerate(actions):
            actions_num[i] = U.action_to_numeric(action)
        return actions_num
    
    def get_reward(self, reward_score: int) -> int:
        reward = reward_score
        return reward

    
    # decision logic
    
    def move_selection(self) -> int:
        if self.available_slots <= 0:
            self.available_slots = ACTIONS_MAX + self.available_slots
            self.ai_done()
            res = 0
        else:
            move = self.card_engine.play_move(self.get_action())
            self.append_actions(move)
            self.update_slots(move)
            # print(self.card_engine.deck)                  # by 4 moves it should know exactly the order of its deck
            res = move.id
        return res
    
    def get_action(self) -> int:
        hand = [move.id for move in self.card_engine.hand]
        move = self.trainer.predict(self.state, hand)
        return move
        # return int(random.random() * 4)

    def append_actions(self, move: Move) -> None:
        value = ACTIONS_MAX - len(self.curr_actions)
        split = move.split(value)
        self.curr_actions.extend(split[0])
        self.futr_actions.extend(split[1])

    def update_slots(self, move: Move) -> None:
        if move.slots >= self.available_slots:
            self.available_slots = ACTIONS_MAX - (move.slots - self.available_slots)
            self.ai_done()
        else:
            self.available_slots = self.available_slots - move.slots
    
    def ai_done(self) -> None:
        self.is_ai_done = True


# basic Linear fc for DQN
class Linear_AI_Engine(AI_Engine):
    def __init__(self, ai_path: str) -> None:
        super().__init__()

        self.ai_path = ai_path

        self.reward = 0
        self.old_state = None
        self.state = None

        self.old_hand = None

        self.model = dqn.LinearQNetwork(66, 256, 8)
        self.trainer = dqn.LinearTrainer(self.model, 0.001, 0.7, 1.0)

    def set_memory(self, reward_score: int, mat_pos: list[int], opp_past_actions: list[Action]) -> None:
        opp_actions = opp_past_actions
        if len(opp_past_actions) == 0:
            opp_actions = [0] * U.ACTIONS_MAX

        self.old_state = self.state
        self.state = self.get_state(mat_pos, opp_actions)
        self.state = np.array(self.state, dtype=int)
        
        self.reward = self.get_reward(reward_score)

        # print(f"agent move: {self.move_selected} | agent state: {self.state}")

        state = self.old_state
        action = self.move_selected - 1
        reward = self.reward
        new_state = self.state

        self.trainer.memorise(state, action, reward, new_state, self.old_hand)
        # print(self.trainer.model)

        self.old_hand = sorted([move.id - 1 for move in self.card_engine.hand])

    def reset_memory(self) -> None:

        self.trainer.load(self.ai_path)

        hand = sorted([move.id - 1 for move in self.card_engine.hand])
        bin_hand = U.convert_binary(hand, 3)

        mat_pos = [-1, 1]
        bin_mat_pos = U.convert_binary([p+4 for p in mat_pos], 3)

        bin_o_actions = bin_c_actions = [0, 0, 0, 0] * 6

        # self.state = [*hand, *mat_pos, *opp_actions, *curr_actions, *futr_actions]
        self.state = [*bin_hand, *bin_mat_pos, *bin_o_actions, *bin_c_actions]
        self.state = np.array(self.state, dtype=int)

        self.old_hand = hand

    def get_action(self) -> int:
        hand = [move.id for move in self.card_engine.hand]
        move = self.trainer.predict(self.state, hand)
        return move
        # return int(random.random() * 4)

# RNN for DQN
class RNN_AI_Engine(AI_Engine):
    def __init__(self, ai_path: str) -> None:
        super().__init__()

        self.ai_path = ai_path

        self.reward = 0
        self.old_state = None
        self.state = None

        self.old_hand = None

        self.sequence_length = 5

        self.model = dqn.RNNQNetwork(66, 256, 8)
        self.trainer = dqn.RNNTrainer(self.model, 0.001, 0.7, 1.0)

    def set_memory(self, reward_score: int, mat_pos: list[int], opp_past_actions: list[Action]) -> None:
        opp_actions = opp_past_actions
        if len(opp_past_actions) == 0:
            opp_actions = [0] * U.ACTIONS_MAX

        self.old_state = copy.deepcopy(self.state)
        state = self.get_state(mat_pos, opp_actions)
        self.state = np.roll(self.state, -1, axis=0)
        self.state[-1, :] = state
        
        self.reward = self.get_reward(reward_score)

        # print(f"agent move: {self.move_selected} | agent state: {self.state}")

        state = self.old_state
        action = self.move_selected - 1
        reward = self.reward
        new_state = self.state

        self.trainer.memorise(state, action, reward, new_state, self.old_hand)
        # print(self.trainer.model)

        self.old_hand = sorted([move.id - 1 for move in self.card_engine.hand])

    def reset_memory(self) -> None:

        self.trainer.load(self.ai_path)

        hand = sorted([move.id - 1 for move in self.card_engine.hand])
        bin_hand = U.convert_binary(hand, 3)

        mat_pos = [-1, 1]
        bin_mat_pos = U.convert_binary([p+4 for p in mat_pos], 3)

        bin_o_actions = bin_c_actions = [0, 0, 0, 0] * 6

        # self.state = [*hand, *mat_pos, *opp_actions, *curr_actions, *futr_actions]
        state = [*bin_hand, *bin_mat_pos, *bin_o_actions, *bin_c_actions]
        self.state = np.zeros((self.sequence_length, 66))
        # print(self.card_engine.hand)
        # print(len(bin_hand), len(bin_mat_pos), len(bin_o_actions), len(bin_c_actions))
        self.state[-1, :] = state

        self.old_hand = hand

    def get_action(self) -> int:
        hand = [move.id for move in self.card_engine.hand]
        move = self.trainer.predict(self.state, hand)
        return move
        # return int(random.random() * 4)