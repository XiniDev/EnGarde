import pygame
import utils as U

# player class

class Player():
    def __init__(self, is_user: bool) -> None:
        self.is_user = is_user
        self.mat_pos = -1 if self.is_user else 1

        self.width = 10 * U.SCALE
        self.height = 10 * U.SCALE
        self.pos_x = self.set_pos_x()
        self.pos_y = U.Y_CENTER - U.SCALE - self.height

        # player states variables
        self.charge = 0
        self.stance = False

    def update(self, win: pygame.Surface) -> None:
        self.render_player(win)
    
    def render_player(self, win: pygame.Surface) -> None:
        pygame.draw.rect(win, (0, 255 if self.is_user else 0, 0 if self.is_user else 255), (self.pos_x, self.pos_y, self.width, self.height))

    def set_pos_x(self) -> int:
        return self.mat_pos * (10 * U.SCALE + 40) + U.X_CENTER - self.width / 2

    def pos_update(self, steps: int, frames: int, total_frames: int) -> None:
        if not self.is_user:
            steps *= -1
        if frames == total_frames:
            self.mat_pos += steps
            self.pos_x = self.set_pos_x()
        else:
            self.pos_x += (steps * (10 * U.SCALE + 40)) / total_frames
    
    def reset_pos(self) -> None:
        self.mat_pos = -1 if self.is_user else 1
        self.pos_x = self.set_pos_x()
    
    def reset_states(self) -> None:
        self.charge = 0
        self.stance = False
