def setup():
    squares = [y + x for x in '12345678' for y in 'abcdefgh']
    start = 'RNBQKBNR' + 'P' * 8 + ' ' * 32 + 'p' * 8 + 'rnbqkbnr'
    board_view = dict(zip(squares, start))
    print(board_view)
    piece_view = {_ : [] for _ in 'BKNPQRbknpqr'}
    for sq in board_view:
        piece = board_view[sq]
        if piece != ' ':
            piece_view[piece].append(sq)
    print(piece_view)
    return piece_view

setup()