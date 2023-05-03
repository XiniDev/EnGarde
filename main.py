from sys import exit

import utils as U

from network import *

from action import *
from stage import *
from card_engine import *
from game_engine import *

import pygame

# pygame.init()

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
pygame.mixer.music.set_volume(0.1) #0.3
pygame.mixer.music.play(loops = -1)

# end game stuff

winner = 0
end_message_timer = 0

# gui functions

def display_victory(winner: int):
    if winner == 3:
        win.blit(pygame.font.Font('assets/font/Minecraft.ttf', 60).render("Both Player wins!", False, (255, 255, 255)), (U.X_CENTER, U.Y_CENTER))
    else:
        win.blit(pygame.font.Font('assets/font/Minecraft.ttf', 60).render("Player " + str(winner) + " wins!", False, (255, 255, 255)), (U.X_CENTER, U.Y_CENTER))

curr_gui = 'menu'
gamemode = -1

network = None

button1, button2, button3, button4, button5, button6, button7 = pygame.Rect(0,0,0,0), pygame.Rect(0,0,0,0),pygame.Rect(0,0,0,0),pygame.Rect(0,0,0,0),pygame.Rect(0,0,0,0),pygame.Rect(0,0,0,0),pygame.Rect(0,0,0,0)

def gui_menu(game_engine: Game_Engine, *args) -> str:         # temporary menu setup
    global gamemode, network, button1, button2, button3, button4, button5, button6, button7
    title = pygame.font.Font('assets/font/Minecraft.ttf', 60).render("EnGarde!", False, (255, 255, 255))
    win.blit(title, title.get_rect(center = (U.X_CENTER, U.SCALE * 50 + 50)))
    start1 = pygame.font.Font('assets/font/Minecraft.ttf', 30).render("Basic DQN", False, (255, 255, 255))
    win.blit(start1, start1.get_rect(center = (U.X_CENTER, U.SCALE * 50 + 150)))
    button1 = start1.get_rect(center = (U.X_CENTER, U.SCALE * 50 + 150))
    start2 = pygame.font.Font('assets/font/Minecraft.ttf', 30).render("Self Play DRQN", False, (255, 255, 255))
    win.blit(start2, start2.get_rect(center = (U.X_CENTER, U.SCALE * 50 + 200)))
    button2 = start1.get_rect(center = (U.X_CENTER, U.SCALE * 50 + 200))
    start3 = pygame.font.Font('assets/font/Minecraft.ttf', 30).render("Decent Bot", False, (255, 255, 255))
    win.blit(start3, start3.get_rect(center = (U.X_CENTER, U.SCALE * 50 + 250)))
    button3 = start1.get_rect(center = (U.X_CENTER, U.SCALE * 50 + 250))
    start4 = pygame.font.Font('assets/font/Minecraft.ttf', 30).render("Devious Bot", False, (255, 255, 255))
    win.blit(start4, start4.get_rect(center = (U.X_CENTER, U.SCALE * 50 + 300)))
    button4 = start1.get_rect(center = (U.X_CENTER, U.SCALE * 50 + 300))
    start5 = pygame.font.Font('assets/font/Minecraft.ttf', 30).render("Greedy Bot", False, (255, 255, 255))
    win.blit(start5, start5.get_rect(center = (U.X_CENTER, U.SCALE * 50 + 350)))
    button5 = start1.get_rect(center = (U.X_CENTER, U.SCALE * 50 + 350))
    start6 = pygame.font.Font('assets/font/Minecraft.ttf', 30).render("Angry Bot", False, (255, 255, 255))
    win.blit(start6, start6.get_rect(center = (U.X_CENTER, U.SCALE * 50 + 400)))
    button6 = start1.get_rect(center = (U.X_CENTER, U.SCALE * 50 + 400))
    start7 = pygame.font.Font('assets/font/Minecraft.ttf', 30).render("Truthful Bot", False, (255, 255, 255))
    win.blit(start7, start7.get_rect(center = (U.X_CENTER, U.SCALE * 50 + 450)))
    button7 = start1.get_rect(center = (U.X_CENTER, U.SCALE * 50 + 450))
    # other = pygame.font.Font('assets/font/Minecraft.ttf', 20).render("Press s to start after selecting difficulty", False, (255, 255, 255))
    # win.blit(other, other.get_rect(center = (U.X_CENTER, U.SCALE * 50 + 550)))
    if gamemode < 0:
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_m]):
            network = Network()
            if network.client == None:
                network.conn()
            gamemode = 0
        # if (keys[pygame.K_s]):      # or True = always single player right now :)
        #     gamemode = 1
        # if (keys[pygame.K_t]):      # or True = always single player right now :)
        #     gamemode = 3
    else:
        game_engine.set_gamemode(gamemode)
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
    if game_engine.gamemode == 0 and network != None and network.client != None:
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
    global gamemode
    # load stuff and classes
    U.load_ALL_MOVES()

    game_engine = Game_Engine()
    card_engine_display = Card_Engine_Display(no_shuffle=False)
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

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if button1.collidepoint(event.pos):
                        print('1.')
                        gamemode = 1
                    if button2.collidepoint(event.pos):
                        print('2.')
                        gamemode = 2
                    if button3.collidepoint(event.pos):
                        print('3.')
                        gamemode = 3
                    if button4.collidepoint(event.pos):
                        print('4.')
                        gamemode = 4
                    if button5.collidepoint(event.pos):
                        print('5.')
                        gamemode = 5
                    if button6.collidepoint(event.pos):
                        print('6.')
                        gamemode = 6
                    if button7.collidepoint(event.pos):
                        print('7.')
                        gamemode = 7

        win.fill((0, 0, 0))
        
        curr_gui = gui.get(curr_gui)(game_engine, [stage, card_engine_display])
        # if not network.client == None:
        #     network.send("asdf")

        clock.tick(FPS)
        pygame.display.update()


if __name__ == "__main__":
    main()