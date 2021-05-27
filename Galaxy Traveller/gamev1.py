import os
import random
import pygame
from pygame import *
from array import *

path = os.path.dirname(os.path.abspath(__file__))
img_path = f"{path}/images"

pygame.init()
pygame.display.init()

BLACK  = (  0,   0,   0)
WHITE  = (255, 255, 255)
BLUE   = (  0,   0, 255)
RED    = (255,   0,   0)
GREEN  = (  0, 255,   0)
YELLOW = (255, 255,   0)
CYAN   = (  0, 255, 255)
PURPLE = (255,   0, 255)
GREY   = pygame.color.Color('grey')

score_height = 90 # >= image du score

screen_size = screen_width, screen_height = 800, 600+score_height
screen = pygame.display.set_mode((screen_width, screen_height))

game_part = pygame.surface.Surface((screen_width, screen_height-score_height))
game_rect = game_part.get_rect()

score_part = pygame.surface.Surface((screen_width, score_height))
score_rect = score_part.get_rect()

scoreboard_img = pygame.image.load(f"{img_path}/scoreboard_transparent.png").convert_alpha()
scoreboard_rect = scoreboard_img.get_rect()

offsetx = int(abs(score_rect.width  - scoreboard_rect.w)/2)
offsety = int(abs(score_rect.height - scoreboard_rect.h)/2)

cell_size = 50
cell_margin = 2
cells = (board_x, board_y) = int(game_rect.width / cell_size), int(game_rect.height / cell_size)  # taille du board en coordonnées cell
cells_nb = board_x * board_y

board = []
for j in range (board_y):
    b=[]
    for i in range (board_x):
        b.append(0)
    board.append(b)

def display_board():
    global board_x, board_y
    for j in range(board_y):
        for i in range(board_x):
            print(board[j][i] , " ",end="")
        print()

def get_board(x,y):
    global board
    return board[y-1][x-1]

def set_board(x,y,v):
    global board
    board[y-1][x-1] = v

EMPTY   = 0
PLAYER1 = 1
PLAYER2 = 2
MARKET  = 3
ZONE    = 4
DEFAULT_COLOR = 5

NOP = ' '
ADD = 'a'
SUB = 's'

#player1,player2
colors     = [BLUE, GREEN]
credits    = [10, 10]
warps      = [10, 10]
dices      = [ 1,  1]
regions    = [ 0,  0]
last_cell  = [(0,0),(0,0)]
left_cells = cells_nb

PEN_EMPTY    = 0
PEN_CURRENT  = 5
board_colors = [YELLOW, colors[0], colors[1], RED, BLACK, CYAN]
#print(board_colors)

# logo market
mkt_logo = pygame.image.load(f"{img_path}/market_logo_transparent.png").convert_alpha()

# cells market
mktcells = []

# score
police = pygame.font.Font('freesansbold.ttf', 60)

def update_scoreboard(p1, w1, c1, r1, p2, w2, c2, r2, backgroundcolor):
    global score_part, police
    w1r = Rect( 15+offsetx, 52+offsety,  93- 15, 80-52)
    c1r = Rect(106+offsetx, 52+offsety, 178-106, 80-52)
    r1r = Rect(191+offsetx, 52+offsety, 269-191, 80-52)
    w2r = Rect(367+offsetx, 52+offsety, 445-367, 80-52)
    c2r = Rect(458+offsetx, 52+offsety, 531-458, 80-52)
    r2r = Rect(544+offsetx, 52+offsety, 621-544, 80-52)
    w1t = str(w1)
    c1t = str(c1)
    r1t = str(r1)
    w2t = str(w2)
    c2t = str(c2)
    r2t = str(r2)
    w1tr = police.render(w1t, True, board_colors[p1])
    c1tr = police.render(c1t, True, board_colors[p1])
    r1tr = police.render(r1t, True, board_colors[p1])
    w2tr = police.render(w2t, True, board_colors[p2])
    c2tr = police.render(c2t, True, board_colors[p2])
    r2tr = police.render(r2t, True, board_colors[p2])

    w1trs = pygame.transform.scale(w1tr, (w1r.w,w1r.h))
    c1trs = pygame.transform.scale(c1tr, (c1r.w,w1r.h))
    r1trs = pygame.transform.scale(r1tr, (r1r.w,w1r.h))
    w2trs = pygame.transform.scale(w2tr, (w2r.w,w2r.h))
    c2trs = pygame.transform.scale(c2tr, (c2r.w,c2r.h))
    r2trs = pygame.transform.scale(r2tr, (r2r.w,r2r.h))

    pygame.draw.rect(score_part, RED, w1r)
    pygame.draw.rect(score_part, backgroundcolor, c1r)
    pygame.draw.rect(score_part, RED, r1r)
    pygame.draw.rect(score_part, backgroundcolor, w2r)
    pygame.draw.rect(score_part, RED, c2r)
    pygame.draw.rect(score_part, backgroundcolor, r2r)

    score_part.blit(w1trs, w1r)
    score_part.blit(c1trs, c1r)
    score_part.blit(r1trs, r1r)
    score_part.blit(w2trs, w2r)
    score_part.blit(c2trs, c2r)
    score_part.blit(r2trs, r2r)

def dice():
    return random.randint(1,6)

def in_range(v, min, max):
    if v < min:
        v = min
    if v > max:
        v = max
    return int(v)

# cell occupée ?
def cell_owned(cx, cy):
    b = get_board(cx,cy)
    return b != EMPTY

# à partir du N° de la cell, rend ses coordonnées cell
def cell_coord_pos(cell_num):
    global cells

    if cell_num > cells_nb:
        return(1/0,1/0)

    i=1
    while i <= board_x:
        line = i*board_x
        if cell_num < line:
            y = i
            x = cell_num - (i-1)*board_x
            break
        i=i+1

    return (x,y)

# à partir des coordonnées cellx,celly, donne le numéro de la cell
def cell_coord_pos_num(x,y):
    global cells
    cell_num = x + (y-1)*board_x
    return cell_num

# à partir du N° de la cell, rend un rectangle de coordonnées screen
def cell_coord_rect(cell_num):
    (x,y) = cell_coord_pos(cell_num)
    if x < 1:
        x = 1
    if y < 1:
        y = 1
    xx = (x-1)*cell_size
    yy = (y-1)*cell_size
    return Rect( int(xx+cell_margin), int(yy+cell_margin), int(cell_size-cell_margin-1), int(cell_size-cell_margin-1) )

def cell_coord_pos_rect(cell_x, cell_y):
    global cells
    cell_x = in_range(cell_x, 1, board_x)
    cell_y = in_range(cell_y, 1, board_y)
    xx = (cell_x-1)*cell_size
    yy = (cell_y-1)*cell_size
    return Rect( int(xx+cell_margin), int(yy+cell_margin), int(cell_size-cell_margin-1), int(cell_size-cell_margin-1) )

# à partir d'une coordonnée screen, rend les coordonnées cell
def cell_coord_from_screen(x, y):
    global game_rect,cell_size
    x = in_range(x, 0, game_rect.width)
    y = in_range(y, 0, game_rect.height)
    cell_x = int(x / cell_size)+1
    cell_y = int(y / cell_size)+1
    return (cell_x,cell_y)

def draw_board():
    global game_part,game_rect
    game_part.fill(YELLOW)
    pygame.draw.rect(game_part, BLACK, game_rect, 1)

    for x in range(0, game_rect.width, cell_size):
        pygame.draw.line(game_part, RED, (x, 0), (x, game_rect.height), 1)

    for y in range(0, game_rect.height, cell_size):
        pygame.draw.line(game_part, RED, (0, y), (game_rect.width, y), 1)

def draw_scoreboard():
    global scoreboard_img
    score_part.fill(GREY)
    score_part.blit(scoreboard_img, (offsetx,offsety))

asteroids = pygame.image.load(f"{img_path}/asteroids.png").convert_alpha()
blackhole = pygame.image.load(f"{img_path}/blackhole.png").convert_alpha()
space     = pygame.image.load(f"{img_path}/space.png").convert_alpha()
sun       = pygame.image.load(f"{img_path}/sun.png").convert_alpha()

zs = [asteroids, blackhole, space, sun]

zones_cells = []
def create_zones():
    global cells_nb, zones_cells, zs, board_x, board_y
    iz=0
    bx2 = int(board_x/2)
    by2 = int(board_y/2)
    for mx in range(2):
        for my in range(2):
            quadx = mx*bx2
            quady = my*by2
            z = zs[iz]
            iz += 1
            r = z.get_rect()
            w,h = round(r.width/cell_size), round(r.height/cell_size)
            cells_nb -= w * h
            rx = random.randint(1, bx2-w)
            ry = random.randint(1, by2-h)
            print("rx,ry=",rx,ry)
            rndx = rx + quadx
            rndy = ry + quady
            print("rndx,rndy=",rndx,rndy)
            for x in range(w):
                xx = x+1+rndx
                for y in range(h):
                    yy = y+1+rndy
                    set_board(xx, yy, ZONE)
                    zones_cells.append((xx,yy))
            zt = pygame.transform.scale(z, (w*cell_size,h*cell_size))
            game_part.blit(zt, ((rndx)*cell_size, (rndy)*cell_size))

    #display_board()
    #print(zones_cells)


def create_markets():
    global cells_nb, mktcells, zones_cells
    nbmkt = random.randint(4, 6)
    cells_nb -= nbmkt
    for n in range(nbmkt):
        while True:
            cn = random.randint(1, cells_nb)
            c = (i, j) = cell_coord_pos(cn)
            if c in zones_cells:
                continue
            #print(cn,c,i,j)
            set_board(i, j, MARKET)
            mktcells.append(c)
            break


def draw_markets():
    global game_part, mktcells, mkt_logo, score_rect
    for c in mktcells:
        cell_rect = cell_coord_pos_rect(c[0], c[1])
        #print("draw_markets, cell_rect=", cell_rect)
        game_part.blit(mkt_logo, (cell_rect.x, cell_rect.y))
    display_board()

draw_board()
draw_scoreboard()
create_zones()
create_markets()
draw_markets()

players_path = [[],[]]

cell_prev = (0,0)

# pas de diagonale


def adjacent(cell_cur, testcell):
    (xc,yc) = cell_cur
    (xl,yl) = testcell
    xd = abs(xc-xl)
    yd = abs(yc-yl)
    if (xd == 0 and yd == 1) or (yd == 0 and xd == 1) :
        return True
    return False

def add_cell(player, cell_cur, b):
    global credits, warps, players_path, last_cell
    print("ADD", "b=", b, "w=", warps[player], "cell_cur", cell_cur,
          "path=", players_path[player], ', last_cell=', last_cell, last_cell[player])
    if cell_cur in players_path[player]:
        return False
    if len(players_path[player]) < 1 and last_cell[player] != (0, 0) and not adjacent(cell_cur, last_cell[player]):
        return False
    if warps[player] < 1:
        return False
    if len(players_path[player]) > 0 and not adjacent(cell_cur, players_path[player][-1]):
        return False
    if b == ZONE:
        return False
    print("ADD2")
    players_path[player].append(cell_cur)
    print("ADD3", "path=", players_path[player])
    if b == EMPTY:
        credits[player] += 1
    warps[player] -= 1
    return True

def sub_cell(player, cell_cur, b):
    global credits, warps, players_path
    if cell_cur in players_path[player]:
        players_path[player].remove(cell_cur)
        if b == EMPTY:
            credits[player] -= 1
        warps[player] += 1
    print("SUB", b, warps[player], cell_cur, players_path[player])
    return True

cell_mouse = (0,0)
def manage_cell(player):
    global game_part, cell_prev, cell_mouse
    mouse_x, mouse_y = pygame.mouse.get_pos()
    #print(mouse_x, mouse_y)
    if mouse_y < score_height:
        return
    mouse_click = pygame.mouse.get_pressed(3)
    cell_cur = (cell_x, cell_y) = cell_coord_from_screen(mouse_x, mouse_y-score_height)
    if cell_mouse == cell_cur and mouse_click == (0, 0, 0):
        return
    cell_mouse = cell_cur
    b = get_board(cell_x, cell_y)
    ok = False
    pen = PEN_CURRENT
    if mouse_click == (0, 0, 0):
        op = NOP
    if mouse_click == (1, 0, 0):
        op = ADD
        ok = add_cell(player, cell_cur, b)
    if mouse_click == (0, 0, 1):
        op = SUB
        ok = sub_cell(player, cell_cur, b)
    if ok:
        pen = player+1
    #print("manage_cell","ok=",ok,"b=",b,"pen=",pen,"color",board_colors[pen])
    if b == EMPTY:
        if cell_cur in players_path[player]:
            pen = player+1

        cell_cur_rect = cell_coord_pos_rect(cell_x, cell_y)
        pygame.draw.rect(game_part, board_colors[pen], cell_cur_rect, 0)

    if cell_cur != cell_prev:
        if not cell_prev in players_path[player]:
            #print("manage_cell2 ", "cell_cur=", cell_cur,"cell_prev=",cell_prev )
            bprev = get_board(cell_prev[0], cell_prev[1])
            if bprev == EMPTY:
                cell_prev_rect = cell_coord_pos_rect(cell_prev[0], cell_prev[1])
                pygame.draw.rect(
                    game_part, board_colors[bprev], cell_prev_rect, 0)
        cell_prev = cell_cur


def manage_cell2(player):
    global game_part, cell_prev, left_cells, players_path, mktcells, mkt_logo
    mouse_x, mouse_y = pygame.mouse.get_pos()
    if mouse_y < score_height:
        return
    mouse_click = pygame.mouse.get_pressed(3)
    color = CYAN
    cell_cur = (cell_x,cell_y) = cell_coord_from_screen(mouse_x, mouse_y-score_height)
    if mouse_click == (0,0,0):
        op = NOP
    if mouse_click == (1,0,0):
        op = ADD
        if not cell_cur in players_path[player]:
            if len(players_path[player]) == 0:
                if (last_cell[player] != (0, 0) and adjacent(cell_cur, last_cell[player])) or adjacent(cell_cur, players_path[player][-1]):
                    if warps[player] > 0:
                        credits[player] += 1
                        warps[player] -= 1
                        players_path[player].append(cell_cur)
    if mouse_click == (0,0,1):
        op = SUB
        #print(mouse_click)
        if cell_cur in players_path[player][-1]:  #oblige à prendre le dernier
            credits[player] -= 1
            warps[player] += 1
            players_path[player].remove(cell_cur)
    if cell_cur in players_path[player]:
        color = colors[player]
    cell_cur_rect = cell_coord_pos_rect(cell_x, cell_y)
    if not cell_cur in mktcells:
        pygame.draw.rect(game_part, color, cell_cur_rect, 0)
    if cell_cur != cell_prev:
        cell_prev_rect = cell_coord_pos_rect(cell_prev[0], cell_prev[1])
        #print(cell_cur, cell_prev, cell_cur_rect, cell_prev_rect)
        if not cell_prev in mktcells:
            if not cell_prev in players_path[player]:
                pygame.draw.rect(game_part, YELLOW, cell_prev_rect, 0)
        else:
            if not cell_prev in players_path[player]:
                game_part.blit(
                    mkt_logo, (cell_prev_rect[0], cell_prev_rect[1]))
        cell_prev = cell_cur

def draw_scores():
    global credits, warps, regions
    player1=0
    player2=1
    update_scoreboard(player1, warps[player1], credits[player1], regions[player1],
                      player2, warps[player2], credits[player2], regions[player2],
                      WHITE)

    return 0

def show_dices(c,w):
    return 0

def accept_dices(c,w):
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_y:
                return True
            return False

def throw_dices(player):
    if players_path[player][-1] in mktcells:
        c = dice()
        w = dice()
        show_dices(c,w)
        if accept_dices(c, w):
            dices[player] -= 1
            if dices[player] == 0:
                credits[player] -= c
                warps[player] += w
    #print("credits=",credits,", warps=", warps)

def update_board(cx,cy,op,player):
    global board
    if op == ADD:
        if get_board(cx,cy) == EMPTY:
            set_board(cx,cy,player+1)
    if op == SUB:
        if get_board(cx, cy) == (player+1):
            set_board(cx,cy,EMPTY)

def reset_path(player):
    global game_part, players_path, left_cells, last_cell
    for (cx,cy) in players_path[player]:
        cell_rect = cell_coord_pos_rect(cx, cy)
        color = board_colors[get_board(cx,cy)]
        pygame.draw.rect(game_part, color, cell_rect, 0)
        credits[player] -= 1
        warps[player] += 1
    players_path[player] = []
    draw_markets()

def turn(player):
    global cell_prev, left_cells, regions, last_cell
    cell_prev = (0,0)
    for (cx, cy) in players_path[player]:
        update_board(cx, cy, ADD, player)
        regions[player] += 1
        left_cells -= 1
    print(  "turn player=:", player,
            "players_path=", players_path[player],
            "left_cells=", left_cells,
            "credits=", credits[player],
            "warps=",warps[player],
            "next=", 1-player)
    display_board()
    last_cell[player] = players_path[player][-1]
    players_path[player] = []
    dices[player] = 1
    draw_scores()
    return 1-player

def game_over():
    print("Game Over")

draw_scores()

def loop():
    player = 0
    while True:
        for event in pygame.event.get():
            if(event.type==pygame.QUIT or (event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE)) :
                return

            if left_cells == 0 or (0 in credits) or (0 in warps):
                game_over()
                return

            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEMOTION:
                manage_cell(player)
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE:
                reset_path(player)

            if event.type==pygame.KEYDOWN and event.key==pygame.K_d :
                throw_dices(player)

            if event.type == pygame.KEYDOWN and (event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER):
                player = turn(player)

        screen.blit(score_part, (0, 0))
        screen.blit(game_part, (0, score_rect.h))

        pygame.display.flip()

loop()

pygame.quit()
