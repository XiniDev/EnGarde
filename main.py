from sys import exit
import socket

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

# connection function

def conn():

    # connect to server
    global client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((IP, PORT))

# main function

def main():

    stage = Stage()
    player1 = Player(True)
    player2 = Player(False)

    # game loop

    while True:
        for event in pygame.event.get():

            # quit game event
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        win.fill((0, 0, 0))

        keys = pygame.key.get_pressed()
        if (keys[pygame.K_LSHIFT] and keys[pygame.K_c]):
            if client == None:
                conn()

        stage.update()
        player1.update()
        player2.update()

        clock.tick(FPS)
        pygame.display.update()


if __name__ == "__main__":
    main()