import random

import utils as U

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

    def reset(self) -> None:
        self.card_engine.reset()

    def start(self) -> None:
        self.card_engine.start(U.ALL_MOVES)
    
    def move_selection(self) -> None:
        if self.available_slots <= 0:
            self.available_slots = ACTIONS_MAX + self.available_slots
            self.ai_done()
        else:
            move = self.card_engine.play_move(int(random.random() * 4))
            self.append_actions(move)
            self.run_turn(move)

    def append_actions(self, move: Move) -> None:
        value = ACTIONS_MAX - len(self.curr_actions)
        split = move.split(value)
        self.curr_actions.extend(split[0])
        self.futr_actions.extend(split[1])

    def run_turn(self, move: Move) -> None:
        if move.slots >= self.available_slots:
            self.available_slots = ACTIONS_MAX - (move.slots - self.available_slots)
            self.ai_done()
        else:
            self.available_slots = self.available_slots - move.slots

    def decision(self, mat_pos_1: int, mat_pos_2: int, opp_past_actions: list[Action]) -> list[Action]:
        # print(self.card_engine.deck)
        print(f"p_pos: {mat_pos_1} | a_pos: {mat_pos_2} | p_past: {opp_past_actions}")
        self.move_selection()
        print(f"AI Done: {self.is_ai_done}")
        if self.is_ai_done:
            result = self.curr_actions
            self.reset_actions()
            print(f"AI Curr: {result} | AI Fut: {self.curr_actions} | AI Fut2: {self.futr_actions}")
            return result
        else:
            return self.decision(mat_pos_1, mat_pos_2, opp_past_actions)
    
    def ai_done(self) -> None:
        self.is_ai_done = True
    
    def reset_turn(self) -> None:
        self.available_slots = ACTIONS_MAX
        self.reset_actions()
    
    def reset_actions(self) -> None:
        self.is_ai_done = False
        self.curr_actions = self.futr_actions
        self.futr_actions = []

    def debug_decision(self) -> list[Action]:
        return [Block(), Block(), Block(), Block(), Block(), Block()]