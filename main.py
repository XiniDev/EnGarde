from sys import exit
import socket

import constants as C

from action import *
from stage import *
from card_engine import *
from game_engine import *

import pygame

IP = 'localhost'
PORT = 5555

client = None

pygame.init()

# initialisation

CAPTION = "En-Garde!"
FPS = 60
SCREEN_SIZE = (C.WIDTH, C.HEIGHT)

pygame.init()

win = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption(CAPTION)
clock = pygame.time.Clock()

#actiion ;p

ALL_MOVES = {}

# load ALL_MOVES function

def load_ALL_MOVES() -> None:
    global ALL_MOVES
    for (name, move_str) in C.ALL_MOVES_STR.items():
        actions = []
        for action in move_str:
            match action:
                case 'x':
                    actions.append(Hit())
                case 'X':
                    actions.append(Smash())
                case 'b':
                    actions.append(Block())
                case 'B':
                    actions.append(Stance())
                case '_':
                    actions.append(Blank())
                case '-':
                    actions.append(Charge())
                case '=':
                    actions.append(Push())
                case '>':
                    actions.append(Forwards())
                case '<':
                    actions.append(Backwards())
        ALL_MOVES[name] = tuple(actions)
    print(ALL_MOVES)

# connection function

def conn() -> None:

    # connect to server
    global client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((IP, PORT))

# main function

def main():

    load_ALL_MOVES()

    game_engine = Game_Engine(True)
    card_engine = Card_Engine()
    stage = Stage(9)

    # game loop

    card_engine.start(ALL_MOVES)

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

        stage.update(win)
        card_engine.update(win)
        game_engine.update(win)

        winner = game_engine.check_victory(win)
        if winner != 0:
            print("!")

        clock.tick(FPS)
        pygame.display.update()


if __name__ == "__main__":
    main()