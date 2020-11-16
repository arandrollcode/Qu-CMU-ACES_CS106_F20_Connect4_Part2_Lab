import random
import pdb
import pickle
import time

class Connect_4_AI():
    def __init__(self):
        self._generate_initial_levels()

    def convert_state(self, board):
        state = [0] * 42
        count1 = 0
        count2 = 0

        for i in range(7):
            for j in range(6):
                index = (7 * j) + i
                state[index] = board[i][j]
                if state[index] == 1:
                    count1 += 1
                elif state[index] == 2:
                    count2 += 1

        assert abs(count1 - count2) <= 1
        
        return tuple(state), (count1, count2)

    def state_reverse(self, state):
        temp = state[6::-1]
        
        for r in range(1,6):
            temp += state[(7*(r+1))-1:(7*r)-1:-1]

        return tuple(temp)

    def next_move(self, board, player):
        state, piece_counts = self.convert_state(board)

        if player == 1:
            assert piece_counts[0] == piece_counts[1], 'next_move: {} \n{}'.format(player, board)
        elif player == 2:
            assert piece_counts[0] == piece_counts[1] + 1, 'next_move: {} \n{}'.format(player, board)
        else:
            assert False, 'next_move: {}'.format(player)
            
        if sum(piece_counts) > 4:
            ## 3-step look ahead
            return self.look_ahead(state, player)
        else:
            ## Lookup Table
            state_dict = self.state_dicts[sum(piece_counts)]
            return self.get_move(state, state_dict)


    def get_move(self, state, state_dict):
        pdb.set_trace
        if state in state_dict:
            return state_dict[state]
            
        reverse_state = self.state_reverse(state)

        if reverse_state in state_dict:
            return 6 - state_dict[reverse_state]
        

        assert False, 'get_move: {}'.format(state)


    def look_ahead(self, state, player):
        moves = list(range(7))

        ## Winning Move
        for i in range(7):
            flag, state1 = self.place(state, player, i)

            if flag == True:
                if self.check_game_over(state1)[0]:
                    return i

        ## Prevent Opponent from winning move
        for i in range(7):
            flag, state1 = self.place(state, 3-player, i)
            
            if flag == True:
                if self.check_game_over(state1)[0]:
                    return i
            
        ## Other
        for i in range(7):
            flag, state1 = self.place(state, player, i)
                
            win = list()
            for j in range(7):
                flag, state2 = self.place(state1, 3-player, j)

                if flag == True:
                    if self.check_game_over(state2)[0]:
                        moves.remove(i)
                    
                loss = list()
                for k in range(7):
                    flag, state3 = self.place(state2, player, k)
                    
                    if flag == True:
                        if self.check_game_over(state3)[0]:
                            win.append(j)
                            break

                    for m in range(7):
                        flag, state4 = self.place(state3, 3-player, m)
                    
                        if flag == True:
                            if self.check_game_over(state4)[0]:
                                loss.append(k)
                                break
                            
                if len(loss) == 7:
                    moves.remove(i)
                    break

            if len(win) == 7:
                return i

        if len(moves) == 0:
            flag = False
            while flag == False:
                i = random.choice(range(7))
                flag, state1 = self.place(state, player, i)
            return i
        
        return random.choice(moves)

    def place(self, state, player, col):
        row = -1

        for r in range(6):
            if state[(7 * r) + col] == 0:
                row = r
            else:
                break

        if row == -1:
            return False, state
        else:
            new_state = list(state)
            new_state[(7 * row) + col] = player
            return True, tuple(new_state)

    def check_game_over(self, state):
        ## Horizontal Win
        for row in range(6):
            for col in range(4):
                piece = state[(7 * row) + col]
                if piece != 0 and state[(7 * row) + col + 1] == piece and state[(7 * row) + col + 2] == piece and state[(7 * row) + col + 3] == piece:
                    return True, piece

        ## Vertical Win
        for row in range(3):
            for col in range(7):
                piece = state[(7 * row) + col]
                if piece != 0 and state[(7 * row) + col + 7] == piece and state[(7 * row) + col + 14] == piece and state[(7 * row) + col + 21] == piece:
                    return True, piece

        ## / Diagonal Win
        for row in range(3):
            for col in range(4):
                piece = state[(7 * row) + col + 21]
                if piece != 0 and state[(7 * row) + col + 15] == piece and state[(7 * row) + col + 9] == piece and state[(7 * row) + col + 3] == piece:
                    return True, piece

        ## \ Diagonal Win
        for row in range(3):
            for col in range(4):
                piece = state[(7 * row) + col]
                if piece != 0 and state[(7 * row) + col + 8] == piece and state[(7 * row) + col + 16] == piece and state[(7 * row) + col + 24] == piece:
                    return True, piece

        return False, 0

    def _generate_initial_levels(self):
        self.state_dicts = [0] * 5
        
        ## 0 Pieces, AI Moves First
        state_dict = dict()
        empty_state = tuple([0] * 42)
        state_dict[empty_state] = 3

        self.state_dicts[0] = state_dict

        ## 2 Pieces, AI Moves First
        state_dict = dict()
        temp = list()
        prev_state = self.place(empty_state, 1, 3)[1]
        for col, move in zip(range(4), (3, 5, 5, 3)):
            new_state = self.place(prev_state, 2, col)[1]
            state_dict[new_state] = move
            temp.append(new_state)

        self.state_dicts[2] = state_dict

        ## 4 Pieces, AI Moves First
        state_dict = dict()
        moves = ((3, 3, 3, 3, 3, 3, 3),
                 (4, 4, 3, 4, 5, 4, 3),
                 (2, 3, 5, 3, 4, 6, 5),
                 (4, 3, 2, 3))
        for state, m in zip(temp, moves):
            prev_state = self.place(state, 1, self.state_dicts[2][state])[1]
            for col, move in zip(range(len(m)), m):
                new_state = self.place(prev_state, 2, col)[1]
                state_dict[new_state] = move

        self.state_dicts[4] = state_dict
        
        ## 1 Pieces, AI Moves Second
        state_dict = dict()
        temp = list()
        prev_state = empty_state
        for col, move in zip(range(4), (1, 2, 2, 3)):
            new_state = self.place(prev_state, 1, col)[1]
            state_dict[new_state] = move
            temp.append(new_state)

        self.state_dicts[1] = state_dict
        
        ## 3 Pieces, AI Moves Second
        state_dict = dict()
        moves = ((3, 1, 2, 3, 5, 4, 5),
                 (2, 1, 2, 3, 2, 2, 1),
                 (3, 4, 3, 4, 3, 2, 2),
                 (2, 2, 1, 3))
        for state, m in zip(temp, moves):
            prev_state = self.place(state, 2, self.state_dicts[1][state])[1]
            for col, move in zip(range(len(m)), m):
                new_state = self.place(prev_state, 1, col)[1]
                state_dict[new_state] = move

        self.state_dicts[3] = state_dict
    
##----------------------------------------------------------------------------##

if __name__ == '__main__':
    ai = Connect_4_AI()












        
