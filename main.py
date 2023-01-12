from sys import exit

import utils as U

from network import *

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
pygame.mixer.music.set_volume(0) #0.3
pygame.mixer.music.play(loops = -1)

# end game stuff

winner = 0
end_message_timer = 0

# gui functions

def display_victory(winner: int):
    win.blit(pygame.font.SysFont('Comic Sans MS', 60).render("Player " + str(winner) + " wins!", False, (255, 255, 255)), (U.X_CENTER, U.Y_CENTER))

curr_gui = 'menu'
connection = None

network = None

def gui_menu(game_engine: Game_Engine, *args) -> str:         # temporary menu setup
    global connection, network
    if connection == None:
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_m]):
            network = Network()
            if network.client == None:
                network.conn()
            connection = False
        if (keys[pygame.K_s]):      # or True = always single player right now :)
            connection = True
    else:
        game_engine.set_sp(connection)
        for arg in args:
            arg.reset()
        game_engine.reset()
        return 'game'
    return 'menu'

def gui_game(game_engine: Game_Engine, *args) -> str:
    global curr_gui, winner

    # update all classes
    for arg in args:
        arg.update(win)
    game_engine.update(win)

    # network stuff
    if game_engine.is_sp == False and network != None and network.client != None:
        data = game_engine.send_data(network)
        game_engine.parse_data(data)
    
    # check victory
    winner = game_engine.check_victory()
    if winner != 0:
        return 'victory'
    return 'game'

def gui_victory(game_engine: Game_Engine, *args) -> str:
    global curr_gui, winner, end_message_timer
    if end_message_timer == 300:
        end_message_timer = 0
        winner = 0
        for arg in args:
            arg.reset()
        game_engine.reset()
        return 'menu'
    else:
        end_message_timer += 1
        display_victory(winner)
    return 'victory'

gui = {
    'menu' : lambda game_engine, args: gui_menu(game_engine, *args),
    'game' : lambda game_engine, args: gui_game(game_engine, *args),
    'victory' : lambda game_engine, args: gui_victory(game_engine, *args),
}

# main function

def main():

    # load stuff and classes
    U.load_ALL_MOVES()

    game_engine = Game_Engine()
    card_engine_display = Card_Engine_Display(no_shuffle=True)
    stage = Stage(U.PISTE_LENGTH)

    # gui stuff
    curr_gui = 'menu'

    # load moves in card
    card_engine_display.start(U.ALL_MOVES)

    # game loop

    while True:
        for event in pygame.event.get():

            # quit game event
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

            if curr_gui == 'game':
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not game_engine.is_turn_running() and not game_engine.is_user_done:
                    game_engine.move_selection(card_engine_display)

        win.fill((0, 0, 0))
        
        curr_gui = gui.get(curr_gui)(game_engine, [stage, card_engine_display])
        # if not network.client == None:
        #     network.send("asdf")

        clock.tick(FPS)
        pygame.display.update()


if __name__ == "__main__":
    main()