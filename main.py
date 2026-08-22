from machine import Pin
import neopixel
import time


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


def soundplayer(index):
    filename = "sound" + str(index) + ".wav"

    print("Play:", filename)

    # Hier kommt die MicroPython-Audioausgabe hin


while not endProgramm:
    for i, button in enumerate(buttons):
        currentState = button.value()

        # Button wurde gerade heruntergedrückt
        if previousStates[i] == 1 and currentState == 0:
            lastClicks.append(i)

            print("Button:", i + 1)
            print("Pattern:", lastClicks)

            soundplayer(i)

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