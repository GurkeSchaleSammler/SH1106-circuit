# MacroPad - MicroPython

This project uses **MicroPython only**.

The same source code is intended to run on:

* Wokwi / Raspberry Pi Pico
* a real Adafruit MacroPad RP2040

## Hardware Detection

`hardware.py` checks GP20/GP21 for the Wokwi I2C OLED at address `0x3C`.

* OLED `0x3C` detected -> Wokwi
* no OLED `0x3C` detected -> real MacroPad

In `config.py`, the target can also be forced manually using:

```python
TARGET = "wokwi"
```

or:

```python
TARGET = "macropad"
```

## Pin Assignment

### Shared

* Buttons: GP1 to GP12
* Encoder CLK / A: GP18
* Encoder DT / B: GP17
* Encoder Switch: GP0
* NeoPixels: GP19
* Speaker: GP16

### Real MacroPad Only

* Speaker Enable: GP14
* OLED CS: GP22
* OLED Reset: GP23
* OLED DC: GP24
* OLED SPI SCK: GP26
* OLED SPI MOSI: GP27
* OLED SPI MISO: GP28

### Wokwi Only

* OLED SDA: GP20
* OLED SCL: GP21
* OLED address: `0x3C`

## Modes

* `-8`: Soundboard using `sound12.wav` to `sound23.wav`
* `-7 .. -1`: `sound0.wav` to `sound11.wav`, pitched down
* `0`: Original `sound0.wav` to `sound11.wav`
* `+1 .. +7`: `sound0.wav` to `sound11.wav`, pitched up
* `+8`: Soundboard using `sound24.wav` to `sound33.wav`

At `+8`, only 10 files are currently defined. Buttons 11 and 12 therefore have no assigned sound.

Pressing the encoder resets the mode to `0`.

Exit pattern:

`Button 1 -> Button 2 -> Button 3 -> Button 12`

## Audio

### Wokwi

Audio is intentionally disabled.

The terminal will instead display messages such as:

```text
SIMULATED: sound0.wav octave: 0
```

### Real MacroPad

The player uses the built-in speaker via PWM on GP16.

GP14 is set HIGH to enable the speaker.

Pitch shifting is implemented through resampling. This also changes playback duration:

* +1 octave -> approximately double playback speed
* -1 octave -> approximately half playback speed

At extreme values such as `+/-7`, the effect is correspondingly extreme.

## Recommended WAV Format

The MicroPython player supports:

* PCM WAV
* Mono or stereo
* 8-bit unsigned or 16-bit signed audio

Recommended for the limited RP2040 RAM:

* Mono
* 8-bit PCM
* 11025 Hz
* Short samples

Using ffmpeg:

```powershell
ffmpeg -i input.wav -ac 1 -ar 11025 -c:a pcm_u8 sound0.wav
```

`config.py` limits a loaded audio data block to `180000` bytes by default.

## Starting Wokwi

### 1. MicroPython Firmware

`wokwi.toml` expects:

```text
RPI_PICO-20251209-v1.27.0.uf2
```

The firmware file must be located in the same directory.

### 2. Start the Simulator

In VS Code:

```text
F1 -> Wokwi: Start Simulator
```

### 3. Run the Code

In a PowerShell terminal inside the project directory:

```powershell
.\run-wokwi.ps1
```

Alternatively, run it directly:

```powershell
python -m mpremote connect port:rfc2217://localhost:4000 mount . exec "import main"
```

`mount .` is important because it allows MicroPython to access all local modules without copying every file individually to the simulated Pico.

## PC Dependency

Only `mpremote` is required:

```powershell
python -m pip install mpremote
```

You do **not** need `board`, `audioio`, or any CircuitPython package.

Modules such as:

```text
machine
neopixel
framebuf
_thread
```

are provided by MicroPython.

## Real MacroPad

The real MacroPad must also run MicroPython.

Afterwards, run:

```powershell
.\deploy-real-pad.ps1
```

The script copies all Python files and all `sound*.wav` files to the connected board.

Important: The official MicroPython download page currently does not provide a dedicated build specifically for the Adafruit MacroPad RP2040.

A generic RP2040 / Raspberry Pi Pico build can access the GPIO pins, but depending on the build, it may not expose the full 8 MB flash memory of the MacroPad as filesystem storage.

If many WAV files are used, a custom MicroPython build configured for the full 8 MB flash may therefore become useful later.
