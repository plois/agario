import pygame
from settings import *


class Grid():
    def __init__(self, screen):
        self.screen = screen
        self.x = 0
        self.y = 0
        self.start_size = 200
        self.size = self.start_size

    def update(self, r_x, r_y, L):
        self.size = self.start_size // L
        self.x = -self.size + (-r_x) % (self.size)
        self.y = -self.size + (-r_y) % (self.size)

    def draw(self):
        for i in range(WIDTH // self.size + 2):
            pygame.draw.line(self.screen, GRID_COLOR,
                             [self.x + i * self.size, 0],
                             [self.x + i * self.size, HEIGHT],
                             1)
        for i in range(HEIGHT // self.size + 2):
            pygame.draw.line(self.screen, GRID_COLOR,
                             [0, self.y + i * self.size],
                             [WIDTH, self.y + i * self.size],
                             1)
