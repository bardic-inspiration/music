import time
import rtmidi
import keyboard

dEBUGMODE = False

#Testing

class MidiObject: #a class for processing midi inputs

    def __init__(self):
        pass

    def GetNote(self, input): #takes an integer and returns a string
        notelist = ["C","C#/Db","D","D#/Eb","E","F","F#/Gb","G","G#/Ab","A","A#/Bb","B"]
        
        try:
            intput = int(input)
        except:
            if dEBUGMODE: print("Input must be an integer.")
            return
        
        pitch = notelist[intput % 12]
        octave = int((intput - (intput % 12))/12)
        note = f"{pitch}{str(octave)}"

        return note

class MidiClock: #a class for the app

    def __init__(self):
        self.midi_in = rtmidi.MidiIn() #creates a midi input class
        self.testmobject = MidiObject()
        self.OpenPorts()

    def OpenPorts(self):
        self.midi_in.open_port(0) #opens port 0 for midi input (assumes 0 is available)
        print(self.midi_in.get_ports()) #prints the port info - for testing

    def Listen(self):
        while True:
            #gets input from midi_in.  returns null or a 2-tuple (int[] midi message, float delta time)
            msg = self.midi_in.get_message()
        
            #if esc is pressed, returns
            if keyboard.is_pressed("esc"):
                print("Thank you for trying reifzmidi")
                break
        
            #if there is an input, prints the deets
            elif msg:
                (ms, dt) = msg #the midi message
                command = hex(ms[0]) #hexes first item, the midi command
                if command[2] == '9': #filters for note-on
                    if dEBUGMODE: print(f"{command} {ms[1:]}\t| dt = {dt:.2f}")
                    print(self.testmobject.GetNote(int(ms[1]))) #ms[1] is the pitch.  ms[2] is velocity.  idk what ms[0] is lol
                elif dEBUGMODE:
                    print(f"debugmode {command[2]}")
        
            #if there is no input, waits for more
            else:
                time.sleep(0.01)
    
midiclock = MidiClock()
midiclock.Listen()

#ports = out.get_ports()   

#[print(x) for x in ports]

"""# List all available MIDI input ports
input_ports = mido.get_input_names()
print("Available MIDI input ports:")
for i, port in enumerate(input_ports):
    print(f"{i}: {port}")"""