import random
import numpy as np

import utils as U

from collections import deque

from action import *
from card_engine import *

# ai engine class

ACTIONS_MAX = 6

class AI_Engine():
    def __init__(self) -> None:
        self.card_engine = Card_Engine()

        self.is_ai_done = False
        
        self.available_slots = ACTIONS_MAX

        self.past_actions = []
        self.curr_actions = []
        self.futr_actions = []

        # hyperparameters

        # self.TURN_MEMORY = 1

        # memory

        # pre-processing
        # self.has_preprocessed = False
        # self.opp_past_actions = {}
        self.opp_past_actions = []
        # self.game_count = 1
        self.curr_deck = deque()

        self.old_state = None
        self.state = None

        self.total_moves = 0

        # guess stuff
        # self.opp_past_moves = {}
        # self.guess_index = 0

        # rewards
        self.rewards = [0] * 6

    def reset(self) -> None:
        self.reset_memory()
        self.card_engine.reset()

    def start(self) -> None:
        self.card_engine.start(U.ALL_MOVES)

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
    
    def reset_turn(self) -> None:
        # on score etc...
        self.available_slots = ACTIONS_MAX
        # pre-processing
        # self.game_count += 1
        # guess
        # self.guess_index = 0
        self.reset_actions()
    
    def reset_actions(self) -> None:
        self.is_ai_done = False
        # self.has_preprocessed = False
        self.past_actions = self.curr_actions
        self.curr_actions = self.futr_actions
        self.futr_actions = []
    
    def reset_memory(self) -> None:
        # pre-processing
        # self.has_preprocessed = False
        # self.opp_past_actions = {}
        self.opp_past_actions = []
        # self.game_count = 1
        self.curr_deck = deque()
        # guess
        # self.opp_past_moves = {}
        # self.guess_index = 0

        hand = [move.id for move in self.card_engine.hand]
        self.state = [*hand, -1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, self.total_moves, 0, 0, 0, 0, 0, 0]

    def update_rewards(self, opp: int, ai: int, action: int) -> None:
        # no one win = 0, opp win = -10, ai win = 10, tie = 10
        self.rewards[action - 1] = (ai - opp) * 10 + (ai * opp * 10)

    # decision stuff

    def debug_decision(self) -> list[Action]:
        return [Charge(), Charge(), Charge(), Push(), Smash(), Blank()]

    def decision(self, mat_pos_1: int, mat_pos_2: int, opp_past_actions: list[Action], player_score: int, agent_score: int) -> list[Action]:
        # print(self.card_engine.deck)
        print(f"p_pos: {mat_pos_1} | a_pos: {mat_pos_2} | p_past: {opp_past_actions} | score: {player_score} : {agent_score}")

        # pre processing
        # if not self.has_preprocessed:
        #     self.append_opp_past_actions(mat_pos_1, mat_pos_2, opp_past_actions, player_score, agent_score)
        #     self.has_preprocessed = True

        # print(f"opp_past_actions: {self.opp_past_actions}")
        # print(f"agent state: {self.state}")
        # print(f"opp_past_moves: {self.opp_past_moves}")

        # move selection
        self.move_selection()
        self.total_moves += 1
        print(f"AI Done: {self.is_ai_done}")
        if self.is_ai_done:
            result = self.curr_actions
            self.reset_actions()
            print(f"AI Curr: {result} | AI Fut: {self.curr_actions} | AI Fut2: {self.futr_actions}")
            return result
        else:
            return self.decision(mat_pos_1, mat_pos_2, opp_past_actions, player_score, agent_score)
    

    def set_states(self, mat_pos_1: int, mat_pos_2: int, opp_past_actions: list[Action], player_score: int, agent_score: int, turn: int) -> bool:
        if len(opp_past_actions) == 6:
            self.old_state = self.state
            if len(self.opp_past_actions) >= U.ACTIONS_MAX:
                self.opp_past_actions = self.opp_past_actions[U.ACTIONS_MAX:]
            self.opp_past_actions.extend(opp_past_actions)
            self.get_states(mat_pos_1, mat_pos_2, player_score, agent_score, turn)
            self.total_moves = 0
            # no need to guess for now
            # found = True
            # while found:
            #     found = self.guess_opp_moves()

    def get_states(self, mat_pos_1: int, mat_pos_2: int, player_score: int, agent_score: int, turn: int) -> None:
        # convert to numeric so that the actions are stored much better in memory
        opp_actions = self.actions_to_numeric(self.opp_past_actions)
        hand = [move.id for move in self.card_engine.hand]
        # at this point, curr_actions = future actions, and past_actions = current actions because this is checked after reset
        curr_actions = self.actions_to_numeric(self.past_actions)
        futr_actions = self.actions_to_numeric(self.curr_actions)
        self.state = [*hand, mat_pos_1, mat_pos_2, *opp_actions, *curr_actions, *futr_actions, player_score, agent_score, turn, self.total_moves]
        self.state = np.array(self.state, dtype=int)
    
    def actions_to_numeric(self, actions: list[Action]) -> list[int]:
        actions_num = [0] * U.ACTIONS_MAX

        for i, action in enumerate(actions):
            numeric = 0
            match action:
                case Hit():
                    numeric = 1
                case Smash():
                    numeric = 2
                case Block():
                    numeric = 3
                case Stance():
                    numeric = 4
                case Blank():
                    numeric = 5
                case Charge():
                    numeric = 6
                case Push():
                    numeric = 7
                case Forwards():
                    numeric = 8
                case Backwards():
                    numeric = 9
            actions_num[i] = numeric
        return actions_num

    
    # decision logic
    
    def move_selection(self) -> None:
        if self.available_slots <= 0:
            self.available_slots = ACTIONS_MAX + self.available_slots
            self.ai_done()
        else:
            move = self.card_engine.play_move(int(random.random() * 4))
            self.append_actions(move)
            self.update_slots(move)
            self.remember_move(move)
            # print(self.card_engine.deck)                  # by 4 moves it should know exactly the order of its deck
            print(self.curr_deck)
    
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