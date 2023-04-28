## Le o arquivo de paredes e de vitimas e permite completar com clicks
## - botao esquerda: acrescenta uma parede ou apaga (se já existir)
## - botao direita: acrescenta uma vítima (se não houver) e apaga se já existir.

import pygame

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# File names (to be Configured)
walls_file = "../data_teste1/env_walls.txt"
victims_file = "../data_teste1/env_victims.txt"


# Set grid size (to be Configured)
R = 20
C = 20
WIDTH = 600
HEIGHT = 600
CELLW = WIDTH/R
CELLH = HEIGHT/C

def write_walls(walls):
    # Remove any duplicate points
    walls = list(set(walls))

    # Sort the wall coordinates by row number and then by column number
    walls = sorted(walls, key=lambda x: (x[0], x[1]))

    # Remove any blank lines from the output file
    walls = [w for w in walls if w]

    with open(walls_file, "w") as f:
        for w in walls:
            f.write(f"{w[0]},{w[1]}\n")
            
def write_victims(victims):
    # Remove any duplicate points
    victims = list(set(victims))

    # Sort the wall coordinates by row number and then by column number
    victims = sorted(victims, key=lambda x: (x[0], x[1]))

    # Remove any blank lines from the output file
    victims = [v for v in victims if v]

    with open(victims_file, "w") as f:
        for v in victims:
            f.write(f"{v[0]},{v[1]}\n")
    
    v_size = len(victims)
    print(f"Total of victims {v_size}")

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

# Read walls coordinates from file
with open(walls_file, 'r') as f:
    wall_coords = [tuple(map(int, line.strip().split(','))) for line in f]

# Read victims coordinates from file
with open(victims_file, 'r') as f:
    victims = [tuple(map(int, line.strip().split(','))) for line in f]

print(f"Total of read victims: {len(victims)}")

# Plot walls as filled black rectangles
for c, r in wall_coords:
    pygame.draw.rect(screen, BLACK, (c * CELLW, r * CELLH, CELLW, CELLH))

# Plot victims as red circles
for c, r in victims:
    pygame.draw.circle(screen, (255, 0, 0), (c * CELLW + CELLW / 2, r * CELLH + CELLH / 2), 0.4*min(CELLW,CELLH))
    if ((c,r) in wall_coords):
        print(f"Error - victim is on the wall ({c},{r})")
    if c >= C or r >= R:
        print(f"Error - victim OUT OF THE grid ({c},{r})")

# Update Pygame display
pygame.display.update()

# Wait for user to close window
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            write_walls(wall_coords)
            write_victims(victims)
            pygame.quit()
            quit()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: # Wall adding or removal
            # Get current mouse position
            x, y = event.pos
            # Convert mouse position to row and column indices
            r = int(y / CELLH)
            c = int(x / CELLW)
            # Draw row and column coordinates on screen
            font = pygame.font.SysFont('Arial', max(int(0.4*min(CELLW,CELLH)),1))
            text = font.render(f'({c},{r})', True, WHITE)
            text_rect = text.get_rect(center=(int(c * CELLW + CELLW / 2), int(r * CELLH + CELLH / 2)))
            if not ((c,r) in wall_coords):
                if not((c,r) in victims):
                    wall_coords.append((c,r))
                    pygame.draw.rect(screen, BLACK, (c * CELLW, r * CELLH, CELLW, CELLH))
            else:
                wall_coords.remove((c,r))
                pygame.draw.rect(screen, WHITE,(c * CELLW, r * CELLH, CELLW-1, CELLH-1), 0)
            screen.blit(text, text_rect)

            # Update Pygame display
            #print(wall_coords)
            pygame.display.update()

           
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:   # Victim adding or removal
            # Get current mouse position
            x, y = event.pos
            # Convert mouse position to row and column indices
            r = int(y / CELLH)
            c = int(x / CELLW)
            print(f'Trying to add or remove victim ({c},{r})')
            if  not ((c,r) in victims):
                if not ((c,r) in wall_coords):
                    victims.append((c,r))
                    pygame.draw.circle(screen, RED, (c * CELLW + CELLW / 2, r * CELLH + CELLH / 2), 0.4*min(CELLW,CELLH))
            else:
                victims.remove((c,r))
                pygame.draw.circle(screen, WHITE, (c * CELLW + CELLW / 2, r * CELLH + CELLH / 2), 0.4*min(CELLW,CELLH))

            #print(f'Remove({c},{r})')
            print(f"Total of victims: {len(victims)}")
            pygame.display.update()



     
            
