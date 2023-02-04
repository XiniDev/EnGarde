
import utils as U

from stage import *
from card_engine import *
from game_engine import *

import pygame

# initialisation

CAPTION = "En-Garde!"
FPS = 60
SCREEN_SIZE = (U.WIDTH, U.HEIGHT)

class Game:
    def __init__(self) -> None:
        # gui stuff
        self.curr_gui = 'menu'

        self.init()

    def init(self) -> None:
        # pygame init
        pygame.init()

        self.win = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption(CAPTION)
        self.clock = pygame.time.Clock()

        # load stuff and classes

        U.load_ALL_MOVES()

        self.game_engine = Game_Engine()

        self.card_engine_display = Card_Engine_Display(no_shuffle=False)
        self.stage = Stage(U.PISTE_LENGTH)

        # load moves in card
        self.card_engine_display.start(U.ALL_MOVES)
    
    def game_loop(self) -> None:
        # game loop

        while True:
            for event in pygame.event.get():

                # quit game event
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()

                if self.curr_gui == 'game':
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and not self.game_engine.is_turn_running() and not self.game_engine.is_user_done:
                        self.game_engine.move_selection(self.card_engine_display)

            self.win.fill((0, 0, 0))
            
            curr_gui = self.gui.get(curr_gui)(self.game_engine, [self.stage, self.card_engine_display])
            # if not network.client == None:
            #     network.send("asdf")

            self.clock.tick(FPS)
            pygame.display.update()