import os
import random
import pygame
from pygame import *
from array import *

pygame.init()

BLACK  = (  0,   0,   0)
WHITE  = (255, 255, 255)
BLUE   = (  0,   0, 255)
RED    = (255,   0,   0)
GREEN  = (  0, 255,   0)
YELLOW = (255, 255,   0)
CYAN   = (  0, 255, 255)
PURPLE = (255,   0, 255)

screen_size = screen_width, screen_height=800,600
screen = pygame.display.set_mode(screen_size)

path = os.path.dirname(os.path.abspath(__file__))
img_path = f"{path}/images"

cell_size = 50
cell_margin = 2
cells = (board_x, board_y) = int(screen_width / cell_size) , int(screen_height / cell_size) #taille du board en coordonnées cell
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
colors  = [BLUE, GREEN]
credits = [10, 10]
warps   = [10, 10]
dices   = [ 1,  1]
left_cells = cells_nb

board_colors = [YELLOW, colors[0], colors[1], RED, BLACK, CYAN]
print(board_colors)

# logo market
mkt_logo = pygame.image.load(f"{img_path}/market_logo_transparent.png").convert_alpha()

# cells market
mktcells = []

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
    global screen_width,screen_height,cell_size
    x = in_range(x, 0, screen_width)
    y = in_range(y, 0, screen_height)
    cell_x = int(x / cell_size)+1
    cell_y = int(y / cell_size)+1
    return (cell_x,cell_y)

def draw_board():
    screen.fill(YELLOW)
    pygame.draw.line(screen, BLACK, (0            , 0)             , (screen_width, 0)              , 1)
    pygame.draw.line(screen, BLACK, (screen_width , 0)             , (screen_width, screen_height)  , 1)
    pygame.draw.line(screen, BLACK, (screen_width , screen_height) , (0           , screen_height)  , 1)
    pygame.draw.line(screen, BLACK, (0            , screen_height) , (0,            0)              , 1)
    for x in range(0,screen_width,cell_size):
        pygame.draw.line(screen, BLACK, (x,0), (x,screen_height), 1)
    for y in range(0,screen_height,cell_size):
        pygame.draw.line(screen, BLACK, (0,y), (screen_width,y), 1)

def create_markets():
    global cells_nb,mktcells
    nbmkt = random.randint(4,6)
    cells_nb -= nbmkt
    for n in range(nbmkt):
        cn = random.randint(1,cells_nb)
        c = (i,j) = cell_coord_pos(cn)
        print(cn,c,i,j)
        set_board(i,j,MARKET)
        mktcells.append(c)

def draw_markets():
    global mktcells,mkt_logo
    for c in mktcells:
        cell_rect = cell_coord_pos_rect(c[0],c[1])
        screen.blit(mkt_logo, (cell_rect.x,cell_rect.y))
    display_board()

def create_zones():
    global cells_nb
    nb_zone_cells = random.randint(15, 20)
    cells_nb -= nb_zone_cells

def draw_zones():
    return 0

draw_board()
create_markets()
draw_markets()
#create_zones()
#draw_zones()

players_path = [[],[]]

cell_prev = (0,0)

# pas de diagonale
def adjacent(cell_cur, playerpath):
    (xc,yc) = cell_cur
    (xl,yl) = last_cell = playerpath[-1]
    xd = abs(xc-xl)
    yd = abs(yc-yl)
    if (xd == 0 and yd == 1) or (yd == 0 and xd == 1) :
        return True
    return False

def add_cell(player, cell_cur, b):
    global credits,warps,players_path
    print("ADD", "b=",b, "w=",warps[player], "cell_cur", cell_cur, "path=",players_path[player])
    if cell_cur in players_path[player]:
        return False
    if warps[player] < 1:
        return False
    if len(players_path[player]) > 0 and not adjacent(cell_cur, players_path[player]):
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
    global cell_prev, cell_mouse
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed(3)
    cell_cur = (cell_x, cell_y) = cell_coord_from_screen(mouse_x, mouse_y)
    if cell_mouse == cell_cur and mouse_click == (0, 0, 0):
        return
    cell_mouse = cell_cur
    b = get_board(cell_x, cell_y)
    pen = DEFAULT_COLOR
    ok = False
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
    print("manage_cell","ok=",ok,"b=",b,"pen=",pen,"color",board_colors[pen])
    if b == EMPTY:
        if cell_cur in players_path[player]:
            pen = player+1
            cell_cur_rect = cell_coord_pos_rect(cell_x, cell_y)
            pygame.draw.rect(screen, board_colors[pen], cell_cur_rect, 0)
    if cell_cur != cell_prev:
        if not cell_prev in players_path[player]:
            print("manage_cell2 ", "cell_cur=", cell_cur,"cell_prev=",cell_prev )
            bprev = get_board(cell_prev[0], cell_prev[1])
            if bprev == EMPTY:
                cell_prev_rect = cell_coord_pos_rect(cell_prev[0], cell_prev[1])
                pygame.draw.rect(screen, board_colors[bprev], cell_prev_rect, 0)
        cell_prev = cell_cur

def draw_path(player):
    global cell_prev, left_cells, players_path, mktcells
    mouse_x, mouse_y = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed(3)
    color = CYAN
    cell_cur = (cell_x,cell_y) = cell_coord_from_screen(mouse_x, mouse_y)
    if mouse_click == (0,0,0):
        op = NOP
    if mouse_click == (1,0,0):
        op = ADD
        #print(mouse_click)
        if not cell_cur in players_path[player]:
            if len(players_path[player]) == 0 or adjacent(cell_cur, players_path[player]):
                if warps[player] > 0:
                    credits[player] += 1
                    warps[player] -= 1
                    players_path[player].append(cell_cur)
    if mouse_click == (0,0,1):
        op = SUB
        #print(mouse_click)
        if cell_cur in players_path[player]:
            credits[player] -= 1
            warps[player] += 1
            players_path[player].remove(cell_cur)
    if cell_cur in players_path[player]:
        color = colors[player]
    cell_cur_rect = cell_coord_pos_rect(cell_x, cell_y)
    if not cell_cur in mktcells:
        pygame.draw.rect(screen, color, cell_cur_rect, 0)
    if cell_cur != cell_prev:
        cell_prev_rect = cell_coord_pos_rect(cell_prev[0], cell_prev[1])
        #print(cell_cur, cell_prev, cell_cur_rect, cell_prev_rect)
        if not cell_prev in mktcells:
            if not cell_prev in players_path[player]:
                pygame.draw.rect(screen, YELLOW, cell_prev_rect, 0)
        else:
            if not cell_prev in players_path[player]:
                screen.blit(mkt_logo, (cell_prev_rect[0],cell_prev_rect[1]))
        cell_prev = cell_cur

def draw_scores():
    global credits,warps
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
    global screen, players_path, left_cells
    for (cx,cy) in players_path[player]:
        cell_rect = cell_coord_pos_rect(cx, cy)
        color = board_colors[get_board(cx,cy)]
        pygame.draw.rect(screen, color, cell_rect, 0)
        credits[player] -= 1
        warps[player] += 1

    players_path[player] = []
    draw_markets()

def turn(player):
    global cell_prev,left_cells
    cell_prev = (0,0)
    for (cx, cy) in players_path[player]:
        update_board(cx, cy, ADD, player)
        left_cells -= 1
    print(  "turn player=:", player,
            "players_path=", players_path[player],
            "left_cells=", left_cells,
            "credits=", credits[player],
            "warps=",warps[player],
            "next=", 1-player)
    display_board()
    players_path[player] = []
    dices[player] = 1
    draw_scores()
    return 1-player

def game_over():
    print("Game Over")

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
                draw_path(player)
            
            if event.type == pygame.KEYDOWN and event.key == pygame.K_BACKSPACE:
                reset_path(player)

            if event.type==pygame.KEYDOWN and event.key==pygame.K_d :
                throw_dices(player)

            if event.type == pygame.KEYDOWN and (event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER):
                player = turn(player)

        pygame.display.flip()

draw_scores()

loop()

pygame.quit()
