def alg_to_index(sq : str):
    col = int(ord(sq[0])-97)
    row = int(8 -int(sq[1]))
    return row,col


def index_to_alg(row, col):
    file = chr(col + 97)     # 0 → 'a'
    rank = str(8 - row)      # 0 → '8'
    return file + rank