from math import sqrt
from random import shuffle


class Puzzle:
    def __init__(self, puzzle_input):
        self.state = puzzle_input
        self.dimension = sqrt(len(puzzle_input))
        if not self.dimension.is_integer():
            raise (Exception("Not the right format"))
        self.dimension = int(self.dimension)
        self.goal_cords = self.generate_goal_cords()

        self.predecessor = None
        self.path_cost = 0

    def __str__(self):
        string = ""
        for i in range(len(self.state)):
            if i % self.dimension == 0:
                string += "\n"
            string += str(self.state[i]) + "\t"

        return string

    def __eq__(self, other):
        return self.state == other.state

    def generate_goal_cords(self):
        cords = dict()
        j = 0
        for i in range(self.dimension ** 2 - 1):
            cords[i + 1] = (j, i % self.dimension)
            if i % self.dimension == self.dimension - 1:
                j += 1
        return cords

    # calculate number of squares to desired location for each tile
    def manhatten_distance(self):
        distance = 0
        j = 0
        for i in range(len(self.state)):
            entry = self.goal_cords.get(self.state[i])
            if entry is not None:
                distance += abs(entry[0] - j) + abs(entry[1] - (i % self.dimension))
            if i % self.dimension == self.dimension - 1:
                j += 1

        return distance

    def up_viable(self):
        return self.state.index(0) >= self.dimension

    def right_viable(self):
        return (self.state.index(0) + 1) % self.dimension != 0

    def down_viable(self):
        return self.state.index(0) < len(self.state) - self.dimension

    def left_viable(self):
        return self.state.index(0) % self.dimension != 0

    def up(self):
        state_copy = self.state[:]
        pos = state_copy.index(0)
        state_copy[pos] = state_copy[pos - self.dimension]
        state_copy[pos - self.dimension] = 0

        return Puzzle(state_copy)

    def right(self):
        state_copy = self.state[:]
        pos = state_copy.index(0)
        state_copy[pos] = state_copy[pos + 1]
        state_copy[pos + 1] = 0

        return Puzzle(state_copy)

    def down(self):
        state_copy = self.state[:]
        pos = state_copy.index(0)
        state_copy[pos] = state_copy[pos + self.dimension]
        state_copy[pos + self.dimension] = 0

        return Puzzle(state_copy)

    def left(self):
        state_copy = self.state[:]
        pos = state_copy.index(0)
        state_copy[pos] = state_copy[pos - 1]
        state_copy[pos - 1] = 0

        return Puzzle(state_copy)


class Game:
    def __init__(self, puzzle):
        self.puzzle = puzzle
        goal = []
        for i in range(self.puzzle.dimension ** 2):
            goal.append(i + 1)
        goal[-1] = 0
        self.goal = Puzzle(goal)

    def play(self):
        print("----------------------------")
        move_count = 0
        while self.puzzle != self.goal:
            print(self.puzzle)

            user_input = input("Schiebe das Feld: [W, A, S, D]")
            if user_input.lower() == "s" and self.puzzle.down_viable():
                self.puzzle = self.puzzle.down()
                move_count += 1
            elif user_input.lower() == "a" and self.puzzle.left_viable():
                self.puzzle = self.puzzle.left()
                move_count += 1
            elif user_input.lower() == "w" and self.puzzle.up_viable():
                self.puzzle = self.puzzle.up()
                move_count += 1
            elif user_input.lower() == "d" and self.puzzle.right_viable():
                self.puzzle = self.puzzle.right()
                move_count += 1

        print("Geschafft. Du hast {} Aktionen gebraucht.".format(move_count))


class Solver:
    def __init__(self, start_puzzle):
        self.start = start_puzzle
        goal = []
        for i in range(self.start.dimension ** 2):
            goal.append(i + 1)
        goal[-1] = 0
        self.goal = Puzzle(goal)

    # find the element with the minimum f value
    # f = cost of path so far and cost from there on
    def get_element_with_min_f_value(self, opened):
        minimum_element = None
        minimum_distance = None
        for i in range(len(opened)):
            distance = opened[i].path_cost + opened[i].manhatten_distance()
            if minimum_element is None or distance < minimum_distance:
                minimum_element = opened[i]
                minimum_distance = distance

        return opened.pop(opened.index(minimum_element))

    def get_successors(self, state):
        successors = []
        if state.up_viable():
            successors.append(state.up())
        if state.right_viable():
            successors.append(state.right())
        if state.down_viable():
            successors.append(state.down())
        if state.left_viable():
            successors.append(state.left())

        return successors

    def expand_successors(self, current, closed, opened):
        for successor in self.get_successors(current):
            if successor in closed:
                continue
            # calculate new path cost
            new_path_cost = current.path_cost + 1
            # do nothing if there is a better path to successor
            if successor in opened and new_path_cost >= successor.path_cost:
                continue
            # memorize which element came before the successor
            successor.predecessor = current
            successor.path_cost = new_path_cost

            if successor not in opened:
                opened.append(successor)

    def solve(self):
        solution = False
        opened = [self.start]
        closed = []
        while True:
            # get element with lowest f value
            current = self.get_element_with_min_f_value(opened)
            # stop if goal is reached
            if current == self.goal:
                self.goal = current
                solution = True
                break
            # memorize, this element has been visited
            closed.append(current)
            # expand successors
            self.expand_successors(current, closed, opened)

            # no solution found
            if len(opened) == 0:
                break

        if solution:
            print("Solution found:")
            self.print_path()
        else:
            print("No solution found")

    def print_path(self):
        states = []
        current = self.goal
        while current.predecessor is not None:
            states.append(current)
            current = current.predecessor
        states.append(self.start)
        print("The solution took {} moves.".format(len(states)))
        for state in reversed(states):
            print(state)


""" 
If N is odd, then puzzle instance is solvable if number of inversions is even in the input state.
If N is even, puzzle instance is solvable if 
the blank is on an even row counting from the bottom (second-last, fourth-last, etc.) and number of inversions is odd.
the blank is on an odd row counting from the bottom (last, third-last, fifth-last, etc.) and number of inversions is even.
For all other cases, the puzzle instance is not solvable."""


# https://www.geeksforgeeks.org/check-instance-15-puzzle-solvable/
def solvable_input(numbers):
    dimension = int(sqrt(len(numbers)))

    inversions = count_inversions(numbers)

    if dimension % 2 == 1:
        return inversions % 2 == 0
    else:

        if inversions % 2 == 0 and not zero_on_even_row_num_from_bottom(numbers, dimension):
            return True
        elif inversions % 2 == 1 and zero_on_even_row_num_from_bottom(numbers, dimension):
            return True
        else:
            return False


def count_inversions(numbers):
    inversions = 0
    for i in range(len(numbers)):
        for j in range(i, len(numbers)):
            if numbers[i] > numbers[j]:
                inversions += 1
    return inversions


def zero_on_even_row_num_from_bottom(numbers, dimension):
    even = True
    for i in reversed(range(len(numbers))):
        if numbers[i] == 0:
            return even

        if i % dimension == 0:
            even = not even


dimension = 3  # change this to have a bigger field
origin_numbers = [i for i in range(dimension ** 2)]
while True:
    shuffle(origin_numbers)
    if solvable_input(origin_numbers):
        break
start = Puzzle(origin_numbers)
print("Starting numbers are: " + "".join([str(i) for i in origin_numbers]))

solver = Solver(start)
solver.solve()

game = Game(start)
game.play()  # goal is to have the 0 in the bottom right

# 1	 2	3
# 4	 5	6
# 7	 8	0
