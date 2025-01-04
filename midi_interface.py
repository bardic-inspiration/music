import time
import rtmidi
import pygame
import math
import keyboard
import array as arr

dEBUGMODE = False

#PYGAME EVENTS
MIDI_PRESS = pygame.USEREVENT + 1
MIDI_RELEASE = pygame.USEREVENT + 2

#PYGAME FUNCTIONS:
def post_midi_event(pitch=0, vel=100): #posts a MIDI_PRESS with pitch and velocity
    event = pygame.event.Event(MIDI_PRESS, {"pitch": pitch, "vel": vel})
    pygame.event.post(event)

#UTILITIES:
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

def text_input(): #takes a string and feeds it to the app as MIDI for testing
    userinput = input("Input an integer.")
    try:
        i = int(userinput) 
        print(f"Integer received: {i}")
        post_midi_event(i, 100)
    except:
        print("Error: Expected integer.")
        return 0

#OBJECTS:
class MidiClock: #a class for each clock

    def __init__(self):
        
        #configurations
        self.resolution = (800,800)
        self.interval = 30 #tick time in ms
        self.speed = 1000 #max lifespan for display objects in ms
        
        
        #structural variables
        self.midi_in = rtmidi.MidiIn() #creates a midi input class
        self.origin = (self.resolution[0] / 2, self.resolution[1] / 2)
        self.activemidi = []

        #initialization calls
        self.OpenPorts()

    def OpenPorts(self):
        self.midi_in.open_port(0) #opens port 0 for midi input (assumes 0 is available)
        print(self.midi_in.get_ports()) #prints the port info - for testing

    def ResetDisplay(self): #initializes the default empty display
        screen.fill((0,0,0))
        
        for note in range(12):
                angle = math.radians(note * 30)
                distance = 200  # Example octave
                x = int(self.origin[0] + distance * math.cos(angle))
                y = int(self.origin[1] - distance * math.sin(angle))
                pygame.draw.circle(screen, (255, 255, 255), (x, y), 5)

    def Listen(self):
        #gets input from midi_in.  returns null or a 2-tuple (int[] midi message, float delta time)
        msg = self.midi_in.get_message()
    
        #if there is an input, prints the details
        if msg:
            (ms, dt) = msg #the midi message
            command = hex(ms[0]) #hexes first item, the midi command, for interpretation
            pitch = int(ms[1]) #ms[1] is pitch of midi signal 
            vel = int(ms[2]) #ms[2] is velocity of midi signal

            if command[2] == '9': #interprets the midi command, filters for note-on
                if dEBUGMODE: print(f"{command} {ms[1:]}\t| dt = {dt:.2f}")
                print(get_note_str(pitch))
                post_midi_event(pitch, vel) #pygame posts a midi event

    def Draw(self, midi):      
        
        pitch = midi[0]
        if dEBUGMODE: print(str(pitch))
        note = pitch % 12
        octave = int((pitch - (pitch % 12))/12)
        color = (255,0,0)

        angle = math.radians(90 - note * 30)
        distance = min(self.resolution) / 2 - octave * 50  #the distance is half the smaller of the two window dimensions
        x = int(self.origin[0] + distance * math.cos(angle))
        y = int(self.origin[1] - distance * math.sin(angle))
        pygame.draw.circle(screen, color, (x, y), 5)

        #else: print("Error: Expected MidiObject")

    def AddMidi(self, pitch, vel=100):
        timeout = vel / 128 * self.speed
        midi = [pitch, timeout]
        self.activemidi.append(midi) 

    def Refresh(self): #purges the queue, resets the display, redraws all objects 
        for i in range(len(self.activemidi) -1, -1, -1):
            self.activemidi[i][1] -= interval
            if self.activemidi[i][1] <= 0: #checks if midi timeout has reached 0
                self.activemidi.pop(i) #removes expired midi
            else:
                if dEBUGMODE: print(str(self.activemidi[i]))
                self.Draw(self.activemidi[i]) #draws the midi on the screen
                

"""class MidiObject:
    def __init__(self, pitch, vel):
        self.pitch = pitch
        self.timeout = vel * 128 / midiclock.speed

    def Decay(self):
        if self.timeout >= 0:
            self.timeout -= midiclock.interval
            return self.timeout
        return 0

    def Pitch(self):
        return self.pitch"""

#/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
#THE MAIN PART OF THE APPLICATION BELOW:|
#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/

#initializes pygame and sets screen resolution
midiclock = MidiClock()
pygame.init()
screen = pygame.display.set_mode((800,800))
clock = pygame.time.Clock()
interval = 30

#switches
running = True
reset = True

#primary loop
while running:
    
    midiclock.Listen() #listens for inputs

    # Process all Pygame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # Quit event
            running = False

        # Handle keypress events
        elif event.type == pygame.KEYDOWN:  # Key is pressed down
            if event.key == pygame.K_ESCAPE:  # Escape key
                running = False
            elif event.key == pygame.K_q:  # Q key
                text_input()

        # Handle custom MIDI events
        elif event.type == MIDI_PRESS:
            try:
                midiclock.AddMidi(event.pitch, event.vel)
            except Exception as e:
                print(f"Error handling MIDI_PRESS: {e}")

    midiclock.ResetDisplay() #resets the display
    midiclock.Refresh() #refreshes the display

    pygame.display.flip()
    clock.tick(interval)

print("Thank you for trying reifzmidi")
pygame.quit()