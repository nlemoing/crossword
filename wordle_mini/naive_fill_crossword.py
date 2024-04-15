from typing import List, Dict, Tuple, Optional, Generator
from copy import deepcopy

class Criterion:
    def __init__(self, letter: int, position: int):
        self.letter = letter
        self.position = position

    def matches(self, word: List[int]):
        return word[self.position] == self.letter
    
    def __repr__(self):
        return f"{chr(self.letter)} at position {self.position}"

class Grid:
    def __init__(self, input: List[str]):
        self.grid = [[ ord(c) for c in l.strip() ] for l in input]
        self.height = len(self.grid)
        self.width = len(self.grid[0])
        self.clues: Dict[str, Tuple[int, int]] = {}
        clues = 1
        for r in range(self.height):
            for c in range(self.width):
                inc = False
                if self.is_ob(r, c - 1):
                    self.clues[f"{clues}A"] =  (r, c)
                    inc = True
                if self.is_ob(r - 1, c):
                    self.clues[f"{clues}D"] =  (r, c)
                    inc = True
                if inc:
                    clues += 1
                
    def __repr__(self):
        s = "~~~~~ Grid: ~~~~~\n"
        for row in self.grid:
            for c in row:
                s += chr(c)
            s += "\n"
        # s += "\n"
        # s += "~~~~~ Clues: ~~~~~\n"
        # for clue in self.clues:
        #     s += f"{clue}: ({self.clues[clue]})\n"
        return s

    def is_ob(self, r, c):
        return r <= -1 or r >= self.height or c <= -1 or c >= self.width or self.grid[r][c] == ord('#')
    
    def clue_iterator(self, clue) -> Generator[Tuple[int, int], None, None]:
        r, c = self.clues[clue]
        dir = clue[1]
        while not self.is_ob(r, c):
            yield r, c
            if dir == "A":
                c += 1
            else:
                r += 1

    def is_filled(self, clue):
        r, c = self.clues[clue]
        dir = clue[1]
        while not self.is_ob(r, c):
            if self.grid[r][c] == ord('.'):
                return False
            if dir == "A":
                c += 1
            else:
                r += 1
        return True
    
    def is_complete(self):
        for r in range(self.height):
            for c in range(self.width):
                if self.grid[r][c] == ord('.'):
                    return False
        return True
    
    def criteria_for_clue(self, clue) -> List[Criterion]:
        r, c = self.clues[clue]
        dir = clue[1]
        criteria = []
        i = 0
        while not self.is_ob(r, c):
            if self.grid[r][c] != ord('.'):
                criteria.append(Criterion(self.grid[r][c], i))
            i += 1
            if dir == "A":
                c += 1
            else:
                r += 1
        return criteria
    
    def next_unfilled_clue(self) -> Optional[str]:
        most_criteria = -1
        next_clue = None
        for clue in self.clues:
            if not self.is_filled(clue) and (l := len(self.criteria_for_clue(clue))) > most_criteria:
                most_criteria = l
                next_clue = clue
        return next_clue    
    
    def insert(self, clue: str, match: List[int]):
        i = 0
        for r, c in self.clue_iterator(clue):
            self.grid[r][c] = match[i]
            i += 1

class Words:
    def __init__(self, input: List[str]):
        self.words = [[ord(c) for c in s.strip()] for s in input]
    
    def matching_words(self, criteria: List[Criterion]):
        return [w for w in self.words if all(c.matches(w) for c in criteria)]

grid = Grid(open("sample.txt").readlines())
words = Words(open("wordle.txt").readlines())

def neighbors(grid: Grid, words: Words) -> Generator[Grid, None, None]:
    clue = grid.next_unfilled_clue()
    if clue is not None:
        criteria = grid.criteria_for_clue(clue)
        matches = words.matching_words(criteria)
        for match in matches:
            nbr = deepcopy(grid)
            nbr.insert(clue, match)
            yield nbr


def solve(grid: Grid, words: Words) -> Optional[Grid]:
    if grid.is_complete():
        return grid
    for nbr in neighbors(grid, words):
        sol = solve(nbr, words)
        if sol:
            print(sol)
    return None

print(solve(grid, words))
