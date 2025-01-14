import rtmidi
import pygame
import math
from colorutils import Color
from itertools import combinations

dEBUGMODE = False

#PYGAME EVENTS
MIDI_PRESS = pygame.USEREVENT + 1
MIDI_RELEASE = pygame.USEREVENT + 2

#PYGAME FUNCTIONS:
def post_midi_press(pitch=0, vel=100): #posts a MIDI_PRESS with pitch and velocity
    event = pygame.event.Event(MIDI_PRESS, {"pitch": pitch, "vel": vel})
    pygame.event.post(event)
def post_midi_release(pitch=0): #post a MIDI_RELEASE with pitch
    event = pygame.event.Event(MIDI_RELEASE, {"pitch": pitch})
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
    userinput = input("Input a command string: -midi -color")
    
    if userinput == "-midi":
        m = input("Input an integer pitch.") 
        try:
            i = int(userinput) 
            print(f"Integer received: {i}")
            post_midi_press(i, 100)
        except:
            print("Error: Expected integer.")
            return
    elif userinput == "-colormode":
        c = input("Input an integer to change the color mode. 0 Default 1 Dynamic 2 Custom")
        try: 
            color = Color(c)
            #midiclock.colormode = 
        except: 
            print("Error: Invalid color format.")
            return
        

    

#OBJECTS:
class MidiClock:

    def __init__(self):
        
        #configurable vars
        self.name = "Default Clock"
        self.resolution = (800,800)
        self.interval = 30 #tick time in ms
        self.speed = 1000 #max lifespan for display objects in ms
        
        #structural vars
        self.midi_in = rtmidi.MidiIn() #creates a midi input class
        self.origin = (self.resolution[0] / 2, self.resolution[1] / 2)
        self.activemidi = []

        #initialization calls
        self.OpenPorts()

#config methods
    def SetSpeed(self, speed):
        try: 
            int(speed)
            self.speed = speed
            print(f"{self.name} speed set to {speed}")
        except:
            print("Error: Expected integer.")
    def SetResolution(self, x, y):
        try:
            int(x)
            int(y)
            self.resolution = (x,y)
        except:
            print("Error: Expected integer.")


#midi in methods
    def OpenPorts(self):
        self.midi_in.open_port(0) #opens port 0 for midi input (assumes 0 is available)
        print(self.midi_in.get_ports()) #prints the port info - for testing
    def Listen(self):
    
        #gets input from midi_in.  returns null or a 2-tuple (int[] midi message, float delta time)
        msg = self.midi_in.get_message()
    
        #if there is an input, prints the details
        if msg:
            (ms, dt) = msg #the midi message
            command = hex(ms[0]) #hexes first item, the midi command, for interpretation
            pitch = int(ms[1]) #ms[1] is pitch of midi signal 
            vel = int(ms[2]) #ms[2] is velocity of midi signal

            if command[2] == '9': #note-on
                if dEBUGMODE: print(f"{command} {ms[1:]}\t| dt = {dt:.2f}")
                print(get_note_str(pitch))
                post_midi_press(pitch, vel) #pygame posts a midi event
            elif command[2] == '8': #note-off
                post_midi_release(pitch)

#display methods
    def ResetDisplay(self): #initializes the default empty display
        screen.fill((0,0,0))
        
        for note in range(12):
                angle = math.radians(note * 30)
                distance = min(self.resolution) / 4  # Example octave
                x = int(self.origin[0] + distance * math.cos(angle))
                y = int(self.origin[1] - distance * math.sin(angle))
                pygame.draw.circle(screen, (255, 255, 255), (x, y), 5)
    def Draw(self, midi):   
        
        pitch = midi.pitch
        scale = midi.timeout / self.speed
        ispressed = midi.ispressed

        #parameters
        size = midi.size * int(min(self.resolution)) * scale

        if dEBUGMODE: print(str(pitch))
        note = pitch % 12
        octave = int((pitch - (pitch % 12))/12)

        if ispressed: color = (255,255,255)
        else: color = (0,0,255)

        angle = math.radians(90 - note * 30)
        distance = min(self.resolution) / 2 - octave * 50  #the distance is half the smaller of the two window dimensions
        x = int(self.origin[0] + distance * math.cos(angle))
        y = int(self.origin[1] - distance * math.sin(angle))
        pygame.draw.circle(screen, color, (x, y), size)

        #else: print("Error: Expected MidiObject")
    def DrawChord(self, midi, mode): #draws a polygon given multiple midi note inputs
        a = 0
        try: 
            a = len(midi)
            if a <= 1:
                print("Error: List too short.")
        except:
            print("Error: Expected list.")
        
        #for i in range(len(midiobjects)):
        #    coords.append(midiobjects[i].GetCoords())    ##NEED TO BUILD GETCOORDS()
        
#midi queue methods
    def Refresh(self): #reduces the timeout of all midi in the queue and purges midi whose timeout is 0
        for i in range(len(self.activemidi)-1, -1, -1): #iterates in reverse to avoid index issues with pop
            if not self.activemidi[i].ispressed: self.activemidi[i].timeout -= interval #reduces timeout of all released midi by 1
            if self.activemidi[i].timeout <= 0: self.activemidi.pop(i) #removes expired midi
    """def AddMidi(self, pitch, vel=100):  #OLD ADD MIDI FUNCTION FOR REFERENCE
        timeout = vel / 128 * self.speed
        midi = [pitch, timeout, True]
        self.activemidi.append(midi) """
    def ReleaseMidi(self, pitch):
        for i in range(len(self.activemidi)): #iterates thru queue and marks first midi component of matching pitch as eligible for timing out. the Refresh() method is called, it will count down and be removed from the queue when midi.timeout = 0.
            if self.activemidi[i].ispressed and self.activemidi[i][0] == pitch:
                self.activemidi[i].ispressed = False
                break
    def AnalyzeQueue(self): #analyzes the notes in the queue and returns any defined pattern matches

        #creates a set out of the midi queue with normalized pitches, deduplicated
        normalized_pitches = {note.pitch % 12 for note in self.activemidi}

        #creates a list of tuples of 2 note combinations
        pitch_pairs = combinations(normalized_pitches, 2)

        intervals = [] #a list of intervals in the queue
        for a, b in pitch_pairs:
            interval = (b - a) % 12 #the difference in pitch of the pair of notes
            intervals.append(interval) #adds the interval to the list
            interval_reverse = (a - b) % 12 #includes the reverse direction for analysis
            intervals.append(interval_reverse)

        #default patterns for major and minor chords... do we want to store all chord patterns in a list?
        major_chord = [4, 3]
        minor_chord = [3, 4]

        #sorts the list of intervals in ascending order
        intervals.sort()

        #checks the list of intervals for major and minor chords  (what if there are both?)
        if major_chord == intervals[:len(major_chord)]:
            return "Major"
        elif minor_chord == intervals[:len(major_chord)]:
            return "Minor"
        return "None"







class Midi:
    
    def __init__(self, pitch=0, vel=100, size=1):
        self.pitch = pitch
        self.vel = vel
        self.size = size
        self.ispressed = True
        self.timeout = vel * 128 / midiclock.speed

    def Decay(self):
        if self.timeout >= 0:
            self.timeout -= midiclock.interval
            return self.timeout
        return 0

    """def Draw(self, offset=(0,0)):
        #parameters
        pitch = self.pitch
        scale = self.timeout / self.speed

        size = self.size * int(min(self.resolution)) * scale

        if dEBUGMODE: print(str(pitch))
        note = pitch % 12
        octave = int((pitch - (pitch % 12))/12)

        if self.ispressed: color = (255,255,255)
        else: color = (0,0,255)

        angle = math.radians(90 - note * 30)
        distance = min(self.resolution) / 2 - octave * 50  #the distance is half the smaller of the two window dimensions
        x = int(self.origin[0] + distance * math.cos(angle)) + offset[1]
        y = int(self.origin[1] - distance * math.sin(angle)) + offset[2]
        pygame.draw.circle(screen, color, (x, y), size)"""


#/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
#THE MAIN LOOP OF THE APPLICATION BELOW:|
#\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/

#initializes pygame and sets screen resolution
midiclock = MidiClock()
pygame.init()
screen = pygame.display.set_mode(midiclock.resolution)
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

        # Handle MIDI events
        elif event.type == MIDI_PRESS: #when a MIDI key is pressed, adds a note to the queue
            try:
                midiclock.activemidi.append(Midi(event.pitch, event.vel))
            except Exception as e:
                print(f"Error handling MIDI_PRESS: {e}")
        elif event.type == MIDI_RELEASE: #when a MIDI key is released, the note starts to time out
            try:
                midiclock.ReleaseMidi(event.pitch) #finds the first note of matching pitch in the queue and marks it for timeout
            except Exception as e:
                print(f"Error handling MIDI_RELEASE: {e}")

    midiclock.ResetDisplay() #resets the display
    midiclock.Refresh() #refreshes the MIDI queue
    midiclock.AnalyzeQueue() #analyzes the MIDI queue for chord patterns

    for note in midiclock.activemidi: midiclock.Draw(note)

    pygame.display.flip()
    clock.tick(interval)

print("Thank you for trying MIDI DROPS")
pygame.quit()