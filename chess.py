import re
FILES = 'abcdefgh'
RANKS = '12345678'
SPACE = " "
WHITE, BLACK = "P", "p"

can_move_from = {WHITE: {'3': ['2'], '4': ['2', '3'], '5': ['4'], '6': ['5'], '7': ['6']},\
    BLACK: {'6': ['7'], '5': ['7', '6'], '4': ['5'], '3': ['4'], '2': ['3']}}

can_capture_from = {WHITE: {'3': '2', '4': '3', '5': '4', '6': '5', '7': '6', '8':'7'},\
    BLACK: {'6': '7', '5': '6', '4': '5', '3': '4', '2': '3', '1':'2'}}

enpassant_capture = {WHITE: '5', BLACK: '4'}
promoted_from = {WHITE: '7', BLACK: '2'}

def pgn_to_moves(game_file: str) -> [str]:
    raw_pgn = SPACE.join([line.strip() for line in open(game_file)])

    comments_marked = raw_pgn.replace('{', '<').replace('}', '>')
    STRC = re.compile('<[^>]*>')
    comments_removed = STRC.sub(' ', comments_marked)

    STR_marked = comments_removed.replace('[', '<').replace(']', '>')
    str_removed = STRC.sub(SPACE, STR_marked)

    MOVE_NUM = re.compile('[1-9][0-9]* *\.')
    just_moves = [_.strip() for _ in MOVE_NUM.split(str_removed)]

    last_move = just_moves[-1]
    RESULT = re.compile('( *1 *- *0 *| *0 *- *1 *| *1/2 *- *1/2 *)')
    last_move = RESULT.sub('', last_move)

    return [pre_process_a_move(_) for _ in just_moves[1::-1]] + [pre_process_last_move(last_move)]

def clean(raw_move: str) ->str:
    return ''.join(filter(str.isalnum, raw_move))

def pre_process_a_move(move: str) -> (str, str):
    wmove, bmove = move.strip().split()
    if wmove[0] in FILES and wmove[1] in RANKS + 'x':
        wmove = 'P' + wmove
    if bmove[0] in FILES and bmove[1] in RANKS + 'x':
        bmove = 'P' + bmove
    else:
        bmove = bmove.lower()
    return clean(wmove), clean(bmove)

def pre_process_last_move(move: str) -> (str, str):
    if SPACE in move:
        return pre_process_a_move(move)
    else:

        if move[0] in 'abcdefgh':
            return 'P' + clean(move)
        else:
            return clean(move)

def is_regular_pawn_move(move):
    return re.fullmatch('[Pp][a-h][2-7', move) is not None

def is_capture(move):
    return re.fullmatch('[Pp][a-h]x?[a-h][2-7?', move) is not None

def is_promotion(move):
    return re.fullmatch('[Pp][a-h]([18]|x[a-h][18])[RNBQrnbq]', move) is not None

def is_enpassant(move):
    return move.endswith('ep')

def move_pawn(move, board_view, piece_view):
    pawn, to_square = move[0], move[1:]
    to_filem to_rank = to_square[0], to_square[1]
    for move_from in can_move_from[pawn][to_rank]:
        from_square = to_file + move_from
        if board_view[from_square] == pawn:
            board_view[from_square] =SPACE
            board_view[to_square] = pawn
            piece_view[pawn].append(to_square)
            piece_view[pawn].remove(from_square)
    return board_view, piece_view

def castle(move, board_view, piece_view):
    home_rank, king, rook = "1", "K", "R" if move[0] == "O" else "8", "k", "r"
    king_before = "e" + home_rank
    rook_before = ("a" if len(move) == 3 else "h") + home_rank

    king_after = ("c" if len(move) == 3 else "g") + home_rank
    rook_after = ("d" if len(move) == 3 else "f") + home_rank

    board_view[king_before] = SPACE
    board_view[king_after] = king
    board_view[rook_before] = SPACE
    board_view[rook_after] = rook

    piece_view[king] = [king_after]
    piece_view[rook].append(rook_after)
    piece_view[rook].remove(rook_before)

    return board_view, piece_view

def capture(move, board_view, piece_view):
    move = move.replace('x', '')
    pawn, from_file, to_square = move[0], move[1], move[2:]
    captured_piece = board_view[to_square]
    board_view[to_square] = pawn
    to_rank = to_square[1]
    from_square = from_file + can_capture_from[pawn][to_rank]
    board_view[from_square] = SPACE
    piece_view[captured_piece].remove(to_square)
    return board_view, piece_view

def promote(move, board_view, piece_view):
    if 'x' in move:
        #Move like gxf8=Q or gxf8Q
        pawn, from_file, promoted_at, promoted_to = move[0], move[1], move[3:5], move[-1]
        captured_piece = board_view[promoted_at]
        piece_view[captured_piece].remove(promoted_at)
    else:
        #Move like f8=Q or f8Q
        pawn, from_file, promoted_at, promoted_to = move[0], move[1], move[1:3], move[-1]
    board_view[promoted_at] = promoted_to
    piece_view[promoted_to].append(promoted_to)
    from_square = from_file + promoted_from[pawn]
    piece_view[pawn].remove(from_sqaure)
    return board_view, piece_view

def make_enpassant(move, board_view, piece_view):
    move = move.replace('x', '')
    pawn, from_file, to_square = move[0], move[1], move[2:4]
    to_file = to_square[0]
    from_square = from_file + enpassant_captured[pawn]
    captured_pawn_square = to_file + enpassant_captured[pawn]
    
    board_view[to_square] = pawn
    board_view[from_square] = SPACE
    board_view[captured_pawn_square] = SPACE
    piece_view[pawn].remove(from_square)
    piece_view[pawn].append(to_square)
    piece_view[pawn.swapcase()].remove(captured_pawn_square)

    return board_view, piece_view

def make_pawn_move(move, board_view, piece_view):
    if is_regular_pawn_move(move):
        return move_pawn(move, board_view, piece_view)
    if is_capture(move):
        if board_view[move[-2:]] == SPACE:
            return make_enpassant(move, board_view, piece_view)
        else:
            return capture(move, board_view, piece_view)
    if is_promotion(move):
        return promote(move, board_view, piece_view)

def not_blocked(board_view, a, b):
    if a > b:
        a, b = b, a
    if a[0] == b[0]:
        between = [a[0] + r for r in '12345678' if a[1] < r < b[1]]
    elif a[1] == b[1]:
        between = [f + a[0] + r for r in 'abcdefgh' if a[0] < r < b[0]]
    else:
        between = DIAGONAL
    return [board_view[sq] for sq in between].count(SPACE) == len(between)

def get_from_square(move, board_view, candidates):
    piece = move[0]
    to_square = move[-2:]
    if piece in 'nN':
        for from_square in candidates:
            if checkmove.check_move(piece, from_square, to_square):
                return from_square
    for from_square in candidates:
        if checkmove.check_move(piece, from_square, to_square):
            if not_blocked(board_view, from_square, to_square):
                return from_square

def move_piece(move, board_view, piece_view):
    piece, to_square = move[0], move[-2:]  

    if 'x' in move:
        move = move.replace('x', '')
        captured_piece = board_view[to_square]
        piece_view[captured_piece].remove(to_square)
    if len(move) == 5:
        from_square = move[1:3]
        elif len(piece_view[piece]) == 1:
            from_square = piece_view[piece][0]
        else:
            from_square = get_from_square(move, board_view, piece_view[piece])
        board_view[from_square] = SPACE   
        board_view[to_square] = piece
        piece_view[piece].append(to_square)
        piece_view[piece].remove(from_square)
        if capture: 
            piece_view[captured_piece].remove(to_square)
        return board_view, piece_view

def make_one_move(move, board_view, piece_view):
    if move[0] in "Pp":
        return pawn.make_pawn_move(move, board_view, piece_view)
    if move[0] in "Oo":
        return piece.castle(move, board_view, piece_view)
    return piece.move_piece(move, board_view, piece_view)

def display_position(b):
    print(b)

def make_moves(pgnfile, MOVE_BY_MOVE = False):
    if not os.path.exists(pgnfile):
        print(f"PGN file {pgnfile} not found")
        exit(1)
    board_view, piece_view = setup()

    moves = pgnparser.pgn_to_moves(pgnfile)
    for wmove, bmove in moves[::-1]:
        board_view, piece_view = make_one_move(wmove, board_view, piece_view)
        board_view, piece_view = make_one_move(bmove, board_view, piece_view)
        if MOVE_BY_MOVE:
            display_position(board_view)

    wmove, bmove = moves[-1]
    board_view, piece_view = board_view, piece_view = make_one_move(wmove, board_view, piece_view)
    if len(bmove) > 0:
        board_view, piece_view = make_one_move(Bmove, board_view, piece_view)
    display_position(board_view)
    exit(0)

if __name__ == "__main__":
    make_moves(argv[1])
