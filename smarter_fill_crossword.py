from typing import List, Tuple, Optional, Set
from copy import deepcopy
from random import choices
    
class Clue:
    def __init__(self, number: int, across: bool, square: Tuple[int, int]):
        self.number = number
        self.across = across
        self.square = square

    def __repr__(self): 
        return f'{self.number}{"A" if self.across else "D"}'

def match(word: str, slot: str) -> bool:
    return len(word) == len(slot) and all(slot[i] == '.' or slot[i] == word[i] for i in range(len(word)))

class Grid:
    def __init__(self, input: List[str]):
        self.grid = [[ c for c in l.strip() ] for l in input]
        self.height = len(self.grid)
        self.width = len(self.grid[0])
        self.used_words: Set[str] = set()
    
    def __repr__(self):
        s = "~~~~~ Grid: ~~~~~\n"
        for row in self.grid:
            for c in row:
                s += c
            s += "\n"
        return s

    def is_ob(self, r, c):
        return r <= -1 or r >= self.height or c <= -1 or c >= self.width or self.grid[r][c] == '#'
    
    def get_word(self, clue: Clue) -> str:
        r, c = clue.square
        s = ''
        while not self.is_ob(r, c):
            s += self.grid[r][c]
            if clue.across:
                c += 1
            else:
                r += 1
        return s
    
    def insert(self, clue: Clue, word: str):
        r, c = clue.square
        i = 0
        while not self.is_ob(r, c):
            self.grid[r][c] = word[i]
            i += 1
            if clue.across:
                c += 1
            else:
                r += 1
        self.used_words.add(word)

class Clues:
    def __init__(self, grid: Grid):
        self.clues: List[Clue] = []
        self.across_clue_at_square: List[List[Optional[Clue]]] = [[None for _ in range(grid.width)] for _ in range(grid.height)]
        self.down_clue_at_square: List[List[Optional[Clue]]] = [[None for _ in range(grid.width)] for _ in range(grid.height)]
        self.used_words: Set[str] = set()
        clues = 1
        for r in range(grid.height):
            for c in range(grid.width):
                inc = False
                if grid.is_ob(r, c - 1):
                    self.clues.append(Clue(clues, True, (r, c)))
                    inc = True
                if grid.is_ob(r - 1, c):
                    self.clues.append(Clue(clues, False, (r, c)))
                    inc = True
                if inc:
                    clues += 1
        for clue in self.clues:
            r, c  = clue.square
            while not grid.is_ob(r, c):
                if clue.across:
                    self.across_clue_at_square[r][c] = clue
                    c += 1
                else:
                    self.down_clue_at_square[r][c] = clue
                    r += 1
    
def most_constrained_unfilled_clue(grid: Grid, clues: Clues, words: List[str]) -> Tuple[Optional[Clue], List[str]]:
    least_matching_words = words + ['xxxxx']
    most_constrained_clue = None
    for clue in clues.clues:
        s = grid.get_word(clue)
        if not '.' in s:
            continue
        matching_words = []
        for word in words:
            if word not in grid.used_words and match(word, s):
                matching_words.append(word)
        if len(matching_words) > 0 and len(matching_words) < len(least_matching_words):
            least_matching_words = matching_words
            most_constrained_clue = clue
    return most_constrained_clue, least_matching_words
    
def crossing_clues(grid: Grid, clue: Clue, clues: Clues) -> List[Clue]:
    r, c = clue.square
    crossing_clues: List[Clue] = []
    while not grid.is_ob(r,c):
        crossing_clue = clues.down_clue_at_square[r][c] if clue.across else clues.across_clue_at_square[r][c]
        assert(crossing_clue is not None)
        crossing_clues.append(crossing_clue)
        if clue.across:
            c += 1
        else:
            r += 1
    return crossing_clues
    
def possibilities_score(grid: Grid, clue: Clue, clues: Clues, words: List[str]) -> int:
    p = 1
    for crossing_clue in crossing_clues(grid, clue, clues):
        s = grid.get_word(crossing_clue)
        if '.' not in s:
            continue
        matches = sum(1 if w not in grid.used_words and match(w, s) else 0 for w in words)
        if matches == 0:
            return 0
        p *= matches
    return p

def neighbors(grid: Grid, clues: Clues, words: List[str]) -> List[Tuple[int, Grid]]:
    nbrs: List[Tuple[int, Grid]] = []
    clue, matching_words = most_constrained_unfilled_clue(grid, clues, words)
    if clue is None:
        return nbrs
    for candidate_word in matching_words:
        nbr = deepcopy(grid)
        nbr.insert(clue, candidate_word)
        score = possibilities_score(nbr, clue, clues, words)
        if score > 0:
            nbrs.append((score, nbr))
    return sorted(nbrs, reverse=True, key=lambda x: x[0])

def is_complete(grid: Grid, clues: Clues, words: List[str]) -> bool:
    for r in range(grid.height):
        for c in range(grid.width):
            if grid.grid[r][c] == '.':
                return False
    for clue in clues.clues:
        if grid.get_word(clue) not in words:
            return False
    return True

def solve(grid: Grid, clues: Clues, words: List[str]) -> Optional[Grid]:
    if is_complete(grid, clues, words):
        return grid

    for _, nbr in neighbors(grid, clues, words):
        sol = solve(nbr, clues, words)
        if sol:
            return sol
    return None

grid = Grid(open("sample.txt").readlines())
clues = Clues(grid)
words = [s.strip() for s in open("wordle.txt").readlines()]

print(solve(grid, clues, words))
