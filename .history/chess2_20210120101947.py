import re
  
def setup():
    squares = [y + x for x in '12345678' for y in 'abcdefgh']
    start = 'RNBQKBNR' + 'P' * 8 + ' ' * 32 + 'p' * 8 + 'rnbqkbnr'

    # board_view = {position : piece}
    board_view = dict(zip(squares, start))

    # piece_view = {piece : [positions]}
    piece_view = {_ : [] for _ in 'BKNPQRbknpqr'}
    for sq in board_view:
        piece = board_view[sq]
        if piece != ' ':
            piece_view[piece].append(sq)
    return piece_view


def pgn_to_move(game_file: str) ->[str]:
    raw_pgn = ' '.join([line.strip() for line in open(game_file)])
    
    #match the pattern starting from < and ending with > with characters other than > in between
    STRC = re.compile('<[^>]*>')

    #remove all the comments i.e. [] and {} part
    comments_marked = raw_pgn.replace('{', '<').replace('}', '>')
    comments_removed = STRC.sub(' ', comments_marked)
    STR_marked = comments_removed.replace('[', '<').replace(']', '>')
    str_removed = STRC.sub(' ', STR_marked)
    print(str_removed)
    
    #remove the extra parts and get the list of only the moves
    MOVE_NUM = re.compile('[1-9][0-9]* *\.') # pattern with number and dot
    just_moves = [_.strip() for _ in MOVE_NUM.split(str_removed)] #remove numbers
    last_move = just_moves[-1]
    last_move = re.sub('( *1 *- *0 *| *0 *- *1 *| *1/2 *- *1/2 *)', '', last_move) #remove score from the last index
    moves = just_moves[:-1] + [last_move] #list of moves and blanks
    return [_ for _ in moves if len(_) > 0] #only moves


def pre_process_a_move(move: str) -> (str, str):
    wmove, bmove = move.split()
    #pawn moves
    if wmove[0] in 'abcdefgh':
        wmove = 'P' + wmove
    if bmove[0] in 'abcdefgh':
        bmove = 'p' + bmove
    #considering lower for black and upper for white
    else:
        bmove = bmove.lower()
    return wmove, bmove
    
    
def pre_process_moves(moves: [str]) -> [(str, str)]:                                                                                          
    return [pre_process_a_move(move) for move in moves[:-1]] + [(moves[-1], )]   
    

letter_index = {'a': 0, 'b': 1, 'c': 2, 'd': 3, 'e': 4, 'f': 5, 'g': 6, 'h': 7}
def valid_king_move(initial, final):
    return abs(final[0] - initial[0]), abs(final[1] - initial[1]) in [(0, 1), (1, 0), (1, 1)]
    
def valid_bishop_move(initial, final):
    return abs(final[0] - initial[0]) == abs(final[1] - initial[1]) 
    
def valid_rook_move(initial, final, piece_v):
    for key in piece_v:
        for position in piece_v[key]:
            position = (letter_index[position[0].lower()], int(position[1]) - 1) 
            if position[0] == initial[0] == final[0]:
                return not (initial[1] < position[1] < final[1] or final[1] < position[1] < initial[1])
            elif position[1] == initial[1] == final[1]:
                return not (initial[0] < position[0] < final[0] or final[0] < position[0] < initial[0]) 
    return final[0] == initial[0] or final[1] == initial[1]
    
def valid_knight_move(initial, final):
    return (abs(final[0] - initial[0]) == 1 and abs(final[1] - initial[1]) == 2) or (abs(final[0] - initial[0]) == 2 and abs(final[1] - initial[1]) == 1)
    
def valid_white_pawn_move(initial, final):
    if initial[1] == 1 or initial[1] == 6:
        return final[0] == initial[0] and final[1] - initial[1] == 2 or final[0] == initial[0] and final[1] - initial[1] == 1
    return final[0] == initial[0] and final[1] - initial[1] == 1

def valid_black_pawn_move(initial, final):
    if initial[1] == 1 or initial[1] == 6:
        return final[0] == initial[0] and initial[1] - final[1] == 2 or final[0] == initial[0] and initial[1] - final[1] == 1
    return final[0] == initial[0] and (initial[1] - final[1]) == 1

def is_move_possible(piece, initial_index, final_index, piece_v):
        if piece.upper() == 'K':
            return valid_king_move(initial_index, final_index)
        elif piece.upper() == 'B':
            return valid_bishop_move(initial_index, final_index)
        elif piece.upper() == 'R':
            return valid_rook_move(initial_index, final_index, piece_v)
        elif piece.upper() == 'N':
            return valid_knight_move(initial_index, final_index)
        elif piece == 'P':
            return valid_white_pawn_move(initial_index, final_index)
        elif piece == 'p':
            return valid_black_pawn_move(initial_index, final_index)
        else:
            return valid_bishop_move(initial_index, final_index) or valid_rook_move(initial_index, final_index, piece_v)


def change_final_position(final_position, piece_v, piece):
    final_index = (letter_index[final_position[0].lower()], int(final_position[1]) - 1)
    for index, position in enumerate(piece_v[piece]):
        initial_index = (letter_index[position[0].lower()], int(position[1]) - 1)                           
        if is_move_possible(piece, initial_index, final_index, piece_v):                                                         
            piece_v[piece][index] = final_position 
            return piece_v


def remove_captured_piece(piece_v, final_position):
    for key in piece_v.keys():                                                                                
        if final_position in piece_v[key]:  
            piece_v[key].remove(final_position)                                                   
            return piece_v


def castling_of_two(rook_position, king, color, turn):
    if color == 'black':
        rank = '8'
    else:
        rank = '1'
    if len(turn) == 3:
        rook_position[rook_position.index('h' + rank)] = 'f' + rank
        king[0] = 'g' + rank
    elif len(turn) == 5:
        rook_position[rook_position.index('h' + rank)] = 'd' + rank
        king[0] = 'c' + rank
    return piece_v


def get_final_piece_view(moves, piece_v):
    for move in moves:
        for turn in move:
            if 'o-' in turn:
                rook_position = piece_v['r']
                king = piece_v['k']
                color = 'black'
                piece_v = castling_of_two(rook_position, king, color, turn)
        
            elif 'O-' in turn:
                rook_position = piece_v['R']
                king = piece_v['K']
                color = 'white'
                piece_v = castling_of_two(rook_position, king, color, turn)

            piece = turn[0]
            if len(turn) == 3 and '-' not in turn:
                final_position = turn[1:]
                piece_v = change_final_position(final_position, piece_v, piece)

            elif len(turn) == 5 and 'x' in turn and '+' not in turn:                                                                  
                final_position = turn[3:]                                                                                
                initial_file = turn[1]                                                                        
                piece_v = remove_captured_piece(piece_v, final_position) 
                for index, position in enumerate(piece_v[piece]):                                                       
                    if initial_file in position:                                                                        
                        piece_v[piece][index] = final_position        
                        break
            
            elif len(turn) == 4 and '+' in turn:
                final_position = turn[1:-1]
                piece_v = change_final_position(final_position, piece_v, piece)

            elif len(turn) == 4 and 'x' not in turn:
                final_position = turn[2:]
                initial_file = turn[1]
                for index, position in enumerate(piece_v[piece]):
                    if initial_file in position:
                        piece_v[piece][index] = final_position
                        break
                    
            elif len(turn) == 5 and 'x' in turn and '+' in turn:   
                final_position = turn[2:-1]
                piece_v = remove_captured_piece(piece_v, final_position)
                piece_v = change_final_position(final_position, piece_v, piece)

            elif len(turn) == 4 and 'x' in turn:
                final_position = turn[2:]
                piece_v = remove_captured_piece(piece_v, final_position)  
                piece_v = change_final_position(final_position, piece_v, piece) 
    return piece_v


def final_board_rank_file(piece_v):
    rank_file = [j+i for i in '87654321' for j in 'abcdefgh']
    for key in piece_v:
        for index, sq in enumerate(rank_file):
            if sq in piece_v[key]:
                rank_file[index] = key
    rank_file = [rank_file[i:i + 8] for i in range(0, len(rank_file), 8)]
    return rank_file


def fen_notation(rank_file):
    fen = ''
    for rank in rank_file:    
        count = 0
        for file in rank:
            if file not in 'RNBKQPrnbkqp':
                count += 1
            else:
                if count>0:
                    fen += str(count)
                    count = 0
                fen += file
        if count>0:
            fen += str(count)
            count = 0   
        fen += ' / '
    return fen[:-3]

moves = pre_process_moves(pgn_to_move('pgn2.txt'))
print(moves)
piece_v = setup() 
print(piece_v)
print(get_final_piece_view(moves, piece_v))
print(fen_notation(final_board_rank_file(piece_v)))