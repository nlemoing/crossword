with open("grids.txt") as f:
    lines = f.readlines()

i = 0
while i*6 < len(lines):
    grid = lines[i*6+1:i*6+6]
    rotated_grid = [ "".join(grid[j][k] for j in range(5)) for k in range(5)]
    print("---")
    for l in range(5):
        print(f"{grid[l].strip()}   {rotated_grid[l]}")
    i += 1
