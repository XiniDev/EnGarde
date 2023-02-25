import random
import numpy as np

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

        # hyperparameters

        # self.TURN_MEMORY = 1

        # pre-processing
        self.curr_deck = deque()

        # memory

        self.old_hand = None

        self.old_state = None
        self.state = None

        self.move_selected = -1

        self.scores = [0, 0]

        # rewards
        self.reward = 0

        # deep q network
        self.model = dqn.LinearQNetwork(66, 256, 8)
        self.trainer = dqn.Trainer(self.model, 0.001, 0.9, 0.0)

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
    
    def reset_memory(self) -> None:

        self.trainer.load("trained/fc_newer/checkpoint_epo50_eps010.pth")

        # pre-processing
        self.curr_deck = deque()

        hand = sorted([move.id - 1 for move in self.card_engine.hand])
        bin_hand = U.convert_binary(hand, 3)

        mat_pos = [-1, 1]
        bin_mat_pos = U.convert_binary([p+4 for p in mat_pos], 3)

        # opp_actions = curr_actions = futr_actions = [0, 0, 0, 0, 0, 0]
        bin_o_actions = bin_c_actions = [0, 0, 0, 0] * 6

        self.scores = [0, 0]
        turn = 1

        # self.state = [*hand, *mat_pos, *opp_actions, *curr_actions, *futr_actions]
        self.state = [*bin_hand, *bin_mat_pos, *bin_o_actions, *bin_c_actions]
        self.state = np.array(self.state, dtype=int)

        self.old_hand = hand

    # def update_rewards(self, opp: int, ai: int, action: int) -> None:
    #     # no one win = 0, opp win = -10, ai win = 10, tie = 10
    #     self.rewards[action - 1] = (ai - opp) * 10 + (ai * opp * 10)

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
            self.set_memory(0, mat_pos, opp_past_actions, scores, turn)
            return self.decision(mat_pos, opp_past_actions, scores, turn)

    def set_memory(self, reward_score: int, mat_pos: list[int], opp_past_actions: list[Action], scores: list[int], turn: int) -> None:
        opp_actions = opp_past_actions
        if len(opp_past_actions) == 0:
            opp_actions = [0] * U.ACTIONS_MAX

        self.old_state = self.state
        self.state = self.get_state(mat_pos, opp_actions, scores, turn)
        self.state = np.array(self.state, dtype=int)

        self.scores = scores
        
        self.reward = self.get_reward(reward_score)

        # print(f"agent move: {self.move_selected} | agent state: {self.state}")

        state = self.old_state
        action = self.move_selected - 1
        reward = self.reward
        new_state = self.state

        self.trainer.train(state, action, reward, new_state, self.old_hand)
        # print(self.trainer.model)

        self.old_hand = sorted([move.id - 1 for move in self.card_engine.hand])
        

    def get_state(self, mat_pos: list[int], opp_past_actions: list[Action], scores: list[int], turn: int) -> list[int]:
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
            self.remember_move(move)
            # print(self.card_engine.deck)                  # by 4 moves it should know exactly the order of its deck
            print(self.curr_deck)
            res = move.id
        return res
    
    def get_action(self) -> int:
        # p1 = self.scores[0]
        # p2 = self.scores[1]
        # self.epsilon = 0.9 - 0.02 * ((p1 + p2) * 2 - (p2 - p1))

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
    
    # post processing

    def remember_move(self, move: Move) -> None:
        if len(self.curr_deck) >= self.card_engine.DECK_MAX - self.card_engine.HAND_MAX:
            self.curr_deck.popleft()
        self.curr_deck.append(move)




    # extra stuff
    # potential pre processing

    # def append_opp_past_actions(self, mat_pos_1: int, mat_pos_2: int, opp_past_actions: list[Action]) -> bool:
    #     if len(opp_past_actions) == 6:
    #         if len(self.opp_past_actions) >= self.TURN_MEMORY:
    #             self.opp_past_actions.pop(self.game_count - self.TURN_MEMORY, None)
    #         if not self.opp_past_actions.get(self.game_count):
    #             self.opp_past_actions[self.game_count] = []
    #         self.opp_past_actions[self.game_count].extend(opp_past_actions)
    #         print(mat_pos_1, mat_pos_2)
    #         # self.get_states(mat_pos_1, mat_pos_2)
    #         # no need to guess for now
    #         # found = True
    #         # while found:
    #         #     found = self.guess_opp_moves()
    
    # def guess_opp_moves(self) -> bool:
    #     if len(self.opp_past_moves) >= self.TURN_MEMORY:
    #         self.opp_past_moves.pop(self.game_count - self.TURN_MEMORY, None)
    #     if not self.opp_past_moves.get(self.game_count):
    #         self.opp_past_moves[self.game_count] = []
    #     guess_range = len(self.opp_past_actions[self.game_count])
    #     for i in range(guess_range):
    #         l = guess_range - i
    #         if self.guess_index >= l:
    #             return False
    #         check = self.opp_past_actions[self.game_count][self.guess_index:l]
    #         for id, (n, a) in U.ALL_MOVES.items():
    #             # print(check)
    #             # print(v)
    #             if tuple(check) == a:
    #                 self.opp_past_moves[self.game_count].append(id)
    #                 self.guess_index += len(a)
    #                 return True
    #     return False