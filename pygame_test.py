import pygame
import math

#initializes pygame and sets screen resolution
pygame.init()
screen = pygame.display.set_mode((800,800))
clock = pygame.time.Clock()

#define MIDI_EVENT
MIDI_EVENT = pygame.USEREVENT + 1
#function to post a MIDI_EVENT with a pitch attribute
def post_midi_event(pitch):
    event = pygame.event.Event(MIDI_EVENT, {"pitch": pitch})
    pygame.event.post(event)

#main pygame loop
running = True
while running:
    
    #cycles thru the pygame event queue with conditions
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            print("A key was pressed")

    #sets background color
    screen.fill((0,0,0))

    #sets up the default display
    for note in range(12):
        angle = math.radians(note * 360 / 12)
        distance = 200  # Example octave
        x = int(400 + distance * math.cos(angle))
        y = int(400 - distance * math.sin(angle))
        pygame.draw.circle(screen, (255, 255, 255), (x, y), 5)

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
