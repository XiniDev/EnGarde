from sys import exit

import pygame

pygame.init()

# initialisation

CAPTION = "En-Garde!"
WIDTH = 1280
HEIGHT = 720
FPS = 60
SCREEN_SIZE = (WIDTH, HEIGHT)

pygame.init()

win = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption(CAPTION)
clock = pygame.time.Clock()

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

        clock.tick(FPS)
        pygame.display.update()


if __name__ == "__main__":
    main()