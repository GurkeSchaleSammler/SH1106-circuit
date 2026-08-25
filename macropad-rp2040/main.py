import time

import config
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

currentVolume = config.DEFAULT_VOLUME


def checkIfEndPattern():
    return (
        lastClicks[-len(endPattern):]
        == endPattern
    )


def clamp(value, minimum, maximum):
    if value < minimum:
        return minimum

    if value > maximum:
        return maximum

    return value


def getVolumePercent():
    return round(
        currentVolume * 100
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

print(
    "Volume:",
    str(getVolumePercent()) + "%",
)

soundPlayer.setVolume(
    currentVolume
)

displayController.showMode(
    currentMode,
    status=(
        "Volume: "
        + str(getVolumePercent())
        + "%"
    ),
)


while not endProgramm:
    # --------------------------------------------------------
    # Encoder
    # --------------------------------------------------------
    rotation = encoderController.getRotation()

    if rotation != 0:

        # ----------------------------------------------------
        # Encoder held + rotation
        # -> change octave / mode
        # ----------------------------------------------------
        if encoderController.isPressed():
            currentMode += rotation

            currentMode = clamp(
                currentMode,
                -8,
                8,
            )

            print(
                "Mode:",
                currentMode,
            )

            displayController.showMode(
                currentMode
            )

        # ----------------------------------------------------
        # Normal encoder rotation
        # -> change volume
        # ----------------------------------------------------
        else:
            currentVolume += (
                rotation
                * config.VOLUME_STEP
            )

            currentVolume = clamp(
                currentVolume,
                config.MIN_VOLUME,
                config.MAX_VOLUME,
            )

            soundPlayer.setVolume(
                currentVolume
            )

            volumePercent = (
                getVolumePercent()
            )

            print(
                "Volume:",
                str(volumePercent) + "%",
            )

            displayController.showMode(
                currentMode,
                status=(
                    "Volume: "
                    + str(volumePercent)
                    + "%"
                ),
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