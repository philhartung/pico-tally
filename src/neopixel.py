import array
import time
import rp2
import math
from machine import Pin
from machine import ADC

NUM_LEDS = 160
PIN_NUM = 6

@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
def ws2812():
    T1 = 2
    T2 = 5
    T3 = 3
    wrap_target()
    label("bitloop")
    out(x, 1)               .side(0)    [T3 - 1]
    jmp(not_x, "do_zero")   .side(1)    [T1 - 1]
    jmp("bitloop")          .side(1)    [T2 - 1]
    label("do_zero")
    nop()                   .side(0)    [T2 - 1]
    wrap()

class NeoPixel(object):
    def __init__(self,pin=PIN_NUM,num=NUM_LEDS,brightness=0.2):
        self.pin=pin
        self.num=num
        self.brightness = brightness
        
        # Create the StateMachine with the ws2812 program, outputting on pin
        self.sm = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=Pin(PIN_NUM))

        # Start the StateMachine, it will wait for data on its FIFO.
        self.sm.active(1)

        # Display a pattern on the LEDs via an array of LED RGB values.
        self.ar = array.array("I", [0 for _ in range(self.num)])
        
    def pixels_show(self):
        dimmer_ar = array.array("I", [0 for _ in range(self.num)])
        for i,c in enumerate(self.ar):
            r = int(((c >> 8) & 0xFF) * self.brightness)
            g = int(((c >> 16) & 0xFF) * self.brightness)
            b = int((c & 0xFF) * self.brightness)
            dimmer_ar[i] = (g<<16) + (r<<8) + b
        self.sm.put(dimmer_ar, 8)

    def pixels_set(self, i, color):
        self.ar[i] = (color[0]<<16) + (color[1]<<8) + color[2]

    def pixels_fill(self, color, brightness):
        for i in range(len(self.ar)):
            self.pixels_set(i, color)
        self.brightness = brightness

    def display5x3(self, array, posX, posY, color, colorBG):
        if len(array) != 15:
            print('Invalid array lenght')
        else:
            for pos in range(15):
                pixel = (posY + math.floor(pos / 3)) * 16 + posX + (pos % 3)
                if array[pos] == 1:
                    self.pixels_set(pixel, color)
                else:
                    self.pixels_set(pixel, colorBG)
    
    def displayChar(self, char, posX, posY, color, colorBG):
        # check pos
        if posX > 13 or posX < 0:
            print('invalid position')
        elif posY > 5 or posY < 0:
            print('invalid position')
        else:
            # if else for chars
            char = char.upper()
            
            # Numbers
            if char == '0':
                self.display5x3([1,1,1,
                                 1,0,1,
                                 1,0,1,
                                 1,0,1,
                                 1,1,1], posX, posY, color, colorBG)
            elif char == '1':
                self.display5x3([0,0,1,
                                 0,0,1,
                                 0,0,1,
                                 0,0,1,
                                 0,0,1], posX, posY, color, colorBG)
            elif char == '2':
                self.display5x3([1,1,1,
                                 0,0,1,
                                 1,1,1,
                                 1,0,0,
                                 1,1,1], posX, posY, color, colorBG)
            elif char == '3':
                self.display5x3([1,1,1,
                                 0,0,1,
                                 1,1,1,
                                 0,0,1,
                                 1,1,1], posX, posY, color, colorBG)
            elif char == '4':
                self.display5x3([1,0,1,
                                 1,0,1,
                                 1,1,1,
                                 0,0,1,
                                 0,0,1], posX, posY, color, colorBG)
            elif char == '5':
                self.display5x3([1,1,1,
                                 1,0,0,
                                 1,1,1,
                                 0,0,1,
                                 1,1,1], posX, posY, color, colorBG)
            elif char == '6':
                self.display5x3([1,1,1,
                                 1,0,0,
                                 1,1,1,
                                 1,0,1,
                                 1,1,1], posX, posY, color, colorBG)
            elif char == '7':
                self.display5x3([1,1,1,
                                 0,0,1,
                                 0,0,1,
                                 0,0,1,
                                 0,0,1], posX, posY, color, colorBG)
            elif char == '8':
                self.display5x3([1,1,1,
                                 1,0,1,
                                 1,1,1,
                                 1,0,1,
                                 1,1,1], posX, posY, color, colorBG)
            elif char == '9':
                self.display5x3([1,1,1,
                                 1,0,1,
                                 1,1,1,
                                 0,0,1,
                                 1,1,1], posX, posY, color, colorBG)
                
            # Special
            elif char == '.':
                self.display5x3([0,0,0,
                                 0,0,0,
                                 0,0,0,
                                 0,0,0,
                                 0,1,0], posX, posY, color, colorBG)
            elif char == ' ':
                self.display5x3([0,0,0,
                                 0,0,0,
                                 0,0,0,
                                 0,0,0,
                                 0,0,0], posX, posY, color, colorBG)
            elif char == '?':
                self.display5x3([1,1,1,
                                 0,0,1,
                                 0,1,0,
                                 0,0,0,
                                 0,1,0], posX, posY, color, colorBG)
            elif char == '!':
                self.display5x3([0,1,0,
                                 0,1,0,
                                 0,1,0,
                                 0,0,0,
                                 0,1,0], posX, posY, color, colorBG)
            elif char == '-':
                self.display5x3([0,0,0,
                                 0,0,0,
                                 1,1,1,
                                 0,0,0,
                                 0,0,0], posX, posY, color, colorBG)
            elif char == '+':
                self.display5x3([0,0,0,
                                 0,1,0,
                                 1,1,1,
                                 0,1,0,
                                 0,0,0], posX, posY, color, colorBG)
            
            # Alphabet
            elif char == 'T':
                self.display5x3([1,1,1,
                                 0,1,0,
                                 0,1,0,
                                 0,1,0,
                                 0,1,0], posX, posY, color, colorBG)
            elif char == 'A':
                self.display5x3([1,1,1,
                                 1,0,1,
                                 1,1,1,
                                 1,0,1,
                                 1,0,1], posX, posY, color, colorBG)
            elif char == 'L':
                self.display5x3([1,0,0,
                                 1,0,0,
                                 1,0,0,
                                 1,0,0,
                                 1,1,1], posX, posY, color, colorBG)
            elif char == 'Y':
                self.display5x3([1,0,1,
                                 1,0,1,
                                 0,1,0,
                                 0,1,0,
                                 0,1,0], posX, posY, color, colorBG)
            
            else:
                print(f"char {char} not implemented")
                self.display5x3([1,1,1,
                                 0,0,1,
                                 0,1,0,
                                 0,0,0,
                                 0,1,0], posX, posY, color, colorBG)
        
    def displayString(self, string, posX, posY, color, colorBG, delay):
        for char in string:
            self.displayChar(char, posX, posY, color, colorBG)
            self.pixels_show()
            time.sleep(delay)
    
    def displayStringHorz(self, string, posX, posY, color, colorBG):
        for char in string:
            self.displayChar(char, posX, posY, color, colorBG)
            posX += 4
        self.pixels_show()
