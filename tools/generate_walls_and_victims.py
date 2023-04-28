## Author: Tacla, UTFPR, 2023
##
## Generate walls from a input file with the following format per line:
## col_ini,row_ini,col_end,row_end
##
## It works for hor, ver and diag lines.
##
## Besides, if you define N_VICTIMS > 0, the program generates N_VICTIMS
## situated in random positions (except at coordinates where there is a wall).
##
## Outputs:
## - walls_file: contains the list of cells containing the walls
## - victims_file: a list of N_VICTIMS with random generated coordinates
##
## To show the grid, use the plot_2d_grid.py

import random

## To be configured
input_file = "walls_input.txt"   #input
walls_file = "walls_tst2.txt"         #out
victims_file = "victims.txt"     #out

MAX_ROWS = 30                    # grid size
MAX_COLS = 30
N_VICTIMS = 60                   # n random coordinates 

######

with open(input_file, "r") as f:
    walls_raw = f.readlines()
    walls = []
    for row in walls_raw:
        c1, r1, c2, r2 = map(int, row.split(','))
        if r1 == r2:
            # horizontal wall
            for c in range(c1, c2+1):
                walls.append((c, r1))
        elif c1 == c2:
            # vertical wall
            for r in range(r1, r2+1):
                walls.append((c1, r))
        else:
            # diagonal wall
            slope = (r2-r1) / (c2-c1)
            if slope > 0:
                for c in range(c1, c2+1):
                    r = r1 + int(round(slope*(c-c1)))
                    walls.append((c, r))
            else:
                for c in range(c1, c2+1):
                    r = r2 + int(round(slope*(c-c2)))
                    walls.append((c, r))

# Remove any duplicate points
walls = list(set(walls))

# Sort the wall coordinates by row number and then by column number
walls = sorted(walls, key=lambda x: (x[0], x[1]))

# Remove any blank lines from the output file
walls = [w for w in walls if w]

with open(walls_file, "w") as f:
    for wall in walls:
        f.write(f"{wall[0]},{wall[1]}\n")

# Generate N random points that do not coincide with any of the wall coordinates or any previously generated points
points = []
while len(points) < N_VICTIMS:
    r = random.randint(1, MAX_ROWS)
    c = random.randint(1, MAX_COLS)
    if (c, r) not in walls and (c, r) not in points:
        points.append((r, c))

if N_VICTIMS > 0:
    # Sort the points by row number and then by column number
    points = sorted(points, key=lambda x: (x[0], x[1]))

    # Write the points to the output file, one point per line in the format row, column
    with open(victims_file, "w") as f:
        for point in points:
            f.write(f"{point[0]}, {point[1]}\n")
