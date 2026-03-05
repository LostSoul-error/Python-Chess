import pygame
import sys
import board
from utils import index_to_alg

pygame.init()

# -------------------------------------------------
# CONSTANTS
# -------------------------------------------------
SQUARE_SIZE = 80
BOARD_SIZE = 8
WIDTH = SQUARE_SIZE * BOARD_SIZE
HEIGHT = SQUARE_SIZE * BOARD_SIZE

LIGHT = (240,217,181)
DARK = (181,136,99)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess")


# -------------------------------------------------
# IMAGE LOADING
# -------------------------------------------------
def load_images():

    pieces = {}

    names = [
        "wp","wr","wn","wb","wq","wk",
        "bp","br","bn","bb","bq","bk"
    ]

    for name in names:

        image = pygame.image.load(f"pieces/{name}.png")
        pieces[name] = pygame.transform.scale(image,(SQUARE_SIZE,SQUARE_SIZE))

    return pieces


# -------------------------------------------------
# DRAW BOARD
# -------------------------------------------------
def draw_board():

    for row in range(8):
        for col in range(8):

            color = LIGHT if (row+col)%2==0 else DARK

            pygame.draw.rect(
                screen,
                color,
                (col*SQUARE_SIZE,row*SQUARE_SIZE,SQUARE_SIZE,SQUARE_SIZE)
            )


# -------------------------------------------------
# DRAW PIECES
# -------------------------------------------------
def draw_pieces(board_state, images):

    for row in range(8):
        for col in range(8):

            piece = board_state[row][col]

            if piece == ".":
                continue

            key = "w"+piece.lower() if piece.isupper() else "b"+piece.lower()

            screen.blit(images[key],(col*SQUARE_SIZE,row*SQUARE_SIZE))


# -------------------------------------------------
# BOARD COORDINATES
# -------------------------------------------------
def draw_coordinates():

    font = pygame.font.SysFont("Times New Roman",18)

    for i in range(8):

        letter = font.render(chr(97+i),True,(0,0,0))
        number = font.render(str(8-i),True,(0,0,0))

        screen.blit(letter,(i*80+70,620))
        screen.blit(number,(5,i*80+5))


# -------------------------------------------------
# HIGHLIGHTS
# -------------------------------------------------
def highlight_square(selected):

    if selected is None:
        return

    row,col = selected

    pygame.draw.rect(
        screen,
        (246,246,105),
        (col*80,row*80,80,80)
    )


def highlight_hover(row,col):

    pygame.draw.rect(
        screen,
        (180,180,180),
        (col*80,row*80,80,80),
        2
    )


def highlight_moves(board_state,moves):

    for row,col in moves:

        x = col*80
        y = row*80

        if board_state[row][col]!=".":

            pygame.draw.circle(
                screen,(220,50,50),(x+40,y+40),30,4
            )

        else:

            pygame.draw.circle(
                screen,(120,200,120),(x+40,y+40),10
            )


# -------------------------------------------------
# CHECK HIGHLIGHT
# -------------------------------------------------
def highlight_check(board_state,turn):

    if not board.is_king_in_check(board_state,turn):
        return

    for r in range(8):
        for c in range(8):

            piece = board_state[r][c]

            if turn=="white" and piece=="K":
                pygame.draw.rect(screen,(255,80,80),(c*80,r*80,80,80))

            if turn=="black" and piece=="k":
                pygame.draw.rect(screen,(255,80,80),(c*80,r*80,80,80))


# -------------------------------------------------
# GAME OVER SCREEN
# -------------------------------------------------
def draw_game_over(text,sub):

    overlay = pygame.Surface((WIDTH,HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((0,0,0))

    screen.blit(overlay,(0,0))

    title_font = pygame.font.SysFont("Times New Roman",72)
    sub_font = pygame.font.SysFont("Times New Roman",36)

    title = title_font.render(text,True,(212,175,55))
    subtitle = sub_font.render(sub,True,(255,255,255))

    screen.blit(title,(WIDTH//2-title.get_width()//2,250))
    screen.blit(subtitle,(WIDTH//2-subtitle.get_width()//2,350))


# -------------------------------------------------
# LEGAL MOVE GENERATOR
# -------------------------------------------------
def get_legal_moves(board_state,row,col,turn):

    moves = []

    from_sq = index_to_alg(row,col)

    for r in range(8):
        for c in range(8):

            to_sq = index_to_alg(r,c)

            if board.is_valid_move(board_state,from_sq,to_sq,turn):
                moves.append((r,c))

    return moves


# -------------------------------------------------
# GAME STATE
# -------------------------------------------------
bd = board.create_board()
turn = "white"

pieces = load_images()

selected_square = None
legal_moves = []

game_over = False
game_text = ""
game_sub = ""


# -------------------------------------------------
# MAIN LOOP
# -------------------------------------------------
running = True

while running:

    mouse_x,mouse_y = pygame.mouse.get_pos()

    hover_col = mouse_x//80
    hover_row = mouse_y//80

    for event in pygame.event.get():

        if event.type==pygame.QUIT:
            running=False

        if event.type==pygame.MOUSEBUTTONDOWN and not game_over:

            col = mouse_x//80
            row = mouse_y//80

            if selected_square is None:

                if bd[row][col]!=".":

                    piece = bd[row][col]

                    if (turn=="white" and piece.isupper()) or \
                       (turn=="black" and piece.islower()):

                        selected_square=(row,col)
                        legal_moves=get_legal_moves(bd,row,col,turn)

            else:

                start=selected_square
                end=(row,col)

                from_sq=index_to_alg(start[0],start[1])
                to_sq=index_to_alg(end[0],end[1])

                moved = board.move_piece(bd,from_sq,to_sq,turn)

                if moved:

                    turn = "black" if turn=="white" else "white"

                    if board.is_checkmate(bd,turn):

                        game_over=True
                        winner="White" if turn=="black" else "Black"
                        game_text="CHECKMATE"
                        game_sub=f"{winner} Wins"

                    elif board.is_stalemate(bd,turn):

                        game_over=True
                        game_text="STALEMATE"
                        game_sub="Draw"

                legal_moves=[]
                selected_square=None


    draw_board()
    draw_coordinates()

    highlight_moves(bd,legal_moves)
    highlight_square(selected_square)
    highlight_check(bd,turn)

    draw_pieces(bd,pieces)

    if 0<=hover_row<8 and 0<=hover_col<8:
        highlight_hover(hover_row,hover_col)

    if game_over:
        draw_game_over(game_text,game_sub)

    pygame.display.flip()


pygame.quit()
sys.exit()