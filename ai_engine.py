import random

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

        self.curr_actions = []
        self.futr_actions = []

        # hyperparameters

        self.TURN_MEMORY = 4

        # memory

        self.has_preprocessed = False
        self.opp_past_actions = {}
        self.opp_past_moves = {}
        self.game_count = 1
        self.guess_index = 0
        self.curr_deck = deque()

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
        self.available_slots = ACTIONS_MAX
        self.game_count += 1
        self.guess_index = 0
        self.reset_actions()
    
    def reset_actions(self) -> None:
        self.is_ai_done = False
        self.has_preprocessed = False
        self.curr_actions = self.futr_actions
        self.futr_actions = []
    
    def reset_memory(self) -> None:
        self.has_preprocessed = False
        self.opp_past_actions = {}
        self.opp_past_moves = {}
        self.game_count = 1
        self.guess_index = 0
        self.curr_deck = deque()

    # decision stuff

    def debug_decision(self) -> list[Action]:
        return [Block(), Block(), Block(), Block(), Block(), Block()]

    def decision(self, mat_pos_1: int, mat_pos_2: int, opp_past_actions: list[Action]) -> list[Action]:
        # print(self.card_engine.deck)
        print(f"p_pos: {mat_pos_1} | a_pos: {mat_pos_2} | p_past: {opp_past_actions}")

        # pre processing
        if not self.has_preprocessed:
            self.append_opp_past_actions(opp_past_actions)
            self.has_preprocessed = True

        print(f"opp_past_actions: {self.opp_past_actions}")
        print(f"opp_past_moves: {self.opp_past_moves}")

        # move selection
        self.move_selection()
        print(f"AI Done: {self.is_ai_done}")
        if self.is_ai_done:
            result = self.curr_actions
            self.reset_actions()
            print(f"AI Curr: {result} | AI Fut: {self.curr_actions} | AI Fut2: {self.futr_actions}")
            return result
        else:
            return self.decision(mat_pos_1, mat_pos_2, opp_past_actions)
    
    # pre processing

    def append_opp_past_actions(self, opp_past_actions: list[Action]) -> bool:
        if len(opp_past_actions) == 6:
            if len(self.opp_past_actions) >= self.TURN_MEMORY:
                self.opp_past_actions.pop(self.game_count - self.TURN_MEMORY, None)
            if not self.opp_past_actions.get(self.game_count):
                self.opp_past_actions[self.game_count] = []
            self.opp_past_actions[self.game_count].extend(opp_past_actions)
            found = True
            while found:
                found = self.guess_opp_moves()
    
    def guess_opp_moves(self) -> bool:
        if len(self.opp_past_moves) >= self.TURN_MEMORY:
            self.opp_past_moves.pop(self.game_count - self.TURN_MEMORY, None)
        if not self.opp_past_moves.get(self.game_count):
            self.opp_past_moves[self.game_count] = []
        guess_range = len(self.opp_past_actions[self.game_count])
        for i in range(guess_range):
            l = guess_range - i
            if self.guess_index >= l:
                return False
            check = self.opp_past_actions[self.game_count][self.guess_index:l]
            for k, v in U.ALL_MOVES.items():
                print(check)
                print(v)
                if tuple(check) == v:
                    self.opp_past_moves[self.game_count].append(k)
                    self.guess_index += len(v)
                    return True
        return False

    
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
            # print(self.curr_deck)
    
    # post processing

    def remember_move(self, move: Move) -> None:
        if len(self.curr_deck) >= self.card_engine.DECK_MAX - self.card_engine.HAND_MAX:
            self.curr_deck.popleft()
        self.curr_deck.append(move)