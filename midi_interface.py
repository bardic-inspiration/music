import time
import rtmidi
import pygame
import math
import keyboard

dEBUGMODE = True

#PYGAME EVENTS
MIDI_EVENT = pygame.USEREVENT + 1

#PYGAME FUNCTIONS:
def post_midi_event(pitch, vel): #posts a MIDI_EVENT with pitch and velocity
    event = pygame.event.Event(MIDI_EVENT, {"pitch": pitch, "vel": vel})
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

    def DrawNote(self, midiobject):      
        
        intput = int(midiobject[0])
        if dEBUGMODE: print(str(midiobject[0]))
        note = intput % 12
        octave = int((intput - (intput % 12))/12)
        color = (255,0,0)

        angle = math.radians(90 - note * 30)
        distance = octave * 50
        x = int(self.origin[0] + distance * math.cos(angle))
        y = int(self.origin[1] - distance * math.sin(angle))
        pygame.draw.circle(screen, color, (x, y), 5)

        #else: print("Error: Expected MidiObject")

    def AddMidi(self, pitch, vel=100):
        timeout = vel * 128 / self.speed
        midi = (pitch, timeout)
        self.activemidi.append(midi) 

    def Refresh(self): #refreshes the midi clock's queue of midi objects
        for midiobject in self.activemidi:
            if midiobject.Decay() == 0: #purges dead midi objects
                self.activemidi.remove(midiobject)
            else: self.DrawNote(midiobject) #draws the midi object

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

#main pygame loop
running = True
reset = True

while running:
    
    #keyboard commands
    if keyboard.is_pressed("esc"): break
    if keyboard.is_pressed("space"): reset = True
    if reset: 
        midiclock.ResetDisplay()
        #midiclock.ClearQueue()  #clears the queue
        reset = False

    #sets up the default display
    #midiclock.DefaultDisplay()

    midiclock.Listen() #listens for inputs
    midiclock.Refresh() #refreshes the display

    #cycles thru the pygame event queue with conditions
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == MIDI_EVENT:
            #try: 
            midiclock.AddMidi(event.pitch, event.vel)
            #except: print("Oops!")

    pygame.display.flip()
    clock.tick(interval)

print("Thank you for trying reifzmidi")
pygame.quit()