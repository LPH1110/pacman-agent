import pygame as pg
import constants as cs

class Pacman(pg.sprite.Sprite):
    def __init__(self, x, y, size):
        super().__init__()
        self.size = size
        self.image = pg.Surface((size, size), pg.SRCALPHA)
        pg.draw.circle(
            surface = self.image, 
            color = cs.PACMAN_COLOR, 
            center = (size // 2, size // 2), 
            radius = size // 3
        )
        # Set the position
        self.rect = self.image.get_rect()
        self.rect.topleft = (x * size, y * size)

    def update(self, x, y):
        self.rect.topleft = (x * self.size, y * self.size)
        