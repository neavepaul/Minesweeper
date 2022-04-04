import random


class Minesweeper():

    def __init__(self, height, width, mines):
        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        self.mines_found = set()

    def print(self):
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        count = 0

        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                if (i, j) == cell:
                    continue

                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        return self.mines_found == self.mines


class Sentence():

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        if len(self.cells) == self.count:
            return set(self.cells)
        else:
            return set()

    def known_safes(self):
        if self.count == 0:
            return set(self.cells)
        else:
            return set()

    def mark_mine(self, cell):
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1
            return 1
        return 0

    def mark_safe(self, cell):
        if cell in self.cells:
            self.cells.remove(cell)
            return 1
        return 0


class MinesweeperAI():

    def __init__(self, height, width):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # Set of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        counter = 0
        self.mines.add(cell)
        for sentence in self.knowledge:
            counter += sentence.mark_mine(cell)
        return counter

    def mark_safe(self, cell):
        counter = 0
        self.safes.add(cell)
        for sentence in self.knowledge:
            counter += sentence.mark_safe(cell)
        return counter

    def add_knowledge(self, cell, count):
        self.moves_made.add(cell)

        self.mark_safe(cell)

        i, j = cell
        neighbors = set()
        for a in range(max(0, i-1), min(i+2, self.height)):
            for b in range(max(0, j-1), min(j+2, self.width)):
                if (a, b) != (i, j):
                    neighbors.add((a, b))
        self.knowledge.append(Sentence(neighbors, count))

        self.update_self_and_sentences()


        guesses = self.new_guesses()

        while guesses:
            for sentence in guesses:
                self.knowledge.append(sentence)

            self.update_self_and_sentences()


            guesses = self.new_guesses()

    
    def make_safe_move(self):
        for move in self.safes:
            if move not in self.moves_made and move not in self.mines:
                return move

        return None

    def make_random_move(self):
        for i in range(0, self.height):
            for j in range(0, self.width):
                move = (i, j)
                if move not in self.mines and move not in self.moves_made:
                    return move

        return None


    def new_guesses(self):
        guesses = []
        removals = []

        for sentence1 in self.knowledge:
            if sentence1.cells == set():
                removals.append(sentence1)
                continue
            for sentence2 in self.knowledge:
                if sentence2.cells == set():
                    removals.append(sentence2)
                    continue
                if sentence1 != sentence2:
                    if sentence2.cells.issubset(sentence1.cells):
                        diff_cells = sentence1.cells - sentence2.cells
                        diff_count = sentence1.count - sentence2.count
                        new_guess = Sentence(diff_cells, diff_count)
                        if new_guess not in self.knowledge:
                            guesses.append(new_guess)

        self.knowledge = [x for x in self.knowledge if x not in removals]
        return guesses

    def update_self_and_sentences(self):
        counter = 1
        while counter:
            counter = 0
            for sentence in self.knowledge:
                for cell in sentence.known_safes():
                    self.mark_safe(cell)
                    counter += 1
                for cell in sentence.known_mines():
                    self.mark_mine(cell)
                    counter += 1
            for cell in self.safes:
                counter += self.mark_safe(cell)
            for cell in self.mines:
                counter += self.mark_mine(cell)
