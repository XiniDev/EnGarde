from sys import exit
import socket

import random

import pygame

IP = 'localhost'
PORT = 5555

client = None

pygame.init()

# initialisation

CAPTION = "En-Garde!"
SCALE = 8
WIDTH = 160 * SCALE
HEIGHT = 90 * SCALE
FPS = 60
SCREEN_SIZE = (WIDTH, HEIGHT)

X_CENTER = WIDTH / 2
Y_CENTER = HEIGHT / 2

pygame.init()

win = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption(CAPTION)
clock = pygame.time.Clock()

# mat class (piste is made out of multiple mats)

class Mat():
    def __init__(self) -> None:
        pass

# stage class

class Stage():
    def __init__(self, piste_length: int) -> None:
        self.piste_length = piste_length
        self.piste = [Mat() for i in range(self.piste_length)]              # use this once sprites are made and put them in mat class

    def update(self) -> None:
        self.render_mats()
        pygame.draw.rect(win, (255, 0, 0), (X_CENTER - 2, Y_CENTER - 2, 4, 4))        # true center
    
    def render_mats(self) -> None:
        LENGTH = 10 * SCALE            # temp length until i make mat sprite :)
        SPACING = 5 * SCALE
        for i in range(self.piste_length):
            # win.blit(img, (), ())     # sprite holder
            pygame.draw.rect(
                win, (255, 255, 255), (X_CENTER - LENGTH / 2 + ((LENGTH + SPACING) * (-1 if i % 2 == 1 else 1) * ((i + 1) // 2)), Y_CENTER, LENGTH, 5))

ACTION_SYMBOLS = ['x', 'X', 'b', 'B', '_', '-', '=', '>', '<']
ALL_MOVES = {
    "Lunge" : "--=x__",
    "Parry" : "BBBB",
    "Riposte" : "bb__x_",
    "Thrust" : "-x__",
    "Flèche" : "---=X___",
    "Fake" : "--",
    "Dodge" : "_<",
    "Move" : "_>"
}

class Action():
    def __init__(self, symbol: str) -> None:
        self.symbol = None
        try:
            if symbol in ACTION_SYMBOLS:
                self.symbol = symbol
            else:
                raise ValueError('Actions must have a valid symbol')
        except ValueError as exp:
            print("An action used an invalid symbol: {}\n{}".format(symbol, exp))
            exit(1)

    def resolve(self) -> None:
        pass

class Move():
    def __init__(self, name: str, move_str: str) -> None:
        self.name = None
        try:
            if name in ALL_MOVES:
                self.name = name
            else:
                raise ValueError('Moves must have a valid name')
        except ValueError as exp:
            print("The move: {} does not have a valid name\n{}".format(name, exp))
            exit(1)
        # self.slots = 0
        # try:
        #     if slots == len(ALL_MOVES.get(self.name)):
        #         self.slots = slots
        #     else:
        #         raise ValueError('Moves must take up the correct number of slots')
        # except ValueError as exp:
        #     print("The move: {} should not take up {} slots\n{}".format(name, slots, exp))
        #     exit(1)
        self.actions = None
        # try:
        #     if len(move_str) == slots:
        try:
            if move_str == ALL_MOVES.get(self.name):
                self.actions = [Action(move_str[i]) for i in range(len(move_str))]
            else:
                raise ValueError('Moves must have valid actions')
        except ValueError as exp:
            print("The move: {} have invalid actions \n{}".format(name, exp))
            exit(1)
        #     else:
        #         raise ValueError('Moves must have same number of actions as the slots it takes up')
        # except ValueError as exp:
        #     print("The move: {} has a length of {} but must take up {} slots\n{}".format(name, len(move_str), slots, exp))
        #     exit(1)
        self.slots = len(self.actions)

# card engine class

class Card_Engine():
    def __init__(self) -> None:
        self.DECK_MAX = 8
        self.HAND_MAX = 4
        self.deck = []
        self.hand = []
        self.cards = [None, None, None, None]
    
    def update(self) -> None:
        self.draw()
    
    def draw(self) -> None:
        card_button = pygame.Surface((200, 100))
        card_button.fill((128, 128, 128))
        self.cards[0] = win.blit(card_button, (100, 500))
        self.cards[1] = win.blit(card_button, (400, 500))
        self.cards[2] = win.blit(card_button, (700, 500))
        self.cards[3] = win.blit(card_button, (1000, 500))

        win.blit(pygame.font.SysFont('Comic Sans MS', 30).render("Move: " + str(self.hand[0].name), False, (255, 255, 255)), (100, 500))
        win.blit(pygame.font.SysFont('Comic Sans MS', 30).render("Move: " + str(self.hand[1].name), False, (255, 255, 255)), (400, 500))
        win.blit(pygame.font.SysFont('Comic Sans MS', 30).render("Move: " + str(self.hand[2].name), False, (255, 255, 255)), (700, 500))
        win.blit(pygame.font.SysFont('Comic Sans MS', 30).render("Move: " + str(self.hand[3].name), False, (255, 255, 255)), (1000, 500))

    def reset(self) -> None:
        self.deck = []
        self.hand = []
    
    def start(self) -> None:
        self.reset()

        # example moves
        moves = []
        for (name, actions) in ALL_MOVES.items():
            moves.append(Move(name, actions))
        self.deck_add_moves(moves)
        
        self.deck_shuffle()
        self.draw_moves()

    def deck_size_check(self, addition: int) -> bool:
        if len(self.deck) + addition <= self.DECK_MAX:
            return True
        else:
            return False

    def deck_add_move(self, move: Move) -> bool:
        if self.deck_size_check(1):
            self.deck.append(move)
            return True
        else:
            return False

    def deck_add_moves(self, moves: list[Move]) -> bool:
        if self.deck_size_check(len(moves)):
            self.deck.extend(moves)
            return True
        else:
            return False

    def deck_shuffle(self) -> None:
        random.shuffle(self.deck)

    def draw_move(self) -> None:
        move = self.deck.pop(0)
        if len(self.hand) == self.HAND_MAX - 1:
            self.hand.append(move)

    def draw_moves(self) -> None:
        moves = []
        if len(self.hand) == self.HAND_MAX - self.HAND_MAX:
            for i in range(self.HAND_MAX):
                moves.append(self.deck.pop(0))
            self.hand.extend(moves)

    def play_move(self, move_id: int) -> Move:       # three moves to choose from, after select one with mouse, it should give the number of the item in the hand
        move = self.hand[move_id]
        self.hand[move_id] = self.deck.pop(0)
        self.deck.append(move)
        return move


# player class

class Player():
    def __init__(self, is_user: bool) -> None:
        self.is_user = is_user
        self.mat_pos = -1 if self.is_user else 1

        self.width = 10 * SCALE
        self.height = 10 * SCALE
        self.pos_x = self.set_pos_x()
        self.pos_y = Y_CENTER - SCALE - self.height

        # player states variables
        self.charge = 0
        self.stance = False

    def update(self) -> None:
        self.render_player()
    
    def render_player(self) -> None:
        pygame.draw.rect(win, (0, 255 if self.is_user else 0, 0 if self.is_user else 255), (self.pos_x, self.pos_y, self.width, self.height))

    def set_pos_x(self) -> int:
        return self.mat_pos * (10 * SCALE + 40) + X_CENTER - self.width / 2

    def pos_update(self, steps: int, frames: int, total_frames: int) -> None:
        if not self.is_user:
            steps *= -1
        if frames == total_frames:
            self.mat_pos += steps
            self.pos_x = self.set_pos_x()
        else:
            self.pos_x += (steps * (10 * SCALE + 40)) / total_frames
    
    def reset_pos(self) -> None:
        self.mat_pos = -1 if self.is_user else 1
        self.pos_x = self.set_pos_x()
    
    def reset_states(self) -> None:
        self.charge = 0
        self.stance = False

# ai engine class

class AI_Engine():
    def __init__(self) -> None:
        pass

    def decision(self) -> list[Action]:
        return [Action('_'), Action('_'), Action('>'), Action('_'), Action('_'), Action('_')]

# game engine class

ACTIONS_MAX = 6
ANIMATION_FRAMES = 20

class Game_Engine():
    def __init__(self, is_sp: bool) -> None:
        self.is_sp = is_sp                      # determines if the game is singleplayer or multiplayer

        self.player = [Player(True), Player(False)]

        self.ai = AI_Engine() if self.is_sp else None

        self.score = [0, 0]

        self.turn = 1                           # turn variable (indicates which turn the game is on right now)
        self.action = 1                         # action variable (indicates which action slot the game is on right now)
        self.frames = -1                        # test for future animation frames temp variable basically

        self.is_user_done = False               # has user committed their actions
        self.running_turn = False               # run turn variable

        self.available_slots = ACTIONS_MAX

        self.curr_actions = []
        self.futr_actions = []

        self.opp_actions = []
        self.opp_actions_past = []

        # states variables
        self.distance = self.player[1].mat_pos - self.player[0].mat_pos - 1
        self.resolve = [False, False]           # for checking if an action is allowed to be resolved or not
    
    def update(self) -> None:
        self.display_score()
        self.display_turn()
        self.display_actions()
        self.resolve_turn()
        self.player[0].update()
        self.player[1].update()
    
    def is_turn_running(self) -> bool:
        return self.running_turn
    
    def move_selection(self, card_engine: Card_Engine) -> None:
        if self.available_slots <= 0:
            self.available_slots = ACTIONS_MAX + self.available_slots
            self.user_done()
        else:
            move = None
            for i in range(card_engine.HAND_MAX):
                if card_engine.cards[i].collidepoint(pygame.mouse.get_pos()):
                    move = card_engine.play_move(i)
                    self.append_actions(move)
                    self.run_turn(move)

    def append_actions(self, move: Move) -> None:
        for j in range(len(move.actions)):
            if len(self.curr_actions) < ACTIONS_MAX:
                self.curr_actions.append(move.actions[j])
            else:
                self.futr_actions.append(move.actions[j])

    def run_turn(self, move: Move) -> None:
        if move.slots >= self.available_slots:
            self.available_slots = ACTIONS_MAX - (move.slots - self.available_slots)
            self.user_done()
        else:
            self.available_slots = self.available_slots - move.slots

    def user_done(self) -> None:
        self.is_user_done = True
    
    def display_score(self) -> None:
        score = pygame.font.SysFont('Comic Sans MS', 30).render(str(self.score[0]) + " : " + str(self.score[1]), False, (255, 255, 255))
        win.blit(score, score.get_rect(center = (X_CENTER, 30)))

    def display_turn(self) -> None:
        win.blit(pygame.font.SysFont('Comic Sans MS', 30).render("Turn " + str(self.turn), False, (255, 255, 255)), (0, 0))

    def display_actions(self) -> None:
        # actions holder
        pygame.draw.rect(win, (128, 128, 128), (X_CENTER - 600, 50, 300, 50))
        pygame.draw.rect(win, (128, 128, 128), (X_CENTER + 300, 50, 300, 50))

        # action holder
        pygame.draw.rect(win, (200, 0, 0), (X_CENTER - 600 + 50 * (self.action - 1), 50, 50, 50))
        pygame.draw.rect(win, (200, 0, 0), (X_CENTER + 300 + 50 * (self.action - 1), 50, 50, 50))

        # action symbols
        for index, action in enumerate(self.curr_actions):
            win.blit(pygame.font.SysFont('Comic Sans MS', 30).render(action.symbol, False, (255, 255, 255)), (X_CENTER - 600 + 50 * index + 15, 50))
        
        # opponent action symbols
        for index, action in enumerate(self.opp_actions):
            win.blit(pygame.font.SysFont('Comic Sans MS', 30).render(action.symbol, False, (255, 255, 255)), (X_CENTER + 300 + 50 * index + 15, 50))
        for index, action in enumerate(self.opp_actions_past):
            win.blit(pygame.font.SysFont('Comic Sans MS', 30).render(action.symbol, False, (255, 255, 255)), (X_CENTER + 300 + 50 * index + 15, 100))

    def resolve_turn(self) -> None:
        self.update_distance()
        if self.running_turn:
            if self.frames == ANIMATION_FRAMES:
                for i in range(2):
                    if self.is_player_out(i):
                        self.scored(i)
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
                self.opp_actions = self.ai.decision()
                self.running_turn = True
            else:
                # recieve connection signal (if recieve signal -> self.running_turn = True)
                pass

    def update_distance(self) -> None:
        self.distance = self.player[1].mat_pos - self.player[0].mat_pos - 1
    
    def is_player_out(self, pid: int) -> None:
        piste_length = 9
        if self.player[pid].mat_pos > (piste_length - 1) / 2 or self.player[pid].mat_pos < -1 * (piste_length - 1) / 2:
            return True
        else:
            return False

    def next_action(self) -> None:
        print(f"Turn: {self.turn} | Action: {self.action}")
        self.reset_resolve()
        if self.action < ACTIONS_MAX:
            self.action += 1
        else:
            self.action = 1
            self.next_turn()
    
    def reset_resolve(self) -> None:
        self.resolve = [False, False]
    
    def next_turn(self) -> None:
        self.turn += 1
        self.reset_actions()
    
    def reset_actions(self) -> None:
        self.is_user_done = False
        self.running_turn = False
        self.curr_actions = self.futr_actions
        self.futr_actions = []
        self.opp_actions_past = self.opp_actions
        self.opp_actions = []
    
    def check_action(self) -> None:
        user_symbol = self.curr_actions[self.action - 1].symbol
        opp_symbol = self.opp_actions[self.action - 1].symbol
        self.check_symbol(user_symbol, 0)
        self.check_symbol(opp_symbol, 1)

    def resolve_action(self) -> None:
        # STILL NEED TO FIT OPPONENT'S MOVE IN HERE!
        user_symbol = self.curr_actions[self.action - 1].symbol
        opp_symbol = self.opp_actions[self.action - 1].symbol
        self.resolve_symbol(user_symbol, 0)
        self.resolve_symbol(opp_symbol, 1)
    
    def check_symbol(self, symbol: str, pid: int) -> None:
        # ACTION_SYMBOLS = ['x', 'X', 'b', 'B', '_', '-', '=', '>', '<']
        # priority is < then B then b then X then x then = then > then - then _
        # still need to figure out whats the best way to code this :(
        match symbol:
            case 'x':
                self.check_hit(pid)
            case 'X':
                self.check_smash(pid)
            case 'b':
                self.check_block(pid)
            case 'B':
                self.check_stance(pid)
            case '_':
                self.check_blank(pid)
            case '-':
                self.check_charge(pid)
            case '=':
                self.check_push(pid)
            case '>':
                self.check_forwards(pid)
            case '<':
                self.check_backwards(pid)

    def resolve_symbol(self, symbol: str, pid: int) -> None:
        # ACTION_SYMBOLS = ['x', 'X', 'b', 'B', '_', '-', '=', '>', '<']
        # priority is < then B then b then X then x then = then > then - then _
        # still need to figure out whats the best way to code this :(
        if self.resolve[pid]:
            match symbol:
                case 'x':
                    self.resolve_hit(pid)
                case 'X':
                    self.resolve_smash(pid)
                case 'b':
                    self.resolve_block(pid)
                case 'B':
                    self.resolve_stance(pid)
                case '_':
                    self.resolve_blank(pid)
                case '-':
                    self.resolve_charge(pid)
                case '=':
                    self.resolve_push(pid)
                case '>':
                    self.resolve_forwards(pid)
                case '<':
                    self.resolve_backwards(pid)

    def check_hit(self, pid: int) -> None:
        self.resolve[pid] = True
    
    def resolve_hit(self, pid: int) -> None:
        self.reset_charge(pid)
        if self.distance == 0 and self.frames == 20:
            self.scored(pid)

    def check_smash(self, pid: int) -> None:
        self.resolve[pid] = True

    def resolve_smash(self, pid: int) -> None:
        self.player[pid].pos_update(1, self.frames, ANIMATION_FRAMES)
        self.reset_charge(pid)
        if self.distance == 0 and self.frames == 20:
            self.scored(pid)

    def check_block(self, pid: int) -> None:
        self.resolve[pid] = True

    def resolve_block(self, pid: int) -> None:
        pass

    def check_stance(self, pid: int) -> None:
        self.resolve[pid] = True

    def resolve_stance(self, pid: int) -> None:
        pass

    def check_blank(self, pid: int) -> None:
        self.resolve[pid] = True

    def resolve_blank(self, pid: int) -> None:
        pass

    def check_charge(self, pid: int) -> None:
        self.resolve[pid] = True
        self.player[pid].charge += 1

    def resolve_charge(self, pid: int) -> None:
        pass

    def check_push(self, pid: int) -> None:
        if self.distance > 1:
            self.resolve[pid] = True
        else:
            if pid == 0:
                self.resolve[pid] = True
            if pid == 1:
                if self.curr_actions[self.action - 1].symbol == '=':
                    self.resolve[0] = False
                else:
                    self.resolve[pid] = True

    def resolve_push(self, pid: int) -> None:
        self.player[pid].pos_update(1, self.frames, ANIMATION_FRAMES)
        if self.distance == 0:
            self.player[pid * -1 + 1].pos_update(-1, self.frames, ANIMATION_FRAMES)

    def check_forwards(self, pid: int) -> None:
        if self.distance > 1:
            self.resolve[pid] = True
        elif self.distance == 1:
            if pid == 0:
                self.resolve[pid] = True
            if pid == 1:
                if self.curr_actions[self.action - 1].symbol == '>':
                    self.resolve[0] = False
                elif not self.curr_actions[self.action - 1].symbol == '=':
                    self.resolve[pid] = True

    def resolve_forwards(self, pid: int) -> None:
        self.player[pid].pos_update(1, self.frames, ANIMATION_FRAMES)

    def check_backwards(self, pid: int) -> None:
        self.resolve[pid] = True

    def resolve_backwards(self, pid: int) -> None:
        self.player[pid].pos_update(-1, self.frames, ANIMATION_FRAMES)
    
    def scored(self, pid: int) -> None:
        self.score[pid] += 1
        self.reset_turn()
    
    def reset_charge(self, pid: int) -> None:
        self.player[pid].charge = 0

    def reset_turn(self) -> None:
        self.turn = 1
        self.action = 1
        self.frames = -1
        self.available_slots = ACTIONS_MAX
        self.player[0].reset_pos()
        self.player[1].reset_pos()
        self.futr_actions = []
        self.opp_actions = []
        self.reset_states()
        self.reset_actions()

    def reset_states(self) -> None:
        self.update_distance()
        self.player[0].reset_states()
        self.player[1].reset_states()

# connection function

def conn() -> None:

    # connect to server
    global client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((IP, PORT))

# main function

def main():

    game_engine = Game_Engine(True)
    card_engine = Card_Engine()
    stage = Stage(9)

    # game loop

    card_engine.start()

    while True:
        for event in pygame.event.get():

            # quit game event
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game_engine.is_turn_running():
                game_engine.move_selection(card_engine)

        win.fill((0, 0, 0))

        keys = pygame.key.get_pressed()
        if (keys[pygame.K_LSHIFT] and keys[pygame.K_c]):
            if client == None:
                conn()

        stage.update()
        card_engine.update()
        game_engine.update()

        clock.tick(FPS)
        pygame.display.update()


if __name__ == "__main__":
    main()