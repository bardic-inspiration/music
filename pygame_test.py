import pygame
import math

pygame.init()
screen = pygame.display.set_mode((800,800))
clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0,0,0))

    for note in range(12):
        angle = math.radians(note * 360 / 12)
        distance = 200  # Example octave
        x = int(400 + distance * math.cos(angle))
        y = int(400 - distance * math.sin(angle))
        pygame.draw.circle(screen, (255, 255, 255), (x, y), 5)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
