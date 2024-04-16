# Sparse grid constructor tool

Goal: given a list of words, create a grid where those words intersect.
Unchecked crosses are allowed because each word is related to the theme

## What makes a good grid?

Denser = better
Density = # of letters / (width * height)

## Formulation as search

Start with a blank grid and a word bank
Add a word at (0,0)
Given a grid, try to add words to it
Tradeoff between density and adding words

## Current state

Have a grid that we can get the neighbours for
Need to implement search with prioritization
