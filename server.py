import socket
from settings import *
import pygame
import random
from models.food import Food
from models.player import Player


def find(s):
    otkr = None
    for i in range(len(s)):
        if s[i] == '<':
            otkr = i
        if s[i] == '>' and otkr != None:
            zakr = i
            res = s[otkr + 1:zakr]
            res = list(map(int, res.split(',')))
            return res
    return ''


def new_val(R, r):
    return (R ** 2 + r ** 2) ** 0.5


main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
main_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
main_socket.bind(('localhost', 10000))
main_socket.setblocking(0)
main_socket.listen(5)

pygame.init()
screen = pygame.display.set_mode((SERVER_WINDOW_WIDTH, SERVER_WINDOW_HEIGHT))
clock = pygame.time.Clock()

players = [Player(None, None, random.randint(0, ROOM_WIDTH),
                  random.randint(0, ROOM_HEIGHT),
                  random.randint(10, 100),
                  str(random.randint(0, 4))) for i in range(mobs_number)]
food_lst = [Food(random.randint(0, ROOM_WIDTH),
                 random.randint(0, ROOM_HEIGHT),
                 food_size, str(random.randint(0, 4))) for i in range(food_number)]
tick = -1

server_works = True
while server_works:
    tick += 1
    clock.tick(FPS)
    if tick == 200:
        try:
            tick = 0
            new_socket, addr = main_socket.accept()
            print('{} connected'.format(addr))

            new_socket.setblocking(0)

            spawn = random.choice(food_lst)
            new_player = Player(new_socket, addr, spawn.x,
                                spawn.y,
                                START_PLAYER_SIZE, str(random.randint(0, 4)))
            food_lst.remove(spawn)
            players.append(new_player)
        except:
            pass
        for i in range(mobs_number - len(players)):
            if len(food_lst) != 0:
                spawn = random.choice(food_lst)
                players.append(Player(None, None, spawn.x, spawn.y,
                                      random.randint(10, 100),
                                      str(random.randint(0, 4))))
                food_lst.remove(spawn)
        new_food = [Food(random.randint(0, ROOM_WIDTH),
                         random.randint(0, ROOM_HEIGHT),
                         food_size, str(random.randint(0, 4))) for i in range(food_number - len(food_lst))]
        food_lst += new_food

    for player in players:
        if player.conn != None:
            try:
                data = player.conn.recv(1024)
                data = data.decode()
                if data[0] == '!':
                    player.ready = True
                else:
                    if data[0] == '.' and data[-1] == '.':
                        player.set_options(data)
                        player.conn.send('{} {}'.format(START_PLAYER_SIZE, player.colour).encode())
                    else:
                        data = find(data)
                        player.change_speed(data)
            except:
                pass
        else:
            if tick == 100:
                data = [random.randint(-100, 100), random.randint(-100, 100)]
                player.change_speed(data)
        player.update()

    visible_balls = [[] for i in range(len(players))]
    for i in range(len(players)):
        for k in range(len(food_lst)):
            dist_x = food_lst[k].x - players[i].x
            dist_y = food_lst[k].y - players[i].y

            if (
                    (abs(dist_x) <= (players[i].w_vision) // 2 + food_lst[k].r)
                    and
                    (abs(dist_y) <= (players[i].h_vision) // 2 + food_lst[k].r)
            ):
                if ((dist_x ** 2 + dist_y ** 2) ** 0.5 <= players[i].r):
                    players[i].r = new_val(players[i].r, food_lst[k].r)
                    food_lst[k].r = 0
                if (players[i].conn != None) and food_lst[k].r != 0:
                    x_ = str(round(dist_x / players[i].L))
                    y_ = str(round(dist_y / players[i].L))
                    r_ = str(round(food_lst[k].r / players[i].L))
                    c_ = food_lst[k].colour

                    visible_balls[i].append('{} {} {} {}'.format(x_, y_, r_, c_))

        for j in range(i + 1, len(players)):
            dist_x = players[j].x - players[i].x
            dist_y = players[j].y - players[i].y
            if (
                    (abs(dist_x) <= (players[i].w_vision) // 2 + players[j].r)
                    and
                    (abs(dist_y) <= (players[i].h_vision) // 2 + players[j].r)
            ):
                if ((dist_x ** 2 + dist_y ** 2) ** 0.5 <= players[i].r and
                        players[i].r > 1.1 * players[j].r):
                    players[i].r = new_val(players[i].r, players[j].r)
                    players[j].r, players[j].speed_x, players[j].speed_y = 0, 0, 0
                if players[i].conn != None:
                    x_ = str(round(dist_x / players[i].L))
                    y_ = str(round(dist_y / players[i].L))
                    r_ = str(round(players[j].r / players[i].L))
                    c_ = players[j].colour
                    n_ = players[j].name

                    if players[j].r >= 30 * players[i].L:
                        visible_balls[i].append('{} {} {} {} {}'.format(x_, y_, r_, c_, n_))
                    else:
                        visible_balls[i].append('{} {} {} {}'.format(x_, y_, r_, c_))

            if (
                    (abs(dist_x) <= (players[j].w_vision) // 2 + players[i].r)
                    and
                    (abs(dist_y) <= (players[j].h_vision) // 2 + players[i].r)
            ):
                if ((dist_x ** 2 + dist_y ** 2) ** 0.5 <= players[j].r and
                        players[j].r > 1.1 * players[i].r):
                    players[j].r = new_val(players[j].r, players[i].r)
                    players[i].r, players[i].speed_x, players[i].speed_y = 0, 0, 0

                if players[j].conn != None:
                    x_ = str(round(-dist_x / players[j].L))
                    y_ = str(round(-dist_y / players[j].L))
                    r_ = str(round(players[i].r / players[j].L))
                    c_ = players[i].colour
                    n_ = players[i].name

                    if players[i].r >= 30 * players[j].L:
                        visible_balls[j].append('{} {} {} {} {}'.format(x_, y_, r_, c_, n_))
                    else:
                        visible_balls[j].append('{} {} {} {}'.format(x_, y_, r_, c_))

    responses = ['' for i in range(len(players))]
    for i in range(len(players)):
        r_ = str(round(players[i].r / players[i].L))
        x_ = str(round(players[i].x / players[i].L))
        y_ = str(round(players[i].y / players[i].L))
        L_ = str(players[i].L)
        visible_balls[i] = ['{} {} {} {}'.format(r_, x_, y_, L_)] + visible_balls[i]
        responses[i] = '<' + (','.join(visible_balls[i])) + '>'

    for i in range(len(players)):
        if players[i].conn != None and (players[i].ready):
            try:
                players[i].conn.send(responses[i].encode())
                players[i].errors = 0
            except:
                players[i].errors += 1

    for player in players:
        if (player.errors == 500) or (player.r == 0):
            if player.conn != None:
                player.conn.close()
            players.remove(player)

    for m in food_lst:
        if m.r == 0: food_lst.remove(m)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            server_works = False

    screen.fill('BLACK')
    for player in players:
        x = round(player.x * SERVER_WINDOW_WIDTH / ROOM_WIDTH)
        y = round(player.y * SERVER_WINDOW_HEIGHT / ROOM_HEIGHT)
        r = round(player.r * SERVER_WINDOW_HEIGHT / ROOM_HEIGHT)
        c = colours[player.colour]

        pygame.draw.circle(screen, c, (x, y), r)
    pygame.display.update()

pygame.quit()
main_socket.close()
