import os
import time
import ustruct

from machine import Pin, PWM

import config
import hardware


class SoundPlayer:
    def __init__(self):
        self.enabled = hardware.AUDIO_ENABLED
        self.generation = 0
        self.pending = None

        self.speakerEnable = None
        self.pwm = None

        if not self.enabled:
            print("Audio disabled - Wokwi simulation")
            return

        self.speakerEnable = Pin(
            hardware.SPEAKER_ENABLE_PIN,
            Pin.OUT,
            value=1,
        )

        self.pwm = PWM(
            Pin(hardware.SPEAKER_PIN)
        )

        # High PWM carrier frequency.
        # The audio level is controlled via duty_u16.
        self.pwm.freq(62_500)
        self.pwm.duty_u16(32_768)

        try:
            import _thread

            self.threadModule = _thread
            _thread.start_new_thread(
                self._worker,
                (),
            )

            print(
                "Audio enabled - real MacroPad"
            )

        except ImportError:
            self.enabled = False
            self.pwm.deinit()
            self.pwm = None

            print(
                "Audio disabled: _thread is missing"
            )

    def resolveSound(
        self,
        buttonIndex,
        mode,
    ):
        if mode == -8:
            return 12 + buttonIndex, 0

        if mode == 8:
            soundNumber = 24 + buttonIndex

            # Your configuration uses sound24 through sound33.
            # Therefore, buttons 11 and 12 have no sound assigned here.
            if soundNumber > 33:
                return None, 0

            return soundNumber, 0

        # Piano mode always uses sound0 through sound11.
        # mode -7..+7 represents the octave shift.
        return buttonIndex, mode

    def playSound(
        self,
        buttonIndex,
        mode,
    ):
        soundNumber, octaveShift = self.resolveSound(
            buttonIndex,
            mode,
        )

        if soundNumber is None:
            print(
                "No sound assigned to button:",
                buttonIndex + 1,
            )

            return None, "No sound"

        filename = (
            "sound"
            + str(soundNumber)
            + ".wav"
        )

        if not self.enabled:
            print(
                "SIMULATED:",
                filename,
                "octave:",
                octaveShift,
            )

            return soundNumber, None

        real_filename = "/" + filename

        try:
            os.stat(real_filename)

        except OSError:
            print(
                "File missing:",
                real_filename,
            )

            return None, "File missing"

        self.generation += 1

        self.pending = (
            real_filename,
            octaveShift,
            self.generation,
        )

        print(
            "Play:",
            filename,
            "octave:",
            octaveShift,
        )

        return soundNumber, None

    def stop(self):
        self.generation += 1
        self.pending = None

        if self.pwm is not None:
            self.pwm.duty_u16(32_768)

    def update(self):
        # Audio runs on the second RP2040 core.
        pass

    def _worker(self):
        while True:
            request = self.pending

            if request is None:
                time.sleep_ms(5)
                continue

            self.pending = None

            filename = request[0]
            octaveShift = request[1]
            generation = request[2]

            try:
                self._playWav(
                    filename,
                    octaveShift,
                    generation,
                )

            except Exception as error:
                print(
                    "Audio worker error:",
                    error,
                )

                if self.pwm is not None:
                    self.pwm.duty_u16(32_768)

    def _readWav(self, filename):
        wav = open(filename, "rb")

        try:
            if wav.read(4) != b"RIFF":
                raise ValueError(
                    "Not a RIFF WAV file"
                )

            wav.read(4)

            if wav.read(4) != b"WAVE":
                raise ValueError(
                    "Not a WAVE file"
                )

            audio_format = None
            channels = None
            sample_rate = None
            bits_per_sample = None
            data = None

            while True:
                chunk_id = wav.read(4)

                if len(chunk_id) < 4:
                    break

                chunk_size_data = wav.read(4)

                if len(chunk_size_data) < 4:
                    break

                chunk_size = ustruct.unpack(
                    "<I",
                    chunk_size_data,
                )[0]

                if chunk_id == b"fmt ":
                    fmt = wav.read(chunk_size)

                    if len(fmt) < 16:
                        raise ValueError(
                            "Invalid fmt chunk"
                        )

                    (
                        audio_format,
                        channels,
                        sample_rate,
                        _byte_rate,
                        _block_align,
                        bits_per_sample,
                    ) = ustruct.unpack(
                        "<HHIIHH",
                        fmt[:16],
                    )

                elif chunk_id == b"data":
                    if (
                        chunk_size
                        > config.MAX_AUDIO_BYTES
                    ):
                        raise MemoryError(
                            "WAV file is too large"
                        )

                    data = wav.read(chunk_size)
                    break

                else:
                    wav.seek(
                        chunk_size,
                        1,
                    )

                if chunk_size & 1:
                    wav.seek(1, 1)

            if audio_format != 1:
                raise ValueError(
                    "Only PCM WAV is supported"
                )

            if channels not in (1, 2):
                raise ValueError(
                    "Only mono or stereo is supported"
                )

            if bits_per_sample not in (8, 16):
                raise ValueError(
                    "Only 8-bit or 16-bit audio is supported"
                )

            if data is None:
                raise ValueError(
                    "No data chunk found"
                )

            return (
                data,
                channels,
                sample_rate,
                bits_per_sample,
            )

        finally:
            wav.close()

    def _playWav(
        self,
        filename,
        octaveShift,
        generation,
    ):
        (
            data,
            channels,
            sourceRate,
            bitsPerSample,
        ) = self._readWav(filename)

        outputRate = config.AUDIO_OUTPUT_RATE

        if outputRate < 1000:
            outputRate = 1000

        bytesPerSample = bitsPerSample // 8
        frameSize = bytesPerSample * channels

        totalFrames = (
            len(data) // frameSize
        )

        # Q16.16 source position.
        # This also allows negative octave shifts
        # by repeating samples during playback.
        baseStep = (
            sourceRate << 16
        ) // outputRate

        if octaveShift >= 0:
            step = baseStep << octaveShift
        else:
            step = baseStep >> abs(
                octaveShift
            )

            if step < 1:
                step = 1

        position = 0
        periodUs = (
            1_000_000 // outputRate
        )

        nextTick = time.ticks_us()

        while True:
            if generation != self.generation:
                break

            frameIndex = position >> 16

            if frameIndex >= totalFrames:
                break

            offset = frameIndex * frameSize

            if bitsPerSample == 8:
                sample = data[offset]

                # Unsigned 8-bit -> 0..65535
                duty = sample * 257

            else:
                low = data[offset]
                high = data[offset + 1]

                sample = low | (high << 8)

                if sample & 0x8000:
                    sample -= 65536

                duty = sample + 32768

            self.pwm.duty_u16(duty)

            position += step
            nextTick = time.ticks_add(
                nextTick,
                periodUs,
            )

            while (
                time.ticks_diff(
                    nextTick,
                    time.ticks_us(),
                )
                > 0
            ):
                pass

        self.pwm.duty_u16(32_768)