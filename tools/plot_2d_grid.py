## Read the walls file with coordinates of walls and the victims file containing
## the victims' coordinates and plots the 2D grid.
## The 2D grid's origin is at the top left corner. Indexations is (column, row).
## It prints the metrics per quadrant (victims and walls per quadrant)
##    upper left | upper right
##    ------------------------
##    lower left | lower right

import pygame

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YEL = (255, 255, 0)

walls_file = "env_walls.txt"
victims_file = "env_victims.txt"

# Set grid size
R = 80
C = 100
WIDTH = 960
HEIGHT = 700
CELLW = WIDTH/C
CELLH = HEIGHT/R

# the base position (to not coincide with walls and victims)
base_r = 50
base_c = 50

# counters
vics_quad=[0]*4  # victims per quadrant
walls_quad=[0]*4 # walls per quadrant
tot_vics=0       # total of victims
tot_walls=0      # total of walls

# Create Pygame window
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Grid')

# Fill background with white
screen.fill(WHITE)

# Draw grid cells as unfilled black rectangles
for r in range(R):
    for c in range(C):
        pygame.draw.rect(screen, BLACK, (c * CELLW, r * CELLH, CELLW, CELLH), 1)

print(f"Stats printed by plot_2d_grid_py\n")
print(f"\n----------------------------------------")
print(f"Total of rows......: {R}")
print(f"Total of cols......: {C}")
print(f"Total of cells.....: {R*C}")
print(f"Base position......: ({base_c}, {base_r})")

# Read wall coordinates from file
with open(walls_file, 'r') as f:
    wall_coords = [tuple(map(int, line.strip().split(','))) for line in f]

tot_walls = len(wall_coords)

# Read victims coordinates from file
with open(victims_file, 'r') as f:
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
