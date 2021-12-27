from settings import *


class Player():
    def __init__(self, conn, addr, x, y, r, colour):
        self.conn = conn
        self.addr = addr
        self.x = x
        self.y = y
        self.r = r
        self.colour = colour

        self.L = 1
        self.width_window = WIDTH
        self.height_window = HEIGHT
        self.w_vision = WIDTH
        self.h_vision = HEIGHT
        self.name = 'Bot'

        self.errors = 0
        self.ready = False

        self.abs_speed = 30 / (self.r ** 0.5)
        self.speed_x = 0
        self.speed_y = 0

    def set_options(self, data):
        data = data[1:-1].split(' ')
        self.name = data[0]
        self.width_window = int(data[1])
        self.height_window = int(data[2])
        self.w_vision = int(data[1])
        self.h_vision = int(data[2])

    def change_speed(self, v):
        if (v[0] == 0) and (v[1] == 0):
            self.speed_x = 0
            self.speed_y = 0
        else:
            lenv = (v[0] ** 2 + v[1] ** 2) ** 0.5
            v = (v[0] / lenv, v[1] / lenv)
            v = (v[0] * self.abs_speed, v[1] * self.abs_speed)
            self.speed_x, self.speed_y = v[0], v[1]

    def update(self):
        if self.x - self.r <= 0:
            if self.speed_x >= 0:
                self.x += self.speed_x
        else:
            if self.x + self.r >= ROOM_WIDTH:
                if self.speed_x <= 0:
                    self.x += self.speed_x
            else:
                self.x += self.speed_x

        if self.y - self.r <= 0:
            if self.speed_y >= 0:
                self.y += self.speed_y
        else:
            if self.y + self.r >= ROOM_HEIGHT:
                if self.speed_y <= 0:
                    self.y += self.speed_y
            else:
                self.y += self.speed_y

        self.abs_speed = 30 / (self.r ** 0.5)

        if self.r >= 100:
            self.r -= self.r / 17500

        if (self.r >= self.w_vision / 4) or (self.r >= self.h_vision / 4):
            if self.w_vision <= ROOM_WIDTH or self.h_vision <= ROOM_HEIGHT:
                self.L *= 2
                self.w_vision = self.width_window * self.L
                self.h_vision = self.height_window * self.L
        if (self.r < self.w_vision / 8) and (self.r < self.h_vision / 8):
            if self.L > 1:
                self.L = self.L / 2
                self.w_vision = self.width_window * self.L
                self.h_vision = self.height_window * self.L
