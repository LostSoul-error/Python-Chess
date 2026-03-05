from utils import alg_to_index
import copy


# =========================================================
# CASTLING RIGHTS
# tracks whether king or rooks have moved
# =========================================================
castling_rights = {
    "white_king_moved": False,
    "white_rook_a_moved": False,
    "white_rook_h_moved": False,
    "black_king_moved": False,
    "black_rook_a_moved": False,
    "black_rook_h_moved": False,
}


# =========================================================
# INITIAL BOARD
# =========================================================
def create_board():
    return [
        ["r","n","b","q","k","b","n","r"],
        ["p","p","p","p","p","p","p","p"],
        [".",".",".",".",".",".",".","."],
        [".",".",".",".",".",".",".","."],
        [".",".",".",".",".",".",".","."],
        [".",".",".",".",".",".",".","."],
        ["P","P","P","P","P","P","P","P"],
        ["R","N","B","Q","K","B","N","R"],
    ]


# =========================================================
# MOVE VALIDATION DISPATCH
# routes piece to correct validator
# =========================================================
def is_valid_move(board, fromsq, tosq, turn):

    fsr, fsc = alg_to_index(fromsq)
    tsr, tsc = alg_to_index(tosq)

    if not (0 <= fsr < 8 and 0 <= fsc < 8 and 0 <= tsr < 8 and 0 <= tsc < 8):
        return False

    piece = board[fsr][fsc]

    if piece == ".":
        return False

    if turn == "white" and not piece.isupper():
        return False

    if turn == "black" and not piece.islower():
        return False

    validators = {
        "P": is_valid_pawn_move,
        "p": is_valid_pawn_move,
        "R": is_valid_rook_move,
        "r": is_valid_rook_move,
        "B": is_valid_bishop_move,
        "b": is_valid_bishop_move,
        "N": is_valid_knight_move,
        "n": is_valid_knight_move,
        "Q": is_valid_queen_move,
        "q": is_valid_queen_move,
        "K": is_valid_king_move,
        "k": is_valid_king_move,
    }

    if not validators[piece](board, fromsq, tosq, turn):
        return False

    if leaves_king_in_check(board, fromsq, tosq, turn):
        return False

    return True


# =========================================================
# MOVE EXECUTION
# =========================================================
def move_piece(board, fromsq, tosq, turn):

    if not is_valid_move(board, fromsq, tosq, turn):
        return False

    fsr, fsc = alg_to_index(fromsq)
    tsr, tsc = alg_to_index(tosq)

    piece = board[fsr][fsc]
    captured = board[tsr][tsc]

    # if rook gets captured, remove castling rights
    if captured == "R" and tosq == "a1":
        castling_rights["white_rook_a_moved"] = True
    if captured == "R" and tosq == "h1":
        castling_rights["white_rook_h_moved"] = True
    if captured == "r" and tosq == "a8":
        castling_rights["black_rook_a_moved"] = True
    if captured == "r" and tosq == "h8":
        castling_rights["black_rook_h_moved"] = True

    # -----------------------------
    # CASTLING EXECUTION
    # -----------------------------
    if piece in ("K", "k") and abs(tsc - fsc) == 2:

        if piece == "K":

            if tsc == 6:
                board[7][5], board[7][7] = "R", "."
            else:
                board[7][3], board[7][0] = "R", "."

            castling_rights["white_king_moved"] = True

        else:

            if tsc == 6:
                board[0][5], board[0][7] = "r", "."
            else:
                board[0][3], board[0][0] = "r", "."

            castling_rights["black_king_moved"] = True

    board[tsr][tsc] = piece
    board[fsr][fsc] = "."

    # update castling rights
    if piece == "K":
        castling_rights["white_king_moved"] = True

    if piece == "k":
        castling_rights["black_king_moved"] = True

    if piece == "R" and fromsq == "a1":
        castling_rights["white_rook_a_moved"] = True

    if piece == "R" and fromsq == "h1":
        castling_rights["white_rook_h_moved"] = True

    if piece == "r" and fromsq == "a8":
        castling_rights["black_rook_a_moved"] = True

    if piece == "r" and fromsq == "h8":
        castling_rights["black_rook_h_moved"] = True


    # -----------------------------
    # PAWN PROMOTION
    # default promotion = queen
    # -----------------------------
    if piece == "P" and tsr == 0:
        board[tsr][tsc] = "Q"

    if piece == "p" and tsr == 7:
        board[tsr][tsc] = "q"

    return True


# =========================================================
# KING SAFETY
# =========================================================
def leaves_king_in_check(board, f, t, turn):

    temp = copy.deepcopy(board)

    fsr, fsc = alg_to_index(f)
    tsr, tsc = alg_to_index(t)

    temp[tsr][tsc] = temp[fsr][fsc]
    temp[fsr][fsc] = "."

    return is_king_in_check(temp, turn)


def is_king_in_check(board, turn):

    enemy = "black" if turn == "white" else "white"

    for r in range(8):
        for c in range(8):

            if (turn == "white" and board[r][c] == "K") or \
               (turn == "black" and board[r][c] == "k"):

                square = chr(c + 97) + str(8 - r)
                return is_square_attacked(board, square, enemy)

    return False


# =========================================================
# CHECK / STALEMATE DETECTION
# =========================================================
def has_any_legal_move(board, turn):

    for r in range(8):
        for c in range(8):

            piece = board[r][c]

            if piece == ".":
                continue

            if turn == "white" and not piece.isupper():
                continue

            if turn == "black" and not piece.islower():
                continue

            fromsq = chr(c + 97) + str(8 - r)

            for tr in range(8):
                for tc in range(8):

                    tosq = chr(tc + 97) + str(8 - tr)

                    if is_valid_move(board, fromsq, tosq, turn):
                        return True

    return False


def is_checkmate(board, turn):
    return is_king_in_check(board, turn) and not has_any_legal_move(board, turn)


def is_stalemate(board, turn):
    return not is_king_in_check(board, turn) and not has_any_legal_move(board, turn)

# ================= ATTACK CHECK =================
def is_square_attacked(board, square, by_turn):
    tsr,tsc = alg_to_index(square)
    for r in range(8):
        for c in range(8):
            p=board[r][c]
            if p==".":
                continue
            if by_turn=="white" and not p.isupper(): continue
            if by_turn=="black" and not p.islower(): continue
            fromsq=chr(c+97)+str(8-r)
            if p=="P" and tsr==r-1 and abs(tsc-c)==1: return True
            if p=="p" and tsr==r+1 and abs(tsc-c)==1: return True
            if p.lower()=="r" and is_valid_rook_move(board,fromsq,square,by_turn): return True
            if p.lower()=="b" and is_valid_bishop_move(board,fromsq,square,by_turn): return True
            if p.lower()=="n" and is_valid_knight_move(board,fromsq,square,by_turn): return True
            if p.lower()=="q" and is_valid_queen_move(board,fromsq,square,by_turn): return True
            if p.lower()=="k" and abs(tsr-r)<=1 and abs(tsc-c)<=1: return True
    return False

# ================= CASTLING =================
def is_valid_castling(board, f, t, turn):
    if turn=="white":
        if castling_rights["white_king_moved"] or f!="e1": return False
        if t=="g1":
            if castling_rights["white_rook_h_moved"]: return False
            if board[7][5]!="." or board[7][6]!=".": return False
            if is_square_attacked(board,"e1","black") or \
               is_square_attacked(board,"f1","black") or \
               is_square_attacked(board,"g1","black"): return False
            return True
        if t=="c1":
            if castling_rights["white_rook_a_moved"]: return False
            if board[7][1]!="." or board[7][2]!="." or board[7][3]!=".": return False
            if is_square_attacked(board,"e1","black") or \
               is_square_attacked(board,"d1","black") or \
               is_square_attacked(board,"c1","black"): return False
            return True

    if turn=="black":
        if castling_rights["black_king_moved"] or f!="e8": return False
        if t=="g8":
            if castling_rights["black_rook_h_moved"]: return False
            if board[0][5]!="." or board[0][6]!=".": return False
            if is_square_attacked(board,"e8","white") or \
               is_square_attacked(board,"f8","white") or \
               is_square_attacked(board,"g8","white"): return False
            return True
        if t=="c8":
            if castling_rights["black_rook_a_moved"]: return False
            if board[0][1]!="." or board[0][2]!="." or board[0][3]!=".": return False
            if is_square_attacked(board,"e8","white") or \
               is_square_attacked(board,"d8","white") or \
               is_square_attacked(board,"c8","white"): return False
            return True
    return False

# ================= PIECE RULES =================
def is_valid_pawn_move(board,f,t,turn):
    fsr,fsc=alg_to_index(f)
    tsr,tsc=alg_to_index(t)
    d=-1 if turn=="white" else 1
    start=6 if turn=="white" else 1
    enemy=str.islower if turn=="white" else str.isupper

    if abs(tsc-fsc)==1 and tsr==fsr+d:
        return board[tsr][tsc]!="." and enemy(board[tsr][tsc])
    if fsc!=tsc or board[tsr][tsc]!=".": return False
    if tsr==fsr+d: return True
    if fsr==start and tsr==fsr+2*d and board[fsr+d][fsc]==".": return True
    return False

def is_valid_rook_move(board,f,t,turn):
    fsr,fsc=alg_to_index(f)
    tsr,tsc=alg_to_index(t)
    if fsr!=tsr and fsc!=tsc: return False
    dr=(tsr>fsr)-(tsr<fsr)
    dc=(tsc>fsc)-(tsc<fsc)
    r,c=fsr+dr,fsc+dc
    while (r,c)!=(tsr,tsc):
        if board[r][c]!=".": return False
        r+=dr; c+=dc
    return board[tsr][tsc]=="." or \
           (board[tsr][tsc].islower() if turn=="white" else board[tsr][tsc].isupper())

def is_valid_bishop_move(board,f,t,turn):
    fsr,fsc=alg_to_index(f)
    tsr,tsc=alg_to_index(t)
    if abs(tsr-fsr)!=abs(tsc-fsc): return False
    dr=1 if tsr>fsr else -1
    dc=1 if tsc>fsc else -1
    r,c=fsr+dr,fsc+dc
    while (r,c)!=(tsr,tsc):
        if board[r][c]!=".": return False
        r+=dr; c+=dc
    return board[tsr][tsc]=="." or \
           (board[tsr][tsc].islower() if turn=="white" else board[tsr][tsc].isupper())

def is_valid_knight_move(board,f,t,turn):
    fsr,fsc=alg_to_index(f)
    tsr,tsc=alg_to_index(t)
    if (abs(tsr-fsr),abs(tsc-fsc)) not in [(2,1),(1,2)]: return False
    return board[tsr][tsc]=="." or \
           (board[tsr][tsc].islower() if turn=="white" else board[tsr][tsc].isupper())

def is_valid_queen_move(board,f,t,turn):
    return is_valid_rook_move(board,f,t,turn) or is_valid_bishop_move(board,f,t,turn)

def is_valid_king_move(board,f,t,turn):
    fsr,fsc=alg_to_index(f)
    tsr,tsc=alg_to_index(t)
    if fsr==tsr and abs(tsc-fsc)==2:
        return is_valid_castling(board,f,t,turn)
    if abs(tsr-fsr)<=1 and abs(tsc-fsc)<=1:
        return board[tsr][tsc]=="." or \
               (board[tsr][tsc].islower() if turn=="white" else board[tsr][tsc].isupper())
    return False


def promote_pawn(piece, turn):
    # default promotion (Queen)
    return "Q" if turn == "white" else "q"


def print_board(board):
    print("\n  a b c d e f g h")
    for r in range(8):
        print(8-r, end=" ")
        for c in range(8):
            print(board[r][c], end=" ")
        print(8-r)
    print("  a b c d e f g h\n")