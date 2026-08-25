from machine import Pin

import hardware


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

    def _readState(self):
        return (
            (self.clk.value() << 1)
            | self.dt.value()
        )

    def getRotation(self):
        currentState = self._readState()

        if currentState == self.lastState:
            return 0

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

        if self.accumulator >= 4:
            self.accumulator = 0
            return DIRECTION

        if self.accumulator <= -4:
            self.accumulator = 0
            return -DIRECTION

        return 0

    def isPressed(self):
        return self.switch.value() == 0