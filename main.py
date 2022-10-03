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
    def __init__(self) -> None:
        self.piste_length = 9
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

ACTION_SYMBOLS = ['x', 'X', 'b', 'B', '_', '-', '>', '<']
ALL_MOVES = {
    "Lunge" : "-->X__",
    "Parry" : "BBBB",
    "Riposte" : "bb__x_",
    "Thrust" : "-x__",
    "Flèche" : "-->XX___",
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
        self.HAND_MAX = 3
        self.deck = []
        self.hand = []
        self.cards = [None, None, None]
    
    def update(self) -> None:
        self.draw()
    
    def draw(self) -> None:
        card_button = pygame.Surface((200, 100))
        card_button.fill((128, 128, 128))
        self.cards[0] = win.blit(card_button, (100, 500))
        self.cards[1] = win.blit(card_button, (400, 500))
        self.cards[2] = win.blit(card_button, (700, 500))

        win.blit(pygame.font.SysFont('Comic Sans MS', 30).render("Move: " + str(self.hand[0].name), False, (255, 255, 255)), (100, 500))
        win.blit(pygame.font.SysFont('Comic Sans MS', 30).render("Move: " + str(self.hand[1].name), False, (255, 255, 255)), (400, 500))
        win.blit(pygame.font.SysFont('Comic Sans MS', 30).render("Move: " + str(self.hand[2].name), False, (255, 255, 255)), (700, 500))

    def reset(self) -> None:
        self.deck = []
        self.hand = []
    
    def start(self) -> None:
        self.reset()
        self.deck_add_moves([Move("Lunge", "-->X__"), Move("Parry", "BBBB"), Move("Riposte", "bb__x_"), Move("Thrust", "-x__"), Move("Flèche", "-->XX___"), Move("Fake", "--"), Move("Dodge", "_<"), Move("Move", "_>")])
        self.deck_shuffle()
        self.draw_moves()
        print(self.hand)

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
        for i in range(self.HAND_MAX):
            moves.append(self.deck.pop(0))
        if len(self.hand) == self.HAND_MAX - 3:
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

    def update(self) -> None:
        self.render_player()

    def set_pos_x(self) -> int:
        return self.mat_pos * (10 * SCALE + 40) + X_CENTER - self.width / 2

    def render_player(self) -> None:
        pygame.draw.rect(win, (0, 255 if self.is_user else 0, 0 if self.is_user else 255), (self.pos_x, self.pos_y, self.width, self.height))

    def pos_update(self, steps: int, frames: int, total_frames: int) -> None:
        if not self.is_user:
            steps *= -1
        if frames == total_frames:
            self.mat_pos += steps
            self.pos_x = self.set_pos_x()
        else:
            self.pos_x += (steps * (10 * SCALE + 40)) / total_frames

# ai engine class

class AI_Engine():
    def __init__(self) -> None:
        pass

    def decision(self) -> list[Action]:
        return [Action('_'), Action('<'), Action('_'), Action('_'), Action('_'), Action('_')]

# game engine class

ACTIONS_MAX = 6
TOTAL_CARDS = 3
ANIMATION_FRAMES = 30

class Game_Engine():
    def __init__(self, is_sp: bool) -> None:
        self.is_sp = is_sp                      # determines if the game is singleplayer or multiplayer

        self.player1 = Player(True)
        self.player2 = Player(False)

        self.ai = AI_Engine() if self.is_sp else None

        self.turn = 1                           # turn variable (indicates which turn the game is on right now)
        self.action = 1                         # action variable (indicates which action slot the game is on right now)
        self.frames = 0                         # test for future animation frames temp variable basically

        self.is_user_done = False               # has user committed their actions
        self.running_turn = False               # run turn variable

        self.available_slots = ACTIONS_MAX

        self.curr_actions = []
        self.futr_actions = []

        self.opp_actions = []
    
    def update(self) -> None:
        self.display_turn()
        self.display_actions()
        self.resolve_turn()
        self.player1.update()
        self.player2.update()
    
    def is_turn_running(self) -> bool:
        return self.running_turn
    
    def move_selection(self, card_engine: Card_Engine) -> None:
        if self.available_slots <= 0:
            self.available_slots = ACTIONS_MAX + self.available_slots
            self.user_done()
        else:
            move = None
            for i in range(TOTAL_CARDS):
                if card_engine.cards[i].collidepoint(pygame.mouse.get_pos()):
                    move = card_engine.play_move(i)
                    self.append_actions(move)
                    self.run_turn(move)
                    print(f"Available Slots: {self.available_slots}")

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

    def resolve_turn(self) -> None:
        if self.running_turn:
            if self.frames == ANIMATION_FRAMES:
                self.frames = 0
                self.next_action()
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

    def next_action(self) -> None:
        if self.action < ACTIONS_MAX:
            self.action += 1
        else:
            self.action = 1
            self.next_turn()
        print(self.action, self.turn)
    
    def next_turn(self) -> None:
        self.turn += 1
        self.reset_turn()
    
    def reset_turn(self) -> None:
        self.is_user_done = False
        self.running_turn = False
        self.curr_actions = self.futr_actions
        self.futr_actions = []

    def resolve_action(self) -> None:
        # STILL NEED TO FIT OPPONENT'S MOVE IN HERE!
        user_symbol = self.curr_actions[self.action - 1].symbol
        opp_symbol = self.opp_actions[self.action - 1].symbol
        self.match_symbol(user_symbol, True)
        self.match_symbol(opp_symbol, False)
    
    def match_symbol(self, symbol: str, is_user: bool):
        # ACTION_SYMBOLS = ['x', 'X', 'b', 'B', '_', '-', '>', '<']
        match symbol:
            case 'x':
                self.resolve_hit(is_user)
            case 'X':
                self.resolve_smash(is_user)
            case 'b':
                self.resolve_block(is_user)
            case 'B':
                self.resolve_stance(is_user)
            case '_':
                self.resolve_blank(is_user)
            case '-':
                self.resolve_charge(is_user)
            case '>':
                self.resolve_forwards(is_user)
            case '<':
                self.resolve_backwards(is_user)
    
    def resolve_hit(self, is_user: bool) -> None:
        pass

    def resolve_smash(self, is_user: bool) -> None:
        if is_user:
            self.player1.pos_update(1, self.frames, ANIMATION_FRAMES)
        else:
            self.player2.pos_update(1, self.frames, ANIMATION_FRAMES)

    def resolve_block(self, is_user: bool) -> None:
        pass

    def resolve_stance(self, is_user: bool) -> None:
        pass

    def resolve_blank(self, is_user: bool) -> None:
        pass

    def resolve_charge(self, is_user: bool) -> None:
        pass

    def resolve_forwards(self, is_user: bool) -> None:
        if is_user:
            self.player1.pos_update(1, self.frames, ANIMATION_FRAMES)
        else:
            self.player2.pos_update(1, self.frames, ANIMATION_FRAMES)

    def resolve_backwards(self, is_user: bool) -> None:
        if is_user:
            self.player1.pos_update(-1, self.frames, ANIMATION_FRAMES)
        else:
            self.player2.pos_update(-1, self.frames, ANIMATION_FRAMES)

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
    stage = Stage()
    # player1 = Player(True)
    # player2 = Player(False)
    # move = Move("Lunge", 6, "--X>__")
    # action = Action('X')

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
        # player1.update()
        # player2.update()

        clock.tick(FPS)
        pygame.display.update()


if __name__ == "__main__":
    main()