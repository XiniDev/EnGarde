import pygame

import constants as C

# mat class (piste is made out of multiple mats)

class Mat():
    def __init__(self) -> None:
        pass

# stage class

class Stage():
    def __init__(self, piste_length: int) -> None:
        self.piste_length = piste_length
        self.piste = [Mat() for i in range(self.piste_length)]              # use this once sprites are made and put them in mat class

    def update(self, win: pygame.Surface) -> None:
        self.render_mats(win)
        pygame.draw.rect(win, (255, 0, 0), (C.X_CENTER - 2, C.Y_CENTER - 2, 4, 4))        # true center
    
    def render_mats(self, win: pygame.Surface) -> None:
        LENGTH = 10 * C.SCALE            # temp length until i make mat sprite :)
        SPACING = 5 * C.SCALE
        for i in range(self.piste_length):
            # win.blit(img, (), ())     # sprite holder
            pygame.draw.rect(
                win, (255, 255, 255), (C.X_CENTER - LENGTH / 2 + ((LENGTH + SPACING) * (-1 if i % 2 == 1 else 1) * ((i + 1) // 2)), C.Y_CENTER, LENGTH, 5))
