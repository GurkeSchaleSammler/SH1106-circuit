from machine import Pin, I2C, SPI

import hardware


class DisplayController:
    def __init__(self):
        self.display = None

        if hardware.IS_WOKWI:
            self._initWokwiDisplay()
        else:
            self._initMacroPadDisplay()

    def _initWokwiDisplay(self):
        from ssd1306 import SSD1306_I2C

        self.i2c = I2C(
            0,
            sda=Pin(hardware.WOKWI_OLED_SDA_PIN),
            scl=Pin(hardware.WOKWI_OLED_SCL_PIN),
            freq=400_000,
        )

        self.display = SSD1306_I2C(
            128,
            64,
            self.i2c,
            addr=hardware.WOKWI_OLED_ADDRESS,
        )

    def _initMacroPadDisplay(self):
        from sh1106 import SH1106_SPI

        self.spi = SPI(
            1,
            baudrate=10_000_000,
            polarity=0,
            phase=0,
            sck=Pin(hardware.MACROPAD_OLED_SCK_PIN),
            mosi=Pin(hardware.MACROPAD_OLED_MOSI_PIN),
            miso=Pin(hardware.MACROPAD_OLED_MISO_PIN),
        )

        dc = Pin(
            hardware.MACROPAD_OLED_DC_PIN,
            Pin.OUT,
            value=0,
        )

        reset = Pin(
            hardware.MACROPAD_OLED_RST_PIN,
            Pin.OUT,
            value=1,
        )

        cs = Pin(
            hardware.MACROPAD_OLED_CS_PIN,
            Pin.OUT,
            value=1,
        )

        self.display = SH1106_SPI(
            128,
            64,
            self.spi,
            dc,
            reset,
            cs,
        )

    def _draw(self, line1, line2="", line3=""):
        self.display.fill(0)

        self.display.text(
            "MacroPad",
            0,
            0,
            1,
        )

        self.display.text(
            line1[:16],
            0,
            16,
            1,
        )

        self.display.text(
            line2[:16],
            0,
            32,
            1,
        )

        self.display.text(
            line3[:16],
            0,
            48,
            1,
        )

        self.display.show()

    def showMode(
        self,
        mode,
        soundNumber=None,
        status=None,
    ):
        if mode == -8:
            line1 = "Soundboard"
            line2 = "sound12 - 23"

        elif mode == 8:
            line1 = "Soundboard"
            line2 = "sound24 - 33"

        elif mode == 0:
            line1 = "Piano"
            line2 = "Original"

        elif mode < 0:
            count = abs(mode)
            line1 = "Piano"

            if count == 1:
                line2 = "1 octave lower"
            else:
                line2 = (
                    str(count)
                    + " octaves lower"
                )

        else:
            count = mode
            line1 = "Piano"

            if count == 1:
                line2 = "1 octave higher"
            else:
                line2 = (
                    str(count)
                    + " octaves higher"
                )

        if status is not None:
            line3 = status

        elif soundNumber is not None:
            line3 = (
                "sound"
                + str(soundNumber)
                + ".wav"
            )

        else:
            line3 = ""

        self._draw(
            line1,
            line2,
            line3,
        )

    def showStopped(self):
        self._draw(
            "Program",
            "stopped",
            "",
        )