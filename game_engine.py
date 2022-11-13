import pygame

import utils as U
import network as network
import action_logic as al

from action import *
from card_engine import *
from player import *
from ai_engine import *

# game engine class

ACTIONS_MAX = 6
ANIMATION_FRAMES = 20

class Game_Engine():
    def __init__(self) -> None:
        self.is_sp = None                      # determines if the game is singleplayer or multiplayer

        self.player = [Player(True), Player(False)]

        self.ai = None

        self.score = [0, 0]

        self.turn = 1                           # turn variable (indicates which turn the game is on right now)
        self.action = 1                         # action variable (indicates which action slot the game is on right now)
        self.frames = -1                        # test for future animation frames temp variable basically

        self.is_user_done = False               # has user committed their actions
        self.running_turn = False               # run turn variable

        self.available_slots = ACTIONS_MAX

        self.past_actions = []
        self.curr_actions = []
        self.futr_actions = []

        self.opp_actions = []
        self.opp_actions_past = []

        # states variables
        self.distance = self.player[1].mat_pos - self.player[0].mat_pos - 1
    
    def update(self, win: pygame.Surface) -> None:
        self.display_score(win)
        self.display_turn(win)
        self.display_actions(win)
        self.resolve_turn()
        self.player[0].update(win)
        self.player[1].update(win)
    
    def reset(self) -> None:
        self.score = [0, 0]
        self.reset_turn()
        if self.is_sp:
            self.ai.reset()
    
    def set_ai(self) -> None:
        self.ai = AI_Engine() if self.is_sp else None
        if self.is_sp:
            self.ai.start()
    
    def set_sp(self, is_sp: bool) -> None:
        self.is_sp = is_sp
        self.set_ai()

    def send_data(self) -> str:
        data = ','.join([i.symbol for i in self.curr_actions]) + ';' + ','.join([i.symbol for i in self.past_actions])
        return network.send(data)

    def parse_data(self, data: str) -> tuple[list[Action]]:
        try:
            parsed = data.split(';')
            curr, past = parsed[0].split(','), parsed(';')[1].split(',')
            return curr, past
        except:
            return [Blank()] * 6, [Blank()] * 6
    
    def display_score(self, win: pygame.Surface) -> None:
        score = pygame.font.SysFont('Comic Sans MS', 30).render(str(self.score[0]) + " : " + str(self.score[1]), False, (255, 255, 255))
        win.blit(score, score.get_rect(center = (U.X_CENTER, 30)))

    def display_turn(self, win: pygame.Surface) -> None:
        win.blit(pygame.font.SysFont('Comic Sans MS', 30).render("Turn " + str(self.turn), False, (255, 255, 255)), (0, 0))

    def display_actions(self, win: pygame.Surface) -> None:
        # actions holder
        pygame.draw.rect(win, (128, 128, 128), (U.X_CENTER - 600, 50, 300, 50))
        pygame.draw.rect(win, (128, 128, 128), (U.X_CENTER + 300, 50, 300, 50))

        # action holder
        pygame.draw.rect(win, (200, 0, 0), (U.X_CENTER - 600 + 50 * (self.action - 1), 50, 50, 50))
        pygame.draw.rect(win, (200, 0, 0), (U.X_CENTER + 300 + 50 * (self.action - 1), 50, 50, 50))

        # action symbols
        for index, action in enumerate(self.curr_actions):
            win.blit(pygame.font.SysFont('Comic Sans MS', 30).render(action.symbol, False, (255, 255, 255)), (U.X_CENTER - 600 + 50 * index + 15, 50))
        for index, action in enumerate(self.past_actions):
            win.blit(pygame.font.SysFont('Comic Sans MS', 30).render(action.symbol, False, (255, 255, 255)), (U.X_CENTER - 600 + 50 * index + 15, 100))
        
        # opponent action symbols
        for index, action in enumerate(self.opp_actions):
            win.blit(pygame.font.SysFont('Comic Sans MS', 30).render(action.symbol, False, (255, 255, 255)), (U.X_CENTER + 300 + 50 * index + 15, 50))
        for index, action in enumerate(self.opp_actions_past):
            win.blit(pygame.font.SysFont('Comic Sans MS', 30).render(action.symbol, False, (255, 255, 255)), (U.X_CENTER + 300 + 50 * index + 15, 100))
    
    def resolve_turn(self) -> None:
        self.update_distance()
        print(network.client)
        if self.running_turn:
            if self.frames == ANIMATION_FRAMES:
                self.out_detection()
                self.frames = -1
                self.next_action()
            elif self.frames == -1:
                self.frames += 1
                self.check_action()
            else:
                self.frames += 1
                self.resolve_action()
        elif self.is_user_done:
            if self.is_sp:
                # run AI
                self.opp_actions = self.ai.decision(self.player[0].mat_pos, self.player[1].mat_pos, self.past_actions)
                # self.opp_actions = self.ai.debug_decision()
                self.running_turn = True
            else:
                # recieve connection signal (if recieve signal -> self.running_turn = True)
                # send curr actions to run on other screen, send past actions to display what they have done previously
                self.opp_actions, self.opp_actions_past = self.parse_data(self.send_data())
                self.running_turn = True
    
    def is_turn_running(self) -> bool:
        return self.running_turn
    
    def move_selection(self, card_engine: Card_Engine) -> None:
        if self.available_slots <= 0:
            self.available_slots = ACTIONS_MAX + self.available_slots
            self.user_done()
        else:
            for i in range(card_engine.HAND_MAX):
                if card_engine.cards[i].collidepoint(pygame.mouse.get_pos()):
                    move = card_engine.play_move(i)
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
            self.user_done()
        else:
            self.available_slots = self.available_slots - move.slots

    def user_done(self) -> None:
        self.is_user_done = True

    def update_distance(self) -> None:
        self.distance = self.player[1].mat_pos - self.player[0].mat_pos - 1
    
    def out_detection(self) -> None:
        piste_length = U.PISTE_LENGTH
        score = [0, 0]
        for i in range(2):
            if self.player[i].mat_pos > (piste_length - 1) / 2 or self.player[i].mat_pos < -1 * (piste_length - 1) / 2:
                score[i] = 1
                self.scored(score[1], score[0])

    def next_action(self) -> None:
        print(f"Turn: {self.turn} | Action: {self.action}")
        if self.action < ACTIONS_MAX:
            self.action += 1
        else:
            self.action = 1
            self.next_turn()
    
    def next_turn(self) -> None:
        self.turn += 1
        self.reset_actions()
    
    def reset_actions(self) -> None:
        self.is_user_done = False
        self.running_turn = False
        self.past_actions = self.curr_actions
        self.curr_actions = self.futr_actions
        self.futr_actions = []
        self.opp_actions_past = self.opp_actions
        self.opp_actions = []
    
    def check_action(self) -> None:
        a_1 = self.curr_actions[self.action - 1]
        a_2 = self.opp_actions[self.action - 1]
        al.compute(a_1, a_2, self.distance)
        states_1 = {**al.states[0], **{'mat_pos': self.player[0].mat_pos}}
        states_2 = {**al.states[1], **{'mat_pos': self.player[1].mat_pos}}
        print(f"User: {a_1} ; {states_1} | Opp: {a_2} ; {states_2} | Distance: {self.distance}")

    def resolve_action(self) -> None:
        # user_action = self.curr_actions[self.action - 1]
        # opp_action = self.opp_actions[self.action - 1]
        # self.resolve_match(user_action, 0)
        # self.resolve_match(opp_action, 1)
        self.resolve_movement()
        self.resolve_score()

    # def resolve_match(self, action: Action, pid: int) -> None:
    #     # ACTION_SYMBOLS = ['x', 'X', 'b', 'B', '_', '-', '=', '>', '<']
    #     # priority is < then B then b then X then x then = then > then - then _
    #     # still need to figure out whats the best way to code this :(
    #     match action:
    #         case Hit():
    #             self.resolve_hit(action, pid)
    #         case Smash():
    #             self.resolve_smash(action, pid)
    #         case Block():
    #             self.resolve_block(action, pid)
    #         case Stance():
    #             self.resolve_stance(action, pid)
    #         case Blank():
    #             self.resolve_blank(action, pid)
    #         case Charge():
    #             self.resolve_charge(action, pid)
    #         case Push():
    #             self.resolve_push(action, pid)
    #         case Forwards():
    #             self.resolve_forwards(action, pid)
    #         case Backwards():
    #             self.resolve_backwards(action, pid)
    
    def resolve_movement(self) -> None:
        for i in range(2):
            self.player[i].pos_update(al.states[i]['move'], self.frames, ANIMATION_FRAMES)
            if al.states[i]['push'] == 1:
                if self.distance == 0:
                    self.player[i * -1 + 1].pos_update(-1, self.frames, ANIMATION_FRAMES)

    def resolve_score(self) -> None:  # thnk of something better HERE
        if self.frames == 20:
            if al.states[0]['score'] == 1 or al.states[1]['score'] == 1:
                self.scored(al.states[0]['score'], al.states[1]['score'])
    
    # def resolve_hit(self, action: Action, pid: int) -> None:
    #     self.reset_charge(pid)
    #     if self.frames == 20:
    #         if action.state['score']:
    #             self.scored(pid)

    # def resolve_smash(self, action: Action, pid: int) -> None:
    #     if action.state['move']:
    #         self.player[pid].pos_update(1, self.frames, ANIMATION_FRAMES)
    #     if action.state['push']:
    #         self.player[pid * -1 + 1].pos_update(-1, self.frames, ANIMATION_FRAMES)
    #     if self.frames == 20:
    #         self.reset_charge(pid)
    #         if action.state['score']:
    #             self.scored(pid)

    # def resolve_block(self, action: Action, pid: int) -> None:
    #     pass

    # def resolve_stance(self, action: Action, pid: int) -> None:
    #     pass

    # def resolve_blank(self, action: Action, pid: int) -> None:
    #     pass

    # def resolve_charge(self, action: Action, pid: int) -> None:
    #     pass

    # def resolve_push(self, action: Action, pid: int) -> None:
    #     if action.state['move']:
    #         self.player[pid].pos_update(1, self.frames, ANIMATION_FRAMES)
    #     if action.state['push']:
    #         self.player[pid * -1 + 1].pos_update(-1, self.frames, ANIMATION_FRAMES)

    # def resolve_forwards(self, action: Action, pid: int) -> None:
    #     if action.state['move']:
    #         self.player[pid].pos_update(1, self.frames, ANIMATION_FRAMES)

    # def resolve_backwards(self, action: Action, pid: int) -> None:
    #     if action.state['move']:
    #         self.player[pid].pos_update(-1, self.frames, ANIMATION_FRAMES)

    def scored(self, p1: int, p2: int) -> None:
        self.score[0] += p1
        self.score[1] += p2
        self.reset_turn()

    def reset_turn(self) -> None:
        self.turn = 1
        self.action = 1
        self.frames = -1
        self.available_slots = ACTIONS_MAX
        self.player[0].reset_pos()
        self.player[1].reset_pos()
        self.futr_actions = []
        self.curr_actions = []
        self.opp_actions = []
        self.reset_states()
        self.reset_actions()
        if self.is_sp:
            self.ai.reset_turn()

    def reset_states(self) -> None:
        self.update_distance()
    
    def check_victory(self) -> int:
        for i in range(2):
            if self.score[i] >= 15:
                print(f"Player {i + 1} wins! Resetting game...")
                return (i + 1)
        return 0