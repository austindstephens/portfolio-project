# Author       : Austin Stephens
# Date         : 11/28/20
# Description  : This is a primitive text-based game editor for
#                the board game Focus/Domination.

class Space:
    """Class that represents a space on the board; can be used
    in conjunction with the FocusGame class"""

    def __init__(self, color):
        """Constructor for Space class; takes an initial color
        for the space/stack"""

        self._stack = [color]

    def get_stack(self):
        """Takes nothing and returns list of stack"""

        return self._stack

    def get_len(self):
        """Takes nothing and returns length of stack"""

        return len(self._stack)

    def get_top_color(self):
        """Takes nothing and returns the top color of a stack"""

        return self._stack[-1]

    def get_bottom_color(self):
        """Takes nothing and returns the bottom color of a stack"""

        return self._stack[0]

    def pop_bottom(self):
        """Removes bottom piece from stack; takes and returns nothing"""

        self._stack.pop(0)

    def pop_top(self, num=1):
        """Optionally takes number of times to pop a stack's top;
        returns nothing"""

        for i in range(num):
            self._stack.pop()

    def add_color(self, color):
        """Adds color/piece to top of stack; takes color and returns nothing"""

        self._stack.append(color)

    def add_to_stack(self, cur_stack, num):
        """Adds however many pieces from the current stack to the
        destination stack invoking this method; takes current stack
        object and number of pieces to add; returns nothing"""

        # We use the slicing operation on the list that is returned
        # and concatenate the two lists together to form new stack
        self._stack = self._stack + cur_stack.get_stack()[-num:]

        # Pop the pieces we removed from the current stack
        cur_stack.pop_top(num)


class FocusGame:
    """Represents the Focus/Domination board game using
    instances of the Space class for board representation"""

    def __init__(self, pl1, pl2):
        """Constructor for FocusGame class; takes two tuples containing info
        about name and color for each player"""

        # A dictionary that maps the player's name to info about that player
        self._pls = {pl1[0]: {"color": pl1[1], "reserve": 0, "captured": 0},
                     pl2[0]: {"color": pl2[1], "reserve": 0, "captured": 0}}

        # Last player to make a move
        self._last_move = ""

        # Initialize game board as a "2d dict" mapping integers/rows
        # to lists/columns
        self._board = dict()

        for i in range(0, 6, 2):
            self._board[i]     = [Space(pl1[1]), Space(pl1[1]), Space(pl2[1]),
                                  Space(pl2[1]), Space(pl1[1]), Space(pl1[1])]

            self._board[i + 1] = [Space(pl2[1]), Space(pl2[1]), Space(pl1[1]),
                                  Space(pl1[1]), Space(pl2[1]), Space(pl2[1])]

    def move_piece(self, name, cur, des, num_mv):
        """Moves a piece; takes name, current position, destination position,
        and number of pieces to move; returns a string or False"""

        # Check if the move is valid; called function returns False if invalid
        if not self.is_valid_move(name, cur, des, num_mv):
            return False

        # Create aliases for current and destination space/stack objects
        cur_stack = self._board[cur[0]][cur[1]]
        des_stack = self._board[des[0]][des[1]]

        # Evaluate and pop pieces from bottom if we overflow stack
        if num_mv + des_stack.get_len() > 5:
            self.eval_pop_bottom(name, des_stack, num_mv)

        # Add the number of pieces from the current to destination stack
        des_stack.add_to_stack(cur_stack, num_mv)

        return self.eval_move(name)

    def eval_move(self, name):
        """Evaluates the move and updates last move for the next player;
        takes name and returns relevant string depending on move outcome"""

        # Update the last player to make a move
        self._last_move = name

        # Return an appropriate message depending on the results of the move
        captured = self._pls[name]["captured"]
        return name + " Wins" if captured >= 6 else "successfully moved"

    def show_pieces(self, pos):
        """Shows pieces at position; takes position and returns stack-list"""

        return self._board[pos[0]][pos[1]].get_stack()

    def show_reserve(self, name):
        """Shows reserve count; takes name and returns reserve count"""

        return self._pls[name]["reserve"]

    def show_captured(self, name):
        """Shows captured count; takes name and returns captured count"""

        return self._pls[name]["captured"]

    def reserved_move(self, name, des):
        """Makes a reserve move; takes name and destination position;
        returns a string or False"""

        # Check if the move is valid; called function returns False if invalid
        if not self.is_valid_reserve_move(name, des):
            return False

        # Evaluate and pop a bottom piece if the stack is 5 tall
        if self._board[des[0]][des[1]].get_len() == 5:
            self.eval_pop_bottom(name, self._board[des[0]][des[1]], 1)

        # Add the piece to the top of the stack
        self._board[des[0]][des[1]].add_color(self._pls[name]["color"])

        # Decrement the number of pieces in reserve for this player
        self._pls[name]["reserve"] -= 1

        return self.eval_move(name)

    def eval_pop_bottom(self, name, des_stack, num_mv):
        """Evaluates and pops bottom pieces of a stack; takes name,
        destination stack and number of pieces to move; returns nothing"""

        # Evaluate and pop however many pieces from bottom to make room
        for i in range((num_mv + des_stack.get_len()) - 5):
            # Add own pieces from bottom to the reserve pile
            if des_stack.get_bottom_color() == self._pls[name]["color"]:
                self._pls[name]["reserve"] += 1
            # Add the opponent's pieces to the captured pile
            else:
                self._pls[name]["captured"] += 1

            # Pop the bottom piece from stack; shifts elements in list
            des_stack.pop_bottom()

    def is_valid_reserve_move(self, name, des):
        """Checks if reserve move is valid; takes name and destination
        position; returns False if invalid and True otherwise"""

        # Short circuits on first True; checks for reserve being
        # empty (0 is a falsy), the player's turn, and out of bounds
        return not (not self._pls[name]["reserve"] or
                    self._last_move == name or
                    not all(i in range(6) for i in des))

    def is_valid_move(self, name, cur, des, num_mv):
        """Checks if move is valid; takes name, current position, destination
        position and pieces to move; returns False if invalid and True
        otherwise"""

        # Short circuits on first True; checks player's turn, out of bounds,
        # invalid number of pieces selected, wrong color, diagonal move,
        # and not moving by number of pieces selected; with regard to the
        # last one we ensured that a row or col must be the same (no diagonal);
        # num_mv=0 for (0,0)->(0,5) etc. would be caught by the 3rd test
        return not (self._last_move == name or
                    not all(i in range(6) for i in (cur + des)) or
                    num_mv <= 0 or
                    num_mv > self._board[cur[0]][cur[1]].get_len() or
                    self._board[cur[0]][cur[1]].get_top_color()
                    != self._pls[name]["color"] or
                    des[0] != cur[0] and des[1] != cur[1] or
                    num_mv not in (abs(des[0] - cur[0]), abs(des[1] - cur[1])))

    def print_board(self):
        """Prints 6x6 board as lists; takes and returns nothing"""

        # Print the rows and columns
        for i in range(6):
            for j in range(6):
                print(self._board[i][j].get_stack(), end="")

            print()

        # Show info about the players; will be in dictionary format
        print(self._pls)
