## Read the walls file with coordinates of walls, the victims file containing
## the victims' coordinates, and a folder containing clusters of victims and
## plots the 2D grid.
##
## Each cluster file has no header and the format for each line is as follows:
## victim id(int), column or x(int), row or y(int), severity (float), sev. label (int)
##
## The 2D grid's origin is at the top left corner. Indexations is (column, row).
## It prints the metrics per quadrant (victims and walls per quadrant)
##    upper left | upper right
##    ------------------------
##    lower left | lower right
##
## Besides, it draws a rectangle around each cluster and lines between the victims
## according the order they appear in the cluster file. Stats on victims per cluster
## are printed according to the values found in each cluster file.

import pygame
import os
import random

## Input files and folders
data_folder = "./datasets/data_100x80_132vic"
env_file = "env_size.txt"
walls_file = "env_walls.txt"
victims_file = "env_victims.txt"
cluster_folder = "./clusters"                     # Directory containing cluster files 

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YEL = (255, 255, 0)
GRAY = (128, 128, 128)

# Function to generate random colors
def generate_random_color():
    return random.randint(50, 205), random.randint(50, 205), random.randint(50, 205)

# Open config file
env_dic = {}
with open(os.path.join(data_folder, env_file), "r") as file:
    # Read each line of the file
    for line in file:
        # Split the line into words
        words = line.split()

        # Get the keyword and value
        keyword = words[0]
        raw_value = words[1]

        # casts the value 
        if keyword == "BASE":
            value = [int(i) for i in raw_value.split(',')]
        elif keyword == "DELAY":
            value = float(raw_value)
        else:
            value = int(raw_value)

        env_dic[keyword] = value

base_c = env_dic["BASE"][0]
base_r = env_dic["BASE"][1]

R = env_dic["GRID_HEIGHT"]
C = env_dic["GRID_WIDTH"]

WIDTH = env_dic["WINDOW_WIDTH"]
HEIGHT = env_dic["WINDOW_HEIGHT"]
CELLW = WIDTH/C
CELLH = HEIGHT/R

# counters
vics_quad=[0]*4  # victims per quadrant
walls_quad=[0]*4 # walls per quadrant
tot_vics=0       # total of victims
tot_walls=0      # total of walls


# Read clusters from all files in the cluster directory
cluster_files = [file for file in os.listdir(cluster_folder) if file.endswith(".txt")]

cluster_data = {}

for file_name in cluster_files:
    with open(os.path.join(cluster_folder, file_name), 'r') as f:
        cluster = []
        for line in f:
            elements = line.strip().split(',')
            converted_elements = []
            for i, element in enumerate(elements):
                if i == 3:  # Assuming the fourth column contains the severity (a float)
                    converted_elements.append(float(element))
                else:       # all other elements are integers
                    converted_elements.append(int(element))
            cluster.append(tuple(converted_elements))

        cluster_data[file_name] = cluster
        
# Create Pygame window
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Grid')

# Fill background with white
screen.fill(WHITE)

# Draw grid cells as unfilled black rectangles
for r in range(R):
    for c in range(C):
        pygame.draw.rect(screen, GRAY, (c * CELLW, r * CELLH, CELLW, CELLH), 1)

print(f"Stats printed by plot_2d_grid_py\n")
print(f"\n----------------------------------------")
print(f"Total of rows......: {R}")
print(f"Total of cols......: {C}")
print(f"Total of cells.....: {R*C}")
print(f"Base position......: ({base_c}, {base_r})")

# Read wall coordinates from file
with open(os.path.join(data_folder, walls_file), 'r') as f:
    wall_coords = [tuple(map(int, line.strip().split(','))) for line in f]

tot_walls = len(wall_coords)

# Read victims coordinates from file
with open(os.path.join(data_folder, victims_file), 'r') as f:
    vict_coords = [tuple(map(int, line.strip().split(','))) for line in f]

tot_vics = len(vict_coords)

# Plot the base position as a yellow rectangle
pygame.draw.rect(screen, YEL, (base_c * CELLW, base_r * CELLH, CELLW, CELLH))

# Plot walls as filled black rectangles
for c, r in wall_coords:
    pygame.draw.rect(screen, BLACK, (c * CELLW, r * CELLH, CELLW, CELLH))
    if r < R/2:
        if c < C/2:
            walls_quad[0] += 1
        else:
            walls_quad[1] += 1
    else:
        if c < C/2:
            walls_quad[2] += 1
        else:
            walls_quad[3] += 1

print(f"\n----------------------------------------")
# Plot clusters
for file_name, cluster in cluster_data.items():
    min_c = 100000
    min_r = 100000
    max_c = -1
    max_r = -1
    tot_vic = 0
    vics_sev=[0]*4  # victims per severity 
    
    cluster_color = generate_random_color()
    for i, c, r, g, l in cluster:
        tot_vic = tot_vic + 1
        c = c + base_c
        r = r + base_r

        if c < min_c:
            min_c = c
        if c > max_c:
             max_c = c

        if r < min_r:
            min_r = r
        if r > max_r:
            max_r = r

        vics_sev[l-1] = vics_sev[l-1]+1
        
        #pygame.draw.rect(screen, cluster_color, (c * CELLW, r * CELLH, CELLW, CELLH) )

    print(f"Cluster: {file_name} {tot_vic} victims, being...")
    print(f"   {vics_sev[0]} critical,")
    print(f"   {vics_sev[1]} instable,")
    print(f"   {vics_sev[2]} pot inst., and")
    print(f"   {vics_sev[3]} stable.")
    pygame.draw.rect(screen, cluster_color, (min_c * CELLW, min_r * CELLH, (max_c - min_c + 1) * CELLW, (max_r - min_r + 1) * CELLH), 5)
        
    # Draw lines between each victim in the cluster
    for i in range(len(cluster) - 1):
        c1 = cluster[i][1] + base_c
        r1 = cluster[i][2] + base_r
        c2 = cluster[i+1][1] + base_c
        r2 = cluster[i+1][2] + base_r
        #print(f"Cluster: {file_name} ({c1},{r1}) ({c2},{r2})")
        pygame.draw.line(screen, cluster_color, (c1 * CELLW + CELLW / 2, r1 * CELLH + CELLH / 2),
                         (c2 * CELLW + CELLW / 2, r2 * CELLH + CELLH / 2), 5)



print(f"\n----------------------------------------")
print(f"Total of walls.....: {tot_walls} ({100*tot_walls/(R*C):.1f}% of the env)")
print(f"  upper left  quad.: {walls_quad[0]} ({100*walls_quad[0]/tot_walls:.1f}%)")
print(f"  upper right quad.: {walls_quad[1]} ({100*walls_quad[1]/tot_walls:.1f}%)")
print(f"  lower left  quad.: {walls_quad[2]} ({100*walls_quad[2]/tot_walls:.1f}%)")
print(f"  lower right quad.: {walls_quad[3]} ({100*walls_quad[3]/tot_walls:.1f}%)")



# Plot victims as red circles
for c, r in vict_coords:
    pygame.draw.circle(screen, (255, 0, 0), (c * CELLW + CELLW / 2, r * CELLH + CELLH / 2), 0.4*min(CELLW,CELLH))
    if r < R/2:
        if c < C/2:
            vics_quad[0] += 1
        else:
            vics_quad[1] += 1
    else:
        if c < C/2:
            vics_quad[2] += 1
        else:
            vics_quad[3] += 1

print(f"\n------------------------------------------") 
print(f"Total of victims...: {tot_vics}")
print(f"  upper left  quad.: {vics_quad[0]} ({100*vics_quad[0]/tot_vics:.1f}%)")
print(f"  upper right quad.: {vics_quad[1]} ({100*vics_quad[1]/tot_vics:.1f}%)")
print(f"  lower left  quad.: {vics_quad[2]} ({100*vics_quad[2]/tot_vics:.1f}%)")
print(f"  lower right quad.: {vics_quad[3]} ({100*vics_quad[3]/tot_vics:.1f}%)")

# Update Pygame display
pygame.display.update()

# Wait for user to close window
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:   ## left click
            # Get current mouse position
            x, y = event.pos
            # Convert mouse position to row and column indices
            r = int(y / CELLH)
            c = int(x / CELLW)
            # Draw row and column coordinates on screen
            font = pygame.font.SysFont('Arial', int(0.3*min(CELLW,CELLH)))
            text = font.render(f'({c},{r})', True, RED)
            text_rect = text.get_rect(center=(x, y))
            print(f'({c},{r})')
            screen.blit(text, text_rect)
            # Update Pygame display
            pygame.display.update()
