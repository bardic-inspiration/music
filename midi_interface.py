import time
import rtmidi
import pygame
import math
import keyboard

dEBUGMODE = False


#PYGAME DEFINITIONS:

#define MIDI_EVENT
MIDI_EVENT = pygame.USEREVENT + 1

def post_midi_event(pitch): #posts a MIDI_EVENT with a pitch attribute
    event = pygame.event.Event(MIDI_EVENT, {"pitch": pitch})
    pygame.event.post(event)

def draw_note(pitch):      
    
    try: #checks for int
        intput = int(pitch)
    except:
        if dEBUGMODE: print("Input must be an integer.")
        return (0, 0)
    
    note = intput % 12
    octave = int((intput - (intput % 12))/12)
    color = (255,0,0)

    angle = math.radians(note * 30)
    distance = octave * 50
    x = int(400 + distance * math.cos(angle))
    y = int(400 - distance * math.sin(angle))
    pygame.draw.circle(screen, color, (x, y), 5)

#GENERAL UTILITY FUNCTIONS:
def get_note_str(input): #takes an integer MIDI pitch and returns a string in standard musical notation.
    notelist = ["C","C#/Db","D","D#/Eb","E","F","F#/Gb","G","G#/Ab","A","A#/Bb","B"]
    
    try: #checks for int
        intput = int(input)
    except:
        if dEBUGMODE: print("Input must be an integer.")
        return
    
    pitch = notelist[intput % 12]
    octave = int((intput - (intput % 12))/12)
    note = f"{pitch}{str(octave)}"

    return note

def get_note(input): #takes int MIDI pitch and returns the note and octave as a 2-tuple of integers
        
    try: #checks for int
        intput = int(input)
    except:
        if dEBUGMODE: print("Input must be an integer.")
        return (0, 0)
    
    note = intput % 12
    octave = int((intput - (intput % 12))/12)

    return (note, octave)

class MidiClock: #a class for the app

    def __init__(self):
        self.midi_in = rtmidi.MidiIn() #creates a midi input class
        self.OpenPorts()

    def OpenPorts(self):
        self.midi_in.open_port(0) #opens port 0 for midi input (assumes 0 is available)
        print(self.midi_in.get_ports()) #prints the port info - for testing

    def DefaultDisplay(self): #initializes the default empty display
        screen.fill((0,0,0))
        
        for note in range(12):
                angle = math.radians(note * 30)
                distance = 200  # Example octave
                x = int(400 + distance * math.cos(angle))
                y = int(400 - distance * math.sin(angle))
                pygame.draw.circle(screen, (255, 255, 255), (x, y), 5)

    def Listen(self):
        #gets input from midi_in.  returns null or a 2-tuple (int[] midi message, float delta time)
        msg = self.midi_in.get_message()
    
        #if there is an input, prints the details
        if msg:
            (ms, dt) = msg #the midi message
            command = hex(ms[0]) #hexes first item, the midi command
            pitch = int(ms[1]) #ms[1] is the pitch.  ms[2] is velocity.

            if command[2] == '9': #filters for note-on
                if dEBUGMODE: print(f"{command} {ms[1:]}\t| dt = {dt:.2f}")
                print(get_note_str(pitch)) 
                post_midi_event(pitch)

#/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
#THE MAIN PART OF THE APPLICATION BELOW:|
#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/

#initializes pygame and sets screen resolution
midiclock = MidiClock()
pygame.init()
screen = pygame.display.set_mode((800,800))
clock = pygame.time.Clock()

#main pygame loop
running = True
while running:
    if keyboard.is_pressed("esc"): break

    #cycles thru the pygame event queue with conditions
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == MIDI_EVENT:
            print(get_note_str(event.pitch))

    #sets up the default display
    midiclock.DefaultDisplay()

    #listens for inputs
    midiclock.Listen()

    pygame.display.flip()
    clock.tick(30)

print("Thank you for trying reifzmidi")
pygame.quit()

#ports = out.get_ports()   

#[print(x) for x in ports]

"""# List all available MIDI input ports
input_ports = mido.get_input_names()
print("Available MIDI input ports:")
for i, port in enumerate(input_ports):
    print(f"{i}: {port}")"""