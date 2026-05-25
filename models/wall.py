import pygame as pg
import constants as cs

class Wall(pg.sprite.Sprite):
    def __init__(self, x, y, size):
        super().__init__()
        self.size = size
        # Create a surface for wall (blue rectangle)
        self.image = pg.Surface((size, size))
        self.image.fill(cs.WALL_COLOR)
        # Set the position
        self.rect = self.image.get_rect()
        self.rect.topleft = (x * size, y * size)