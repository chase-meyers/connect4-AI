def board_input():
    # Placeholder THIS WILL CHANGE INTO WHAT IS CHANGING PLAY BY PLAY FROM CPP FILE.  
    # Su Su made change rto read the board exported by C++
    board = []
    try:
        with open("board.txt", "r") as f:
           for line in f:
               row = line.strip().split()
               if row:
                   board.append(row)
    except FileNotFoundError:
        board = [[ '-' for _ in range(7)] for _ in range(6)]
    return board


# Puts all full columns to 0.0 since they cannot be selected from
def availability_rule(board_copy, agent_weights):
    for col in range(len(board_copy[0])):
        if '-' not in [row[col] for row in board_copy]:
            agent_weights[str(col)] *= 0.0
    return agent_weights


# Weighs closeness to center since center gives more options
def center_rule(agent_weights):
    bonus = {"0": 0.8, "1": 0.85, "2": 0.9, "3": 0.9, "4": 0.85, "5": 0.8, "6": 0.8}
    for key in agent_weights:
        agent_weights[key] *= bonus[key]
    return agent_weights


# Drops a disc into the lowest open row
def drop_disc(board_copy, col, disc):
    for row in range(len(board_copy) - 1, -1, -1):
        if board_copy[row][col] == '-':
            board_copy[row][col] = disc
            return row


# Checks for four discs in a row through the last move
def wins_at(board_copy, row, col, disc):
    for row_step, col_step in [(0, 1), (1, 0), (1, 1), (1, -1)]:
        count = 1
        for direction in [-1, 1]:
            r = row + row_step * direction
            c = col + col_step * direction
            while (0 <= r < len(board_copy) and 0 <= c < len(board_copy[0])
                   and board_copy[r][c] == disc):
                count += 1
                r += row_step * direction
                c += col_step * direction
        if count >= 4:
            return True
    return False


# Counts columns that can win on the next drop
def winning_moves(board_copy, disc):
    count = 0
    for col in range(len(board_copy[0])):
        next_board = [row[:] for row in board_copy]
        row = drop_disc(next_board, col, disc)
        if row is not None and wins_at(next_board, row, col, disc):
            count += 1
    return count


# Weighs moves that give the agent two ways to win or let the player do the same
def fork_rule(board_copy, weight):
    if winning_moves(board_copy, 'o') >= 2:
        return weight * 1.2

    for col in range(len(board_copy[0])):
        reply_board = [row[:] for row in board_copy]
        row = drop_disc(reply_board, col, 'x')
        if (row is not None and winning_moves(reply_board, 'x') >= 2
                and winning_moves(reply_board, 'o') == 0):
            return weight * 0.8
    return weight


# Weighs winning moves first and lowers the weight for each player win left
def win_block_rule(board_copy, agent_weights):
    for key in agent_weights:
        if agent_weights[key] == 0.0:
            continue
        col = int(key)
        next_board = [row[:] for row in board_copy]
        row = drop_disc(next_board, col, 'o')
        if wins_at(next_board, row, col, 'o'):
            agent_weights[key] *= 2.0
            continue

        player_wins = winning_moves(next_board, 'x')
        if player_wins:
            agent_weights[key] *= 0.5 ** player_wins
        else:
            agent_weights[key] = fork_rule(next_board, agent_weights[key])
    return agent_weights


# Uses function rules
def agent_weight_rules(board_copy, agent_weights):
    agent_weights = center_rule(agent_weights)
    agent_weights = availability_rule(board_copy, agent_weights)
    agent_weights = win_block_rule(board_copy, agent_weights)
    return agent_weights


# Interprets board: handles rules, instantiates weight dictionary and creates board copy
def agent_interpret():
    agent_weights = {"0": 1.0, "1": 1.0, "2": 1.0, "3": 1.0, "4": 1.0,
                     "5": 1.0, "6": 1.0}
    board_copy = board_input()
    agent_weights = agent_weight_rules(board_copy, agent_weights)
    return agent_weights


def main():
    weights =agent_interpret(); 
    valid_moves = {k: v for k, v in weights.items() if v > 0.0}
    if valid_moves:
        best_col = max(valid_moves, key=valid_moves.get)
    else:
        best_col = "0"
        
    # Write the chosen move to a file for C++ to read
    with open("move.txt", "w") as f:
        f.write(best_col)   

if __name__ == "__main__":
    print(main())
