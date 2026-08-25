# "auto"     -> Wokwi is detected via the I2C OLED.
# "wokwi"    -> Force simulation mode.
# "macropad" -> Force real Adafruit MacroPad mode.
TARGET = "auto"

# Audio intentionally remains disabled in Wokwi.
WOKWI_AUDIO_ENABLED = False

# Real MacroPad: WAV playback via the built-in PWM speaker.
REAL_AUDIO_ENABLED = True

# Python PWM playback is most stable at 8 kHz.
# Recommended WAV format:
# PCM, Mono, 8-bit unsigned or 16-bit signed.
AUDIO_OUTPUT_RATE = 8000

# A complete WAV data block is loaded into RAM for playback.
# The RP2040 has limited RAM, so keep sound files small.
MAX_AUDIO_BYTES = 180_000

DEFAULT_VOLUME = 0.30
MIN_VOLUME = 0.00
MAX_VOLUME = 1.00
VOLUME_STEP = 0.05