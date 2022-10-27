from sys import exit
import socket

import utils as U

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
SCREEN_SIZE = (U.WIDTH, U.HEIGHT)

pygame.init()

win = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption(CAPTION)
clock = pygame.time.Clock()

pygame.mixer.init()
pygame.mixer.music.load('assets/music/background_track.wav')
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(loops = -1)

#actiion ;p

# connection function

def conn() -> None:

    # connect to server
    global client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((IP, PORT))

# main function

def main():

    U.load_ALL_MOVES()

    game_engine = Game_Engine(True)
    card_engine_player = Card_Engine_Player()
    stage = Stage(9)

    # game loop

    game_engine.start()
    card_engine_player.start(U.ALL_MOVES)

    while True:
        for event in pygame.event.get():

            # quit game event
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game_engine.is_turn_running():
                game_engine.move_selection(card_engine_player)

        win.fill((0, 0, 0))

        keys = pygame.key.get_pressed()
        if (keys[pygame.K_LSHIFT] and keys[pygame.K_c]):
            if client == None:
                conn()

        stage.update(win)
        card_engine_player.update(win)
        game_engine.update(win)

        winner = game_engine.check_victory(win)
        if winner != 0:
            print("!")

        clock.tick(FPS)
        pygame.display.update()


if __name__ == "__main__":
    main()