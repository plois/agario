import socket
import pygame
from settings import *
from models.grid import Grid

name = 'primewave'


class Local_player():
    def __init__(self, data):
        data = data.split()
        self.r = int(data[0])
        self.colour = data[1]

    def update(self, new_r):
        self.r = new_r

    def draw(self):
        if self.r != 0:
            pygame.draw.circle(screen, colours[self.colour],
                               (WIDTH // 2, HEIGHT // 2), self.r)
        write_name(WIDTH // 2, HEIGHT // 2, self.r, name)


def draw_opponents(data):
    for i in range(len(data)):
        j = data[i].split(' ')

        x = WIDTH // 2 + int(j[0])
        y = HEIGHT // 2 + int(j[1])
        r = int(j[2])
        c = colours[j[3]]
        pygame.draw.circle(screen, c, (x, y), r)

        if len(j) == 5: write_name(x, y, r, j[4])


def write_name(x, y, r, n):
    font = pygame.font.Font(None, r)
    text = font.render(n, True, (0, 0, 0))
    rect = text.get_rect(center=(x, y))
    screen.blit(text, rect)


def find(s):
    otkr = None
    for i in range(len(s)):
        if s[i] == '<':
            otkr = i
        if s[i] == '>' and otkr is not None:
            zakr = i
            res = s[otkr + 1:zakr]
            return res
    return ''


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))

pygame.display.set_caption('Bebra online')

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
sock.connect(('localhost', 10000))

sock.send('.{} {} {}.'.format(name, WIDTH, HEIGHT).encode())

data = sock.recv(64).decode()
sock.send('!'.encode())
client = Local_player(data)
grid = Grid(screen)

old_v = (0, 0)
running = True
while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if pygame.mouse.get_focused():
        pos = pygame.mouse.get_pos()
        v = (pos[0] - WIDTH // 2, pos[1] - HEIGHT // 2)

        if v[0] ** 2 + v[1] ** 2 <= client.r ** 2:
            v = (0, 0)

        if v != old_v:
            old_v = v
            message = '<{},{}>'.format(v[0], v[1])
            sock.send(message.encode())

    data = sock.recv(2 ** 20)
    data = data.decode()
    data = find(data)
    data = data.split(',')

    if data != ['']:
        parametrs = list(map(int, data[0].split(' ')))
        client.update(parametrs[0])
        grid.update(parametrs[1], parametrs[2], parametrs[3])

        screen.fill('gray25')
        grid.draw()
        draw_opponents(data[1:])
        client.draw()

    pygame.display.update()

pygame.quit()
