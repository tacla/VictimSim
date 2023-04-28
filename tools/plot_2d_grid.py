## Read the walls file with coordinates of walls and the victims file containing
## the victims' coordinates and plots the 2D grid.
## The 2D grid's origin is at the top left corner. Indexations is (column, row).

import pygame

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

walls_file = "walls.txt"
victims_file = "victims.txt"

# Set grid size
R = 20
C = 20
WIDTH = 800
HEIGHT = 800
CELLW = WIDTH/R
CELLH = HEIGHT/C

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

# Read wall coordinates from file
with open(walls_file, 'r') as f:
    wall_coords = [tuple(map(int, line.strip().split(','))) for line in f]

# Read victims coordinates from file
with open(victims_file, 'r') as f:
    vict_coords = [tuple(map(int, line.strip().split(','))) for line in f]

# Plot walls as filled black rectangles
for c, r in wall_coords:
    pygame.draw.rect(screen, BLACK, (c * CELLW, r * CELLH, CELLW, CELLH))

# Plot victims as red circles
for c, r in vict_coords:
    pygame.draw.circle(screen, (255, 0, 0), (c * CELLW + CELLW / 2, r * CELLH + CELLH / 2), 0.4*min(CELLW,CELLH))

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
