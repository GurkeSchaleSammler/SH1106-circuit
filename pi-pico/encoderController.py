from machine import Pin
import time

import hardware


MIN_MODE = -8
MAX_MODE = 8

DIRECTION = 1


class EncoderController:
    def __init__(self):
        self.clk = Pin(
            hardware.ENCODER_CLK_PIN,
            Pin.IN,
            Pin.PULL_UP,
        )

        self.dt = Pin(
            hardware.ENCODER_DT_PIN,
            Pin.IN,
            Pin.PULL_UP,
        )

        self.switch = Pin(
            hardware.ENCODER_SWITCH_PIN,
            Pin.IN,
            Pin.PULL_UP,
        )

        self.lastState = self._readState()
        self.accumulator = 0

        self.lastSwitchState = self.switch.value()
        self.lastSwitchChange = time.ticks_ms()

    def _readState(self):
        return (
            (self.clk.value() << 1)
            | self.dt.value()
        )

    def update(self, currentMode):
        currentState = self._readState()

        if currentState == self.lastState:
            return currentMode, False

        transition = (
            (self.lastState << 2)
            | currentState
        )

        self.lastState = currentState

        transitionTable = (
             0, -1,  1,  0,
             1,  0,  0, -1,
            -1,  0,  0,  1,
             0,  1, -1,  0,
        )

        self.accumulator += transitionTable[transition]

        # KY-040
        if self.accumulator >= 4:
            self.accumulator = 0

            newMode = currentMode + DIRECTION

        elif self.accumulator <= -4:
            self.accumulator = 0

            newMode = currentMode - DIRECTION

        else:
            return currentMode, False

        if newMode > MAX_MODE:
            newMode = MAX_MODE

        elif newMode < MIN_MODE:
            newMode = MIN_MODE

        return newMode, newMode != currentMode

    def switchPressed(self):
        currentState = self.switch.value()
        now = time.ticks_ms()

        if currentState != self.lastSwitchState:
            if time.ticks_diff(
                now,
                self.lastSwitchChange,
            ) >= 30:
                self.lastSwitchState = currentState
                self.lastSwitchChange = now

                if currentState == 0:
                    return True

        return False