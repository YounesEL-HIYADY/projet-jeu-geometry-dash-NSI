import pygame
from level import Level

pygame.init()
WIDTH, HEIGHT = 1000, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Geometry Dash Clone")
clock = pygame.time.Clock()

level = Level("levels/level1.json")

running = True
while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Contrôles
    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE]:
        level.player.jump()

    # Logique
    level.update()

    # Rendu
    screen.fill((30, 30, 30))
    level.draw(screen)
    pygame.display.flip()

pygame.quit()
