import random


class TicTacToe:
    def __init__(self):
        self.initial_state = '_' * 9
        self.sides = ['X', 'O']
        self.turn = 0
        self.params_accepted = False
        self.game_finished = False
        self.state = []
        self.menu()

    def menu(self):
        while not self.params_accepted:
            params = input('Input command:').split()
            if params[0] == 'exit':
                self.params_accepted = True
                exit()
            elif params[0] == 'start':
                if len(params) != 3 or any(param not in ['user', 'easy', 'medium', 'hard'] for param in params[1:]):
                    print('Bad parameters!')
                else:
                    self.params_accepted = True
                    self.reset()
                    self.play(*params[1:])
            else:
                print('Bad parameters!')

    def play(self, *players):
        player_one, player_two = self.assign_player(1, *players), self.assign_player(2, *players)

        while not self.game_finished:
            if self.turn % 2 == 0:
                self.change_state(*player_one.move(self), player_one.side)
                player_one.coords_accepted = False
            else:
                self.change_state(*player_two.move(self), player_two.side)
                player_two.coords_accepted = False
            self.print_state(self.state)
            self.analyse_state(self.state)
            self.turn += 1
        else:
            self.params_accepted = False

    def assign_player(self, n, *players):
        if players[n - 1] == 'user':
            return User(self, n)
        elif players[n - 1] == 'easy':
            return Easy(self, n)
        elif players[n - 1] == 'medium':
            return Medium(self, n)
        elif players[n - 1] == 'hard':
            return Hard(self, n)

    def reset(self):
        self.turn = 0
        self.game_finished = False
        self.state = self.state_matrix(self.initial_state)
        self.print_state(self.state)

    def is_valid_move(self, x, y):
        return self.state[x][y] == '_'

    def change_state(self, x, y, side):
        self.state[x][y] = side

    def analyse_state(self, state):
        # Check if either side has won
        for side in self.sides:
            if self.is_victory(state, side):
                self.game_finished = True
                return print(f'{side} wins')

        # Otherwise, check if table is complete
        if not self.empty_spaces(state):
            self.game_finished = True
            return print('Draw')

    @staticmethod
    def empty_spaces(state):
        return [(i, j) for i in range(3) for j in range(3) if state[i][j] == '_']

    @staticmethod
    def is_victory(state, side):
        for i in range(3):
            # Check rows and columns
            if (all(state[i][j] == side for j in range(3))
                    or all(state[j][i] == side for j in range(3))):
                return True
            # Check diagonals
            if (all(state[i][i] == side for i in range(3))
                    or all(state[i][2 - i] == side for i in range(3))):
                return True
        else:
            return False

    @staticmethod
    def print_state(state):
        print('-' * 9)
        for i in range(3):
            print('| ' + ' '.join(cell.replace('_', ' ') for cell in state[i]) + ' |')
        print('-' * 9)

    @staticmethod
    def state_matrix(state):
        return [[cell for cell in state[i:i + 3]] for i in range(0, len(state), 3)]


class Player:
    def __init__(self, game, player_num):
        if player_num == 1:
            [self.side, self.opt_side] = game.sides
        elif player_num == 2:
            [self.opt_side, self.side] = game.sides
        self.coords_accepted = False


class User(Player):
    def move(self, game):
        while not self.coords_accepted:
            coords = input('Enter the coordinates:')
            if not coords.replace(' ', '').isnumeric():
                print('You should enter numbers!')
            else:
                coords = [int(coord) for coord in coords.split()]
                if any(coord < 1 or coord > 3 for coord in coords):
                    print('Coordinates should be from 1 to 3!')
                else:
                    x, y = [coord - 1 for coord in coords]
                    if not game.is_valid_move(x, y):
                        print('This cell is occupied! Choose another one!')
                    else:
                        self.coords_accepted = True
                        return x, y


class Computer(Player):
    def random_move(self, game):
        while not self.coords_accepted:
            x, y = random.randint(0, 2), random.randint(0, 2)
            if game.is_valid_move(x, y):
                self.coords_accepted = True
                return x, y

    def check_possible_moves(self, game, side):
        for i in range(3):
            for j in range(3):
                if game.state[i][j] == '_':
                    possible_move = [row.copy() for row in game.state]
                    possible_move[i][j] = side
                    if game.is_victory(possible_move, side):
                        return i, j


class Easy(Computer):
    def move(self, game):
        print('Making move level "easy"')
        return self.random_move(game)


class Medium(Computer):
    def move(self, game):
        print('Making move level "medium"')

        # If has 2 in a row and can win with one further move, makes it
        if game.turn >= 4:
            winning_move = self.check_possible_moves(game, self.side)
            if winning_move:
                return winning_move

        # If opponent can win with one move, plays the move necessary to block this
        if game.turn >= 3:
            blocking_move = self.check_possible_moves(game, self.opt_side)
            if blocking_move:
                return blocking_move

        # Otherwise, make a random move
        return self.random_move(game)


class Hard(Computer):
    def move(self, game):
        print('Making move level "hard"')
        return self.minimax(game.state, self.side, game, -10000, 10000).coords

    def minimax(self, new_board, player, game, alpha, beta):  # the main minimax function

        available_spots = game.empty_spaces(new_board)

        # Checks for the terminal states (win, lose, draw) and returns a value accordingly
        if game.is_victory(new_board, self.opt_side):
            return Move(score=-10)
        elif game.is_victory(new_board, self.side):
            return Move(score=10)
        elif not available_spots:
            return Move(score=0)

        if player == self.side:
            best_score = -10000
            best_move = None

            for (i, j) in available_spots:
                move = Move(coords=(i, j))

                # Set the empty spot to the current player
                new_board[i][j] = player

                # Collect the score resulting from calling minimax on the opponent of the current player
                result = self.minimax(new_board, self.opt_side, game, alpha, beta)
                move.score = result.score

                # Reset the spot to empty
                new_board[i][j] = '_'

                if move.score > best_score:
                    best_score = move.score
                    best_move = move

                alpha = max(alpha, move.score)

                if beta <= alpha:
                    break

            return best_move

        else:
            best_score = 10000
            best_move = None

            for (i, j) in available_spots:
                move = Move(coords=(i, j))

                new_board[i][j] = player

                result = self.minimax(new_board, self.side, game, alpha, beta)
                move.score = result.score

                new_board[i][j] = '_'

                if move.score < best_score:
                    best_score = move.score
                    best_move = move

                beta = min(beta, move.score)

                if beta <= alpha:
                    break

            return best_move


class Move:
    def __init__(self, coords=None, score=None):
        self.coords = coords
        self.score = score


game = TicTacToe()
