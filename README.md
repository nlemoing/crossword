# Crossword constructor tool

Step 1: The 'ideal' mini: 5x5 grid, no black squares
Word list: wordle original 2310 words
Sourced from https://web.ma.utexas.edu/users/rusin/wordle/official

.puz format is used widely by "commercial software for crossword puzzles",
and there's an informal description of the spec [here](https://code.google.com/archive/p/puz/wikis/FileFormat.wiki) but it's fairly complex for our use case. Includes a bunch of
info about solving state, rebus clues (where multiple letters can fit in a square), checksums, etc.

For us, a crossword file will be a text file containing letters arranged in a grid. 
. represents an open square, # represents a black square.

## Formulation
Our goal is to take a grid as input and search for a grid such that:
* all of the original letters and black tiles are in the same place as they were in the input
* there are no blank squares
* every clue represents a valid word

## Brute force

Based on our word list with 2310 words, there are roughly 2310^5 = 6,577,485,501,510,000 possibilities
for the across clues (in reality, this is slightly smaller because we can't repeat words, but it's not meaningfully different). One strategy might be to run through all of these combinations and check
whether they produce valid down clues as well, but this is... unlikely to be fruitful. For a sense of
scale, let's say we were able to check 1 million of these possibilities per second (which is already very
optimistic). In that case, it would still take us 208 years to run through all of the combinations.

This option is kind of like a random guess-and-check strategy: the checks we're doing aren't letting us
narrow down the number of options we have to choose from.

## Search
Instead of searching via brute force, it can be helpful to think of the grids we're searching as nodes
in a graph. From any partially-filled grid, we can move to another grid by taking an unfilled clue and
filling it with a valid word. Our strategy is to search this graph to find a grid that matches our constraints
above. Since we're going to be searching a graph, we need to choose between breadth-first and depth-first
search.

Breadth-first search is good at examining the entire solution space and finding the most optimal solution 
efficiently. Is this a good fit for us?
* Our search space is really wide, and our valid solutions are far away. Each grid has thousands of potential neighbours, and to get to a valid solution, we have to take as many steps as there are clues in the grid. Breadth-first search will get caught examining all the neighbors and won't ever make it to the end.
* There's no clear notion of what it means to be optimal. Is it better to have unique words that stretch people's vocabulary? Is it better to include interesting letters, or different combinations of letters? Does the word choice not matter at all if we can come up with interesting clues? We might have heuristics for what makes a crossword better or worse, but at the end of the day, crosswords are made for people to solve, and our program won't be as good as a person is at determining whether our grid is good.
* Measures of quality are global, not local. The quality of a puzzle isn't something that can be determined on the fly. We could have a promising start with exciting entries, only for it to fall short because the only crossing clues that make it work are clunky words that no one uses in real life. 

Therefore, we'll go with depth-first search, which will look like the following:
1. Pick a clue to fill.
2. For each possible word that we can fill, search the grid that results from filling that word
3. If none of the possible words resulted in a valid grid, then there's no valid grid from this starting point, so we can return. There's no need to check the rest of the clues for this grid.

To make this work well, we'll need to make use of our knowledge of crosswords to direct our search and eliminate certain possibilities that we know won't be fruitful.



1. First clue, naive word ordering
2. Clue with most filled letters, naive word ordering
3. Clue with fewest possibilities, word ordering by possibilities in resulting grid

## Attempt 1: naive fill
Here, we make no attempt to use heuristics; we always pick the first unfilled clue,
and we always pick a random word to explore first.

This approach is able to succeed on small, partially filled grids. On the one below,
the program returns almost instantly:
```
allow
belch
agate
.....
.....
```
However, if we run the program on a grid with one fewer clue filled in, it takes 8 seconds.

## Attempt 2: clue with most filled letters, naive word ordering

If we look at partial grid:
```
abode
decor
.....
.....
.....
```
The third row has no restrictions, so we could put anything there and continue on. However,
we probably want to fill the clues that are harder to satisfy first, otherwise we'll waste
a lot of time. So, it might make more sense to try to fill the first column first instead
since we realize there are no valid grids earlier.

# Attempt 3: clue with fewest valid remaining options, word ordering by number of possibilities for neighbours
This approach modifies the clue choice to do a better job of checking for constrained clues based on
the remaining options available.

Consider the following partial grid:
```
abode
devil
.....
.....
.....
```

The previous approach would have picked 1D as the first clue to fill. However, we could narrow things down more by starting with 3D clue, since there are only 5 options in our dictionary that begin with `ov`, compared to 11 that begin with `ad`. This check is more expensive to perform since it involves checking more matches; however, it does tend to perform better in practice because it's able to prune things quite
aggressively.

This is also the first time we're making a word ordering choice. Our strategy is going to be to start with
words that leave more possibilities for crossing clues. Here, we're not trying to narrow possibilities like
we were when choosing a clue to start with. It didn't matter which clue we started exploring since each one 
could lead to the same solution, so it made sense to pick the clue that resulted in the fewest paths to 
explore. However, with word choice, we want to increase the likelihood that the neighbours we explore are also
valid.

I ran this process for a few hours on my laptop and it generated 51 grids. The first was
available within a minute and I used it to build this crossword:
https://crosshare.org/crosswords/BcOFnK6cWhK4rsoxLvGr/taking-measurements

I actually rotated the grid from the configuration my program spit out because it resulted
in some interested stacked across clues that shared a theme. How serendipitous!

## Further improvements

There's still a lot to be desired in terms of efficiency:
* Match efficiency: we're still running through each word and checking it via string comparison
* Small dictionary: since the dictionary we're using is small, we can more easily check options exhaustively, but it also means it takes longer to find valid fill since there are fewer valid grids.
* We're spending a long time finding the most optimal clue to start with when clues have several valid options

Lots of good ideas sourced from https://cdn.aaai.org/AAAI/1990/AAAI90-032.pdf
Kudos to crosshare, which have an open-source platform that includes an autofiller: https://github.com/crosshare-org/crosshare

