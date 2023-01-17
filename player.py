import pygame
import utils as U

from action import *
from stage import LENGTH as MAT_LENGTH, SPACING as MAT_SPACING

import math

# load animation images

PLAYER_IMG_WIDTH = 640 * U.IMG_SCALE
PLAYER_IMG_HEIGHT = 360 * U.IMG_SCALE

SPRITE_FRAMES = 4

player_img = pygame.image.load("assets/sprites/character.png")
player_2_img = pygame.transform.scale(player_img, (PLAYER_IMG_WIDTH, PLAYER_IMG_HEIGHT))
player_1_img = pygame.transform.flip(player_2_img, True, False)
player_imgs = [player_1_img, player_2_img]

# player class

class Player():
    def __init__(self, is_user: bool) -> None:
        self.is_user = is_user
        self.mat_pos = -1 if self.is_user else 1

        self.width = 45 * U.IMG_SCALE
        self.height = 30 * U.IMG_SCALE
        self.pos_x = self.set_pos_x()
        self.pos_y = U.Y_CENTER - U.IMG_SCALE - self.height

    def update(self, is_running_turn: bool, win: pygame.Surface, player: int, frames: int, action: Action, states: dict[str, int]) -> None:
        self.render_player(is_running_turn, win, player, frames, action, states)
    
    def render_player(self, is_running_turn: bool, win: pygame.Surface, player: int, frames: int, action: Action, states: dict[str, int]) -> None:
        # pygame.draw.rect(win, (0, 255 if self.is_user else 0, 0 if self.is_user else 255), (self.pos_x, self.pos_y, self.width, self.height))
        
        frame_x = 0
        frame_increment = math.floor(frames / (U.ANIMATION_FRAMES / SPRITE_FRAMES)) % 4 if frames >= 0 else 0
        if player == 0:
            frame_x = PLAYER_IMG_WIDTH - self.width - self.width * frame_increment
        else:
            frame_x = self.width * frame_increment

        action_num = U.action_to_numeric(action)

        frame_y = self.height * (action_num - 1) if is_running_turn else self.height * 4

        # mini movements
        # without changing actual pos_x, use temp to display short burst of movement
        temp_pos_x = self.pos_x
        if isinstance(action, Hit) or isinstance(action, Smash):
            if frames != -1:
                movement = frames if frames < U.ANIMATION_FRAMES / 2 else U.ANIMATION_FRAMES - frames
                temp_pos_x += (player - 0.5) * -5 * movement * U.IMG_SCALE
        
        win.blit(player_imgs[player], (temp_pos_x, self.pos_y), ((frame_x, frame_y, self.width, self.height)))


    def set_pos_x(self) -> int:
        return self.mat_pos * (MAT_LENGTH + MAT_SPACING) + U.X_CENTER - self.width / 2

    def pos_update(self, steps: int, frames: int) -> None:
        if not self.is_user:
            steps *= -1
        if frames == U.ANIMATION_FRAMES:
            self.mat_pos += steps
            self.pos_x = self.set_pos_x()
        else:
            self.pos_x += (steps * (MAT_LENGTH + MAT_SPACING)) / U.ANIMATION_FRAMES
    
    def reset_pos(self) -> None:
        self.mat_pos = -1 if self.is_user else 1
        self.pos_x = self.set_pos_x()
