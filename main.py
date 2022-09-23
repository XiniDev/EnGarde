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
        pygame.draw.rect(win, (255, 0, 0), (WIDTH / 2 - 2, HEIGHT / 2 - 2, 4, 4))        # true center
    
    def render_mats(self) -> None:
        X_CENTER = WIDTH / 2
        Y_CENTER = HEIGHT / 2
        LENGTH = 10 * SCALE            # temp length until i make mat sprite :)
        SPACING = 5 * SCALE
        for i in range(self.piste_length):
            # win.blit(img, (), ())     # sprite holder
            pygame.draw.rect(
                win, (255, 255, 255), (X_CENTER - LENGTH / 2 + ((LENGTH + SPACING) * (-1 if i % 2 == 1 else 1) * ((i + 1) // 2)), Y_CENTER, LENGTH, 5))

# player class

class Player():
    def __init__(self, is_user) -> None:
        self.is_user = is_user
        self.mat_pos = -1 if self.is_user else 1

        self.width = 10 * SCALE
        self.height = 10 * SCALE
        self.pos_x = self.set_pos_x()
        self.pos_y = HEIGHT / 2 - SCALE - self.height

    def update(self) -> None:
        steps = 0
        # steps test
        # keys = pygame.key.get_pressed()
        # if (keys[pygame.K_a]):
        #     steps = -1
        # if (keys[pygame.K_d]):
        #     steps = 1
        self.pos_update(steps)

    def set_pos_x(self) -> int:
        return self.mat_pos * (10 * SCALE + 40) + WIDTH / 2 - self.width / 2

    def render_player(self) -> None:
        pygame.draw.rect(win, (0, 255 if self.is_user else 0, 0 if self.is_user else 255), (self.pos_x, self.pos_y, self.width, self.height))

    def pos_update(self, steps) -> None:
        self.mat_pos += steps
        self.pos_x = self.set_pos_x()
        self.render_player()

ACTION_SYMBOLS = ['X', 'B', '_', '-', '>', '<', '^', '$']
ALL_MOVES = {
    "Lunge" : "--X>__",
    "Parry" : "BBB$",
    "Riposte" : "BB__X_",
    "Thrust" : "-X__",
    "Flèche" : "---X^___",
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
    def __init__(self, name: str, slots: int, move_str: str) -> None:
        self.name = None
        try:
            if name in ALL_MOVES:
                self.name = name
            else:
                raise ValueError('Moves must have a valid name')
        except ValueError as exp:
            print("The move: {} does not have a valid name\n{}".format(name, exp))
            exit(1)
        self.slots = 0
        try:
            if slots == len(ALL_MOVES.get(self.name)):
                self.slots = slots
            else:
                raise ValueError('Moves must take up the correct number of slots')
        except ValueError as exp:
            print("The move: {} should not take up {} slots\n{}".format(name, slots, exp))
            exit(1)
        self.actions = None
        try:
            if len(move_str) == slots:
                try:
                    if move_str == ALL_MOVES.get(self.name):
                        self.actions = [Action(move_str[i]) for i in range(self.slots)]
                    else:
                        raise ValueError('Moves must have valid actions')
                except ValueError as exp:
                    print("The move: {} have invalid actions \n{}".format(name, exp))
                    exit(1)
            else:
                raise ValueError('Moves must have same number of actions as the slots it takes up')
        except ValueError as exp:
            print("The move: {} has a length of {} but must take up {} slots\n{}".format(name, len(move_str), slots, exp))
            exit(1)

# card engine class

class Card_Engine():
    def __init__(self) -> None:
        self.DECK_MAX = 8
        self.HAND_MAX = 3
        self.deck = []
        self.hand = []
    
    def update(self) -> None:
        win.blit(pygame.font.SysFont('Comic Sans MS', 30).render("Move: " + str(self.hand[0].name), False, (255, 255, 255)), (100, 500))
        win.blit(pygame.font.SysFont('Comic Sans MS', 30).render("Move: " + str(self.hand[1].name), False, (255, 255, 255)), (400, 500))
        win.blit(pygame.font.SysFont('Comic Sans MS', 30).render("Move: " + str(self.hand[2].name), False, (255, 255, 255)), (700, 500))

    def reset(self) -> None:
        self.deck = []
        self.hand = []
    
    def start(self) -> None:
        self.reset()
        self.deck_add_moves([Move("Lunge", 6, "--X>__"), Move("Parry", 4, "BBB$"), Move("Riposte", 6, "BB__X_"), Move("Thrust", 4, "-X__"), Move("Flèche", 8, "---X^___"), Move("Fake", 2, "--"), Move("Dodge", 2, "_<"), Move("Move", 2, "_>")])
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


# game functions 

ACTIONS_MAX = 6
turn = 1            # global turn variable (indicates which turn the game is on right now)
action = 1          # global action variable (indicates which action slot the game is on right now)

def next_turn() -> None:
    global turn
    turn += 1

def next_action() -> None:
    global action, turn
    if action < ACTIONS_MAX:
        action += 1
    else:
        action = 1
        next_turn()
    print(action, turn)

def run_turn():
    for i in range(ACTIONS_MAX):
        next_action()

def display_turn() -> None:
    win.blit(pygame.font.SysFont('Comic Sans MS', 30).render("Turn " + str(turn), False, (255, 255, 255)), (0, 0))


# connection function

def conn() -> None:

    # connect to server
    global client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((IP, PORT))

# main function

def main():

    card_engine = Card_Engine()
    stage = Stage()
    player1 = Player(True)
    player2 = Player(False)
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

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                card_engine.play_move(0)
                run_turn()

        win.fill((0, 0, 0))

        keys = pygame.key.get_pressed()
        if (keys[pygame.K_LSHIFT] and keys[pygame.K_c]):
            if client == None:
                conn()

        display_turn()
        card_engine.update()
        stage.update()
        player1.update()
        player2.update()

        clock.tick(FPS)
        pygame.display.update()


if __name__ == "__main__":
    main()