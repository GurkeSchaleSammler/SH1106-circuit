from machine import Pin, I2C

import config


# ------------------------------------------------------------
# Shared GPIO pin configuration
# ------------------------------------------------------------
# These pins work for both the Wokwi setup and
# the Adafruit MacroPad RP2040.
BUTTON_PINS = tuple(range(1, 13))

ENCODER_CLK_PIN = 18
ENCODER_DT_PIN = 17
ENCODER_SWITCH_PIN = 0

NEOPIXEL_PIN = 19
PIXEL_COUNT = 12

SPEAKER_PIN = 16
SPEAKER_ENABLE_PIN = 14

# Wokwi: external SSD1306 via I2C
WOKWI_OLED_SDA_PIN = 20
WOKWI_OLED_SCL_PIN = 21
WOKWI_OLED_ADDRESS = 0x3C

# Real MacroPad: built-in SH1106 via SPI1
MACROPAD_OLED_SCK_PIN = 26
MACROPAD_OLED_MOSI_PIN = 27
MACROPAD_OLED_MISO_PIN = 28
MACROPAD_OLED_CS_PIN = 22
MACROPAD_OLED_RST_PIN = 23
MACROPAD_OLED_DC_PIN = 24


def _detect_wokwi():
    if config.TARGET == "wokwi":
        return True

    if config.TARGET == "macropad":
        return False

    i2c = None

    try:
        i2c = I2C(
            0,
            sda=Pin(WOKWI_OLED_SDA_PIN),
            scl=Pin(WOKWI_OLED_SCL_PIN),
            freq=400_000,
        )

        return WOKWI_OLED_ADDRESS in i2c.scan()

    except Exception:
        return False

    finally:
        if i2c is not None:
            try:
                i2c.deinit()
            except Exception:
                pass


IS_WOKWI = _detect_wokwi()
IS_MACROPAD = not IS_WOKWI

if IS_WOKWI:
    AUDIO_ENABLED = config.WOKWI_AUDIO_ENABLED
    TARGET_NAME = "Wokwi Raspberry Pi Pico"
else:
    AUDIO_ENABLED = config.REAL_AUDIO_ENABLED
    TARGET_NAME = "Adafruit MacroPad RP2040"