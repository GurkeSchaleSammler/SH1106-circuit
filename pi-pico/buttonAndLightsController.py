from machine import Pin
import neopixel

import hardware


LED_ON = (255, 0, 0)
LED_OFF = (0, 0, 0)


class ButtonAndLightsController:
    def __init__(self):
        self.buttons = [
            Pin(pin_number, Pin.IN, Pin.PULL_UP)
            for pin_number in hardware.BUTTON_PINS
        ]

        self.previousStates = [
            button.value()
            for button in self.buttons
        ]

        self.pixels = neopixel.NeoPixel(
            Pin(hardware.NEOPIXEL_PIN),
            hardware.PIXEL_COUNT,
        )

        self.clear()

    def poll(self):
        events = []
        pixels_changed = False

        for index, button in enumerate(self.buttons):
            current_state = button.value()
            previous_state = self.previousStates[index]

            if current_state != previous_state:
                pressed = current_state == 0

                events.append((index, pressed))

                if pressed:
                    self.pixels[index] = LED_ON
                else:
                    self.pixels[index] = LED_OFF

                pixels_changed = True
                self.previousStates[index] = current_state

        if pixels_changed:
            self.pixels.write()

        return events

    def clear(self):
        for index in range(hardware.PIXEL_COUNT):
            self.pixels[index] = LED_OFF

        self.pixels.write()
