import pygame

import utils as U
import action_logic as al

from network import *

from action import *
from card_engine import *
from player import *
from ai_engine import *

action_icons_img = pygame.image.load("assets/sprites/action_icons.png")
action_icons_img = pygame.transform.scale(action_icons_img, (U.SPRITE_IMG_WIDTH, U.SPRITE_IMG_HEIGHT))

# game engine class

class Game_Engine():
    def __init__(self) -> None:
        self.gamemode = 0                      # multiplayer: 0 | singleplayer: 1 | debug: 2 | training >= 3

        self.playerModels = [Player(True), Player(False)]

        # self.ai = None
        self.players = [None, None]

        self.score = [0, 0]

        self.turn = 1                           # turn variable (indicates which turn the game is on right now)
        self.action = 1                         # action variable (indicates which action slot the game is on right now)
        self.frames = -1                        # test for future animation frames temp variable basically

        self.is_user_done = False               # has user committed their actions
        self.running_turn = False               # run turn variable

        self.available_slots = U.ACTIONS_MAX

        self.past_actions = []
        self.curr_actions = []
        self.futr_actions = []

        self.opp_actions = []
        self.opp_actions_past = []

        # states variables
        self.distance = self.playerModels[1].mat_pos - self.playerModels[0].mat_pos - 1

        # for animation
        self.action_check = (Blank(), al.states[0], Blank(), al.states[1])
    
    def update(self, win: pygame.Surface) -> None:
        self.display_score(win)
        self.display_turn(win)
        self.display_actions(win)
        self.resolve_turn()
        self.playerModels[0].update(self.running_turn, win, 0, self.frames, self.action_check[0], self.action_check[1])
        self.playerModels[1].update(self.running_turn, win, 1, self.frames, self.action_check[2], self.action_check[3])
    
    def reset(self) -> None:
        self.score = [0, 0]
        self.reset_turn()
        if self.gamemode > 0:
            if self.gamemode >= 3:
                self.players[0].reset()
            self.players[1].reset()
    
    def set_ai(self) -> None:
        if self.gamemode > 0:
            if self.gamemode >= 3:
                self.players[0] = AI_Engine()
                self.players[0].start()
            self.players[1] = Linear_AI_Engine()
            self.players[1].start()
    
    def set_gamemode(self, gamemode: int) -> None:
        self.gamemode = gamemode
        self.set_ai()
    
    def display_score(self, win: pygame.Surface) -> None:
        score = pygame.font.SysFont('Comic Sans MS', 30).render(str(self.score[0]) + " : " + str(self.score[1]), False, (255, 255, 255))
        win.blit(score, score.get_rect(center = (U.X_CENTER, 30)))

    def display_turn(self, win: pygame.Surface) -> None:
        win.blit(pygame.font.SysFont('Comic Sans MS', 30).render("Turn " + str(self.turn), False, (255, 255, 255)), (0, 0))

    def display_actions(self, win: pygame.Surface) -> None:
        ACTION_ICON_SIZE = 27
        CONTAINER_SIZE = ACTION_ICON_SIZE + 6
        BAR_SIZE = CONTAINER_SIZE * 6

        # actions holder
        pygame.draw.rect(win, (128, 128, 128), (U.X_CENTER - (BAR_SIZE + 400), 40, BAR_SIZE, CONTAINER_SIZE))
        pygame.draw.rect(win, (128, 128, 128), (U.X_CENTER + 400, 40, BAR_SIZE, CONTAINER_SIZE))

        # action holder
        pygame.draw.rect(win, (200, 0, 0), (U.X_CENTER - (BAR_SIZE + 400) + CONTAINER_SIZE * (self.action - 1), 40, CONTAINER_SIZE, CONTAINER_SIZE))
        pygame.draw.rect(win, (200, 0, 0), (U.X_CENTER + 400 + CONTAINER_SIZE * (self.action - 1), 40, CONTAINER_SIZE, CONTAINER_SIZE))

        # action symbols
        self.render_actions(win, self.curr_actions, -(BAR_SIZE + 400), 40, 0)
        self.render_actions(win, self.past_actions, -(BAR_SIZE + 400), 80, 0)
    
        # opponent action symbols
        self.render_actions(win, self.opp_actions, 400, 40, 1)
        self.render_actions(win, self.opp_actions_past, 400, 80, 1)
    
    def render_actions(self, win: pygame.Surface, actions: list[Action], from_center: int, height: int, is_opp: int):
        for index, action in enumerate(actions):
            win.blit(action_icons_img, (U.X_CENTER + from_center + (27 + 6) * index + 3, height + 3), ((U.ACTION_SYMBOLS.index(action.symbol) * 27 * 2, 27 * 2 * is_opp, 27, 27)))
            # win.blit(pygame.font.SysFont('Comic Sans MS', 30).render(action.symbol, False, (255, 255, 255)), (U.X_CENTER + from_center + 50 * index + 15, height))
    
    def resolve_turn(self) -> None:
        self.update_distance()
        # print(network.client)
        if self.running_turn:
            if self.frames == U.ANIMATION_FRAMES:
                self.frames = -1
                self.next_action()
            elif self.frames == -1:
                self.frames += 1
                self.check_action()
            else:
                self.frames += 1
                self.resolve_action()
        else:
            match self.gamemode:
                case 0:
                    # recieve connection signal (if opp_actions are appended, then running_turn = True)
                    # send curr actions to run on other screen, send past actions to display what they have done previously
                    if self.is_user_done:
                        if not self.opp_actions == []:
                            self.running_turn = True
                case 1:
                    if self.is_user_done:
                        # run AI
                        self.opp_actions = self.players[1].decision([self.playerModels[0].mat_pos, self.playerModels[1].mat_pos], self.past_actions, self.score, self.turn)
                        # self.opp_actions = self.players[1].debug_decision()
                        self.running_turn = True
                case 2:
                    self.curr_actions = self.players[0].decision([self.playerModels[0].mat_pos, self.playerModels[1].mat_pos], self.opp_actions_past, self.score, self.turn)
                    self.opp_actions = self.players[1].decision([self.playerModels[0].mat_pos, self.playerModels[1].mat_pos], self.past_actions, self.score, self.turn)

                    self.running_turn = True
                case 3:
                    self.curr_actions = self.players[0].decision([self.playerModels[0].mat_pos, self.playerModels[1].mat_pos], self.opp_actions_past, self.score, self.turn)
                    self.opp_actions = self.players[1].decision([self.playerModels[0].mat_pos, self.playerModels[1].mat_pos], self.past_actions, self.score, self.turn)

                    self.running_turn = True

    def next_action(self) -> None:
        print(f"Turn: {self.turn} | Action: {self.action}")
        if self.action < U.ACTIONS_MAX:
            self.action += 1
        else:
            self.action = 1
            self.next_turn()
    
    def next_turn(self) -> None:
        self.turn += 1
        if self.gamemode > 0:
            if self.gamemode >= 3:
                self.set_ai_states(0, 0)
            self.set_ai_states(1, 0)
        self.reset_actions()

    def update_distance(self) -> None:
        self.distance = self.playerModels[1].mat_pos - self.playerModels[0].mat_pos - 1
    
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
        states_1 = {**al.states[0], **{'mat_pos': self.playerModels[0].mat_pos}}
        states_2 = {**al.states[1], **{'mat_pos': self.playerModels[1].mat_pos}}
        print(f"User: {a_1} ; {states_1} | Opp: {a_2} ; {states_2} | Distance: {self.distance}")
        self.action_check = (a_1, al.states[0], a_2, al.states[1])

    def resolve_action(self) -> None:
        self.resolve_movement()
        if self.frames == U.ANIMATION_FRAMES:
            score = self.resolve_score()
            if not 1 in score:
                score = self.out_detection()

            # ai stuff
            # self.players[1].update_rewards(score[0], score[1], self.action)
            # print(self.players[1].rewards)

            if 1 in score:
                self.scored(score[0], score[1])
    
    def resolve_movement(self) -> None:
        for i in range(2):
            self.playerModels[i].pos_update(al.states[i]['move'], self.frames)
            if al.states[i]['push'] == 1:
                if self.distance == 0:
                    self.playerModels[i * -1 + 1].pos_update(-1, self.frames)

    def resolve_score(self) -> None:  # thnk of something better HERE
        return [al.states[0]['score'], al.states[1]['score']]
    
    def out_detection(self) -> None:
        piste_length = U.PISTE_LENGTH
        score = [0, 0]
        for i in range(2):
            if self.playerModels[i].mat_pos > (piste_length - 1) / 2 or self.playerModels[i].mat_pos < -1 * (piste_length - 1) / 2:
                score[i * -1 + 1] = 1
        return score

    def scored(self, p1: int, p2: int) -> None:
        self.score[0] += p1
        self.score[1] += p2
        self.reset_ai_on_score(p1, p2)
        self.reset_turn()
    
    def reset_ai_on_score(self, p1: int, p2: int) -> None:
        if self.gamemode > 0:
            # have to do something with tie, because tie = 0, but cannot = 0
            buffer = 0
            r0 = 10 * (p1 * 2 - p2) + buffer
            r1 = 10 * (p2 * 2 - p1) + buffer
            # now rewards are:
            # -10 = lose
            # 10 = tie
            # 20 = win
            if self.gamemode >= 3:
                self.set_ai_states(0, r0)
            self.set_ai_states(1, r1)
    
    def set_ai_states(self, index: int, reward_score: int) -> None:
        # not sure bout this yet, but potentially record position back at -1 and 1
        # this is because one side scored, so that means the ai should record positions back to default, as the game resets
        # instead of recording position ended when scoring, not sure bout this yet tho
        # original self.playerModels[0].mat_pos, self.playerModels[1].mat_pos

        # self.players[index].set_memory(reward_score, [self.playerModels[0].mat_pos, self.playerModels[1].mat_pos], self.curr_actions)

        # print(f"opp_past_actions: {self.players[index].opp_past_actions}")
        # print(f"opp_past_moves: {self.players[index].opp_past_moves}")
        pass
    
    def reset_ai_turn(self) -> None:
        if self.gamemode > 0:
            if self.gamemode >= 3:
                self.players[0].reset_turn()
            self.players[1].reset_turn()

    def reset_turn(self) -> None:
        self.turn = 1
        self.action = 1
        self.frames = -1
        self.available_slots = U.ACTIONS_MAX
        self.reset_ai_turn()
        self.playerModels[0].reset_pos()
        self.playerModels[1].reset_pos()
        self.futr_actions = []
        self.curr_actions = []
        self.opp_actions = []
        self.reset_states()
        self.reset_actions()
        al.reset_states()

    def reset_states(self) -> None:
        self.update_distance()
    
    # move selection in main
    
    def is_turn_running(self) -> bool:
        return self.running_turn
    
    def move_selection(self, card_engine: Card_Engine) -> None:
        if self.available_slots <= 0:
            self.available_slots = U.ACTIONS_MAX + self.available_slots
            self.user_done()
        else:
            for i in range(card_engine.HAND_MAX):
                if card_engine.cards[i].collidepoint(pygame.mouse.get_pos()):
                    move = card_engine.play_move(i)
                    self.append_actions(move)
                    self.update_slots(move)

    def append_actions(self, move: Move) -> None:
        value = U.ACTIONS_MAX - len(self.curr_actions)
        split = move.split(value)
        self.curr_actions.extend(split[0])
        self.futr_actions.extend(split[1])

    def update_slots(self, move: Move) -> None:
        if move.slots >= self.available_slots:
            self.available_slots = U.ACTIONS_MAX - (move.slots - self.available_slots)
            self.user_done()
        else:
            self.available_slots = self.available_slots - move.slots

    def user_done(self) -> None:
        self.is_user_done = True

    # victory checking in main
    
    def check_victory(self) -> int:
        if self.score[0] == self.score[1] and self.score[0] == 15:
            print(f"Both Player wins! Resetting game...")
            return 3
        for i in range(2):
            if self.score[i] >= 15:
                print(f"Player {i + 1} wins! Resetting game...")
                return (i + 1)
        return 0
    
    # multiplayer sockets stuff

    def send_data(self, network: Network) -> str:
        data = ','.join([i.symbol for i in self.curr_actions]) + ';' + ','.join([i.symbol for i in self.past_actions])
        return network.send(data)

    def parse_data(self, data: str) -> None:
        try:
            parsed = data.split(';')
            curr, past = parsed[0].split(','), parsed[1].split(',')
            if len(curr) == 6:
                curr = [U.convert_action(symbol) for symbol in curr]
                past = [U.convert_action(symbol) for symbol in past if symbol != '']
                self.opp_actions, self.opp_actions_past = curr, past
        except:
            pass