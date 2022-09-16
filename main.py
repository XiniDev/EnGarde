from sys import exit
import socket
from this import d

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
        self.length = 8
        self.piste = [Mat() for i in range(self.length)]

    def update(self) -> None:
        pass
    
    def render_mats(self) -> None:
        # X_CENTER = WIDTH / 2
        # Y_CENTER = HEIGHT / 2
        # for i in range(self.length):
            # win.blit(img, (), ())
        pass

# connection function

def conn():

    # connect to server
    global client
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((IP, PORT))

# main function

def main():

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

        clock.tick(FPS)
        pygame.display.update()


if __name__ == "__main__":
    main()