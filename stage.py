import pygame

import utils as U

LENGTH = 96 * U.SCALE
SPACING = 48 * U.SCALE

# mat class (piste is made out of multiple mats)

# class Mat():
#     def __init__(self) -> None:
#         pass

# stage class

class Stage():
    def __init__(self, piste_length: int) -> None:
        self.piste_length = piste_length
        # self.piste = [Mat() for i in range(self.piste_length)]              # use this once sprites are made and put them in mat class

    def update(self, win: pygame.Surface) -> None:
        self.render_mats(win)
        # pygame.draw.rect(win, (255, 0, 0), (U.X_CENTER - 2, U.Y_CENTER - 2, 4, 4))        # true center

    def reset(self) -> None:
        pass
    
    def render_mats(self, win: pygame.Surface) -> None:
        for i in range(self.piste_length):
            # win.blit(img, (), ())     # sprite holder
            pygame.draw.rect(
                win, (255, 255, 255), (U.X_CENTER - LENGTH / 2 + ((LENGTH + SPACING) * (-1 if i % 2 == 1 else 1) * ((i + 1) // 2)), U.Y_CENTER, LENGTH, 5))
