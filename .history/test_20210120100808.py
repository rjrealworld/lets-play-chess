import re

def pgn_to_move(game_file: str) ->[str]:
    raw_pgn = ''.join([line.strip() for line in open(game_file)])
    
    #match the pattern starting from < and ending with > with characters other than > in between
    STRC = re.compile('<[^>]*>')

    #remove all the comments i.e. [] and {} part
    comments_marked = raw_pgn.replace('{', '<').replace('}', '>')
    comments_removed = STRC.sub('', comments_marked)
    STR_marked = comments_removed.replace('[', '<').replace(']', '>')
    str_removed = STRC.sub('', STR_marked)

    MOVE_NUM = re.compile('[1-9][0-9]* *\.')
    print(MOVE_NUM.split(str_removed))
    just_moves = [_.strip() for _ in MOVE_NUM.split(str_removed)]
    print(just_moves)
    last_move = just_moves[-1]
    last_move = re.sub('( *1 *- *0 *| *0 *- *1 *| *1/2 *- *1/2 *)', '', last_move)
    moves = just_moves[:-1] + [last_move]
    return [_ for _ in moves if len(_) > 0]

pgn_to_move('pgn.txt')