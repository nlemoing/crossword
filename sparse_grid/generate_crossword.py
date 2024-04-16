from __future__ import annotations

from enum import Enum
from typing import Optional, Tuple, NamedTuple, Callable
import copy

WORDS = [s.strip() for s in open("sparse_grid/words.txt").readlines()]

class Direction(Enum):
    ACROSS = 0
    DOWN = 1

class Intersection(NamedTuple):
    character: str
    row: int
    col: int
    valid: bool

class WordAssignment(NamedTuple):
    word_index: int
    row: int
    col: int
    direction: Direction

    def word_length(self) -> int:
        return len(WORDS[self.word_index])
    
    def intersects(self, other: WordAssignment) -> Optional[Intersection]:

        if self.direction == other.direction:
            return None
        
        a, d = (self, other) if self.direction == Direction.ACROSS else (other, self)
        d_in_range = d.col >= a.col and d.col < a.col + a.word_length()
        a_in_range = a.row >= d.row and a.row < d.row + d.word_length()
        
        if d_in_range and a_in_range:
            a_char = WORDS[a.word_index][d.col - a.col]
            d_char = WORDS[d.word_index][a.row - d.row]
            return Intersection(a_char, a.row, d.col, a_char == d_char)  
        else:
            return None
        
    def touches(self, other: WordAssignment) -> bool:
        e1, e2 = self.endpoints(True)
        o1, o2 = other.endpoints(False)
        return (e1[0] >= o1[0] and e1[0] <= o2[0] and e1[1] >= o1[1] and e1[1] <= o2[1]) or \
           (e2[0] >= o1[0] and e2[0] <= o2[0] and e2[1] >= o1[1] and e2[1] <= o2[1])

    def endpoints(self, outer: bool) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        adj = 1 if outer else 0
        if self.direction == Direction.ACROSS:
            return (self.row, self.col - adj), (self.row, self.col + self.word_length() - 1 + adj)
        else:
            return (self.row - adj, self.col), (self.row + self.word_length() - 1 + adj, self.col)


class OpenSquare(NamedTuple):
    character: str
    row: int
    col: int
    direction: Direction

# partition a list into two lists, the left one containing values where the predicate is true
def partition[T](l: list[T], pred: Callable[[T], bool]):
    y: list[T] = []
    n: list[T] = []
    for item in l:
        if pred(l):
            y.append(item)
        else:
            n.append(item)
    return y, n

def isAcross(w: WordAssignment) -> bool:
    return w.direction == Direction.ACROSS

class State:
    def __init__(self, start_word_index: int):
        self.assignments = set[WordAssignment]()
        self.assignments.add(WordAssignment(start_word_index, 0, 0, Direction.ACROSS))
        self.open_squares = [
            OpenSquare(c, 0, i, Direction.DOWN)
            for i, c in enumerate(WORDS[start_word_index])
        ]
    
    def __hash__(self) -> int:
        return self.assignments._hash()
    
    def bounds(self) -> Tuple[int, int, int, int]:
        min_row = min(x.row for x in self.assignments)
        min_col = min(x.col for x in self.assignments)
        # Exclusive endpoints
        max_row = max(x.row + 1 if x.direction == Direction.ACROSS else x.row + x.word_length() for x in self.assignments)
        max_col = max(x.col + 1 if x.direction == Direction.DOWN else x.col + x.word_length() for x in self.assignments)
        return min_row, min_col, max_row, max_col
    
    def __repr__(self) -> str:
        min_row, min_col, max_row, max_col = self.bounds()
        letters = dict[Tuple[int, int], str]()
        s = ""
        for assignment in self.assignments:
            for i, char in enumerate(WORDS[assignment.word_index]):
                if assignment.direction == Direction.ACROSS:
                    letters[(assignment.row, assignment.col + i)] = char
                else:
                    letters[(assignment.row + i, assignment.col)] = char
        for r in range(min_row, max_row):
            for c in range(min_col, max_col):
                s += letters.get((r,c), ".")        
            s += "\n"
        return s
    
    def add(self, word_assignment: WordAssignment) -> Optional[State]:
        closed_squares = set[Tuple[int, int]]()
        for existing_assignment in self.assignments:
            intersection = word_assignment.intersects(existing_assignment)
            touch = word_assignment.touches(existing_assignment) or existing_assignment.touches(word_assignment)
            if (intersection is not None and not intersection.valid) or touch:
                return None
            elif intersection is not None:
                closed_squares.add((intersection.row, intersection.col))
                closed_squares.add((intersection.row + 1, intersection.col))
                closed_squares.add((intersection.row - 1, intersection.col))
                closed_squares.add((intersection.row, intersection.col + 1))
                closed_squares.add((intersection.row, intersection.col - 1))
        
        new_state = copy.deepcopy(self)
        new_state.assignments.add(word_assignment)
        new_state.open_squares = [
            square
            for square in self.open_squares + [
                OpenSquare(char, word_assignment.row, word_assignment.col + i, Direction.DOWN) if word_assignment.direction == Direction.ACROSS
                else OpenSquare(char, word_assignment.row + i, word_assignment.col, Direction.ACROSS)
                for i, char in enumerate(WORDS[word_assignment.word_index])
            ]
            if (square.row, square.col) not in closed_squares
        ]

        return new_state

    
    def quality() -> float:
        # quality is some mix of number of words and density, TBD
        return 0

    
def get_biggest_index(l: list[str]):
    max_so_far = -1, -1
    for i, w in enumerate(l):
        if len(w) > max_so_far[1]:
            max_so_far = i, len(w)
    return max_so_far[0]

def neighbours(state: State) -> list[State]:
    # First, get open squares. An open square is any square where there's already a letter and where
    # we can add a word crossing it. To make things easy, we'll rule out anything that's within one 
    # square of an intersection (otherwise, we'd have to worry about stacked two letter words).
    taken_words = set(x.word_index for x in state.assignments)
    potential_assignments = list[WordAssignment]()
    neighbours = list[State]()
    for open_square in state.open_squares:
        for word_index in range(len(WORDS)):
            if word_index in taken_words:
                continue

            for i in range(len(WORDS[word_index])):
                if open_square.character == WORDS[word_index][i]:
                    if open_square.direction == Direction.ACROSS:
                        potential_assignments.append(
                            WordAssignment(
                                word_index,
                                open_square.row,
                                open_square.col - i,
                                Direction.ACROSS
                            )
                        )
                    else:
                        potential_assignments.append(
                            WordAssignment(
                                word_index,
                                open_square.row - i,
                                open_square.col,
                                Direction.DOWN
                            )
                        )

    for potential_assignment in potential_assignments:
        nbr = state.add(potential_assignment)
        if nbr is not None:
            neighbours.append(nbr)

    return neighbours

def generate():
    # To get us started, we'll always start by getting the biggest word and putting it at 0,0 going across
    # This cuts down the solution space and gives us a good jumping off point for future words
    biggest_word = get_biggest_index(WORDS)
    start_state = State(biggest_word)
    m = start_state.add(WordAssignment(3, 0, 6, Direction.DOWN))
    o = m.add(WordAssignment(2, 2, 5, Direction.ACROSS))
    n = o.add(WordAssignment(1, 0, 3, Direction.DOWN))
    print(n)
    
    
generate()