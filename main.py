from sys import exit

import utils as U

import network as network

from action import *
from stage import *
from card_engine import *
from game_engine import *

import pygame

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

# end game stuff

winner = 0
end_message_timer = 0

# gui functions

def display_victory(winner: int):
    win.blit(pygame.font.SysFont('Comic Sans MS', 60).render("Player " + str(winner) + " wins!", False, (255, 255, 255)), (U.X_CENTER, U.Y_CENTER))

curr_gui = 'menu'
is_sp = None

def gui_menu(*args) -> str:         # temporary menu setup
    global is_sp
    if is_sp == None:
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_m]):
            if network.client == None:
                network.conn()
            is_sp = False
        if (keys[pygame.K_s]):      # or True = always single player right now :)
            is_sp = True
    else:
        for arg in args:
            if type(arg) == Game_Engine:
                arg.set_sp(is_sp)
            arg.reset()
        return 'game'
    return 'menu'

def gui_game(*args) -> str:
    global curr_gui, winner
    for arg in args:
        arg.update(win)
        if type(arg) == Game_Engine:
            winner = arg.check_victory()
    if winner != 0:
        return 'victory'
    return 'game'

def gui_victory(*args) -> str:
    global curr_gui, winner, end_message_timer
    if end_message_timer == 300:
        end_message_timer = 0
        winner = 0
        for arg in args:
            arg.reset()
        return 'menu'
    else:
        end_message_timer += 1
        display_victory(winner)
    return 'victory'

gui = {
    'menu' : lambda args: gui_menu(*args),
    'game' : lambda args: gui_game(*args),
    'victory' : lambda args: gui_victory(*args),
}

# main function

def main():

    # load stuff and classes
    U.load_ALL_MOVES()

    game_engine = Game_Engine()
    card_engine_player = Card_Engine_Player()
    stage = Stage(U.PISTE_LENGTH)

    # gui stuff
    curr_gui = 'menu'

    # load moves in card
    card_engine_player.start(U.ALL_MOVES)

    # game loop

    while True:
        for event in pygame.event.get():

            # quit game event
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if curr_gui == 'game':
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game_engine.is_turn_running():
                    game_engine.move_selection(card_engine_player)

        win.fill((0, 0, 0))
        
        curr_gui = gui.get(curr_gui)([stage, card_engine_player, game_engine])

        clock.tick(FPS)
        pygame.display.update()


if __name__ == "__main__":
    main()