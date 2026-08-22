from machine import Pin
import neopixel
import time

import audioio
import board

buttons = [Pin(i, Pin.IN, Pin.PULL_UP) for i in range(1, 13)]

pixels = neopixel.NeoPixel(
    Pin(19),
    12
)

endProgramm = False

endPattern = [0, 1, 2, 11]

lastClicks = []

previousStates = [1] * 12


def checkIfEndPattern(lastClicks, endPattern):
    return lastClicks[-len(endPattern):] == endPattern


while not endProgramm:
    for i, button in enumerate(buttons):
        currentState = button.value()

        if previousStates[i] == 1 and currentState == 0:
            lastClicks.append(i)

            print("Button:", i + 1)
            print("Pattern:", lastClicks)

            if checkIfEndPattern(lastClicks, endPattern):
                endProgramm = True
                break

        if currentState == 0:
            pixels[i] = (255, 0, 0)
        else:
            pixels[i] = (0, 0, 0)

        previousStates[i] = currentState

    pixels.write()
    time.sleep_ms(10)

def soundplayer(index):
    wave_file = open("sound" + str(index) + ".wav", "rb")
    wave = audioio.WaveFile(wave_file)
    with audioio.AudioOut(board.A0) as audio:
        audio.play(wave)
        while audio.playing:
            pass



