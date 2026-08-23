import time

import hardware

from buttonAndLightsController import ButtonAndLightsController
from displayController import DisplayController
from encoderController import EncoderController
from soundPlayer import SoundPlayer


buttonAndLightsController = ButtonAndLightsController()
encoderController = EncoderController()
displayController = DisplayController()
soundPlayer = SoundPlayer()


endProgramm = False

endPattern = [0, 1, 2, 11]

lastClicks = []

currentMode = 0


def checkIfEndPattern():
    return (
        lastClicks[-len(endPattern):]
        == endPattern
    )


print(
    "Hardware:",
    hardware.TARGET_NAME,
)

print(
    "Audio:",
    "enabled"
    if hardware.AUDIO_ENABLED
    else "disabled",
)

displayController.showMode(
    currentMode
)


while not endProgramm:
    # --------------------------------------------------------
    # Encoder
    # --------------------------------------------------------
    newMode, modeChanged = (
        encoderController.update(
            currentMode
        )
    )

    if modeChanged:
        currentMode = newMode

        print(
            "Mode:",
            currentMode,
        )

        displayController.showMode(
            currentMode
        )

    if encoderController.switchPressed():
        currentMode = 0

        print(
            "Encoder pressed -> Original"
        )

        displayController.showMode(
            currentMode
        )

    # --------------------------------------------------------
    # Buttons + NeoPixels
    # --------------------------------------------------------
    events = (
        buttonAndLightsController.poll()
    )

    for buttonIndex, pressed in events:
        if not pressed:
            continue

        lastClicks.append(
            buttonIndex
        )

        lastClicks = lastClicks[
            -len(endPattern):
        ]

        print(
            "Button:",
            buttonIndex + 1,
        )

        print(
            "Pattern:",
            lastClicks,
        )

        soundNumber, error = (
            soundPlayer.playSound(
                buttonIndex,
                currentMode,
            )
        )

        if error is not None:
            displayController.showMode(
                currentMode,
                status=error,
            )

        elif soundNumber is not None:
            displayController.showMode(
                currentMode,
                soundNumber=soundNumber,
            )

        if checkIfEndPattern():
            print(
                "End pattern received!"
            )

            endProgramm = True
            break

    soundPlayer.update()

    time.sleep_ms(5)


soundPlayer.stop()
buttonAndLightsController.clear()
displayController.showStopped()

print("END.")
