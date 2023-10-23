# Crossword constructor tool

Step 1: The 'ideal' mini: 5x5 grid, no black squares
Word list: wordle original 2310 words
Sourced from https://web.ma.utexas.edu/users/rusin/wordle/official

.puz format is used widely by "commercial software for crossword puzzles",
and there's an informal description of the spec [here](https://code.google.com/archive/p/puz/wikis/FileFormat.wiki) but it's fairly complex for our use case. Includes a bunch of
info about solving state, rebus clues (where multiple letters can fit in a square), checksums, etc.

For us, a crossword file will be a text file containing letters arranged in a grid. 
. represents an open square, # represents a black square. Our goal is to write a program
that accepts a grid file (which may be partially filled) and return a list of potential words that could be added in the first open clue.

## Attempt 1 (naive fill): search by checking the most constrained clue first

This is essentially brute force, but with a heuristic that can help us avoid spending too much
time in the iteration phase. By checking the most constrained clue first, we're more likely
to exit early. E.g. if we look at partial grid:
abode
decor
.....
.....
.....
the third row has no restrictions, so we could put anything there and continue on. However,
we probably want to satisfy the clues that are harder to satisfy first, otherwise we'll waste
a lot of time. So, it might make more sense to try to fill the first column first instead
since we may exit early.

Churned away with some poor seed entries at the top (abode)
Produced the following result for chimp at the top:
chimp
audio
brisk
arose
lymyr
This would be great, except the last across answer isn't real!
This is because we aren't checking whether there are candidates for the neighbor grid before marking it as complete.
However, this illustrates the importance of a good seed. Although the "chimp" seed never
produced a well-filled grid, it was 90% of the way there, whereas the "abode" seed never produced any valid grids.

My algorithm also produced this grid at one point, which breaks an important rule in crosswords: no repeated words. (it has 2)
chimp
humor
imbue
rouse
preen

These two things can be fixed by changing the algorithm slightly.
The first is to pick a better heuristic for searching. We can improve on this by 
taking some ideas from this paper: https://cdn.aaai.org/AAAI/1990/AAAI90-032.pdf
Their idea is to start by ranking each candidate by the number of possible words that
can cross it. This is similar to the heuristic we were using earlier but it does a much
better job of looking ahead and at looking at the whole grid (not just the clue being filled).
