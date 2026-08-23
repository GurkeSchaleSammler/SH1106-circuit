# Minimaler SH1106-SPI-Treiber fuer das eingebaute
# 128x64 OLED des Adafruit MacroPad RP2040.

import framebuf
import time


class SH1106_SPI:
    def __init__(
        self,
        width,
        height,
        spi,
        dc,
        reset,
        cs,
    ):
        self.width = width
        self.height = height
        self.pages = height // 8

        self.spi = spi
        self.dc = dc
        self.resetPin = reset
        self.cs = cs

        self.buffer = bytearray(
            self.width * self.pages
        )

        self.framebuf = framebuf.FrameBuffer(
            self.buffer,
            self.width,
            self.height,
            framebuf.MONO_VLSB,
        )

        self.reset()
        self.init_display()

    def reset(self):
        self.resetPin.value(1)
        time.sleep_ms(1)
        self.resetPin.value(0)
        time.sleep_ms(10)
        self.resetPin.value(1)
        time.sleep_ms(10)

    def write_cmd(self, cmd):
        self.cs.value(1)
        self.dc.value(0)
        self.cs.value(0)

        self.spi.write(bytes((cmd,)))

        self.cs.value(1)

    def write_data(self, data):
        self.cs.value(1)
        self.dc.value(1)
        self.cs.value(0)

        self.spi.write(data)

        self.cs.value(1)

    def init_display(self):
        commands = (
            0xAE,
            0xD5,
            0x80,
            0xA8,
            0x3F,
            0xD3,
            0x00,
            0x40,
            0xAD,
            0x8B,
            0xA1,
            0xC8,
            0xDA,
            0x12,
            0x81,
            0x7F,
            0xD9,
            0x22,
            0xDB,
            0x40,
            0xA4,
            0xA6,
            0xAF,
        )

        for cmd in commands:
            self.write_cmd(cmd)

        self.fill(0)
        self.show()

    def fill(self, color):
        self.framebuf.fill(color)

    def pixel(self, x, y, color=None):
        if color is None:
            return self.framebuf.pixel(x, y)

        self.framebuf.pixel(x, y, color)

    def text(self, string, x, y, color=1):
        self.framebuf.text(
            string,
            x,
            y,
            color,
        )

    def show(self):
        # SH1106 besitzt intern 132 Spalten.
        # Das 128px Panel startet mit Offset 2.
        column_offset = 2

        for page in range(self.pages):
            self.write_cmd(0xB0 | page)

            self.write_cmd(
                0x00 | (column_offset & 0x0F)
            )

            self.write_cmd(
                0x10 | (column_offset >> 4)
            )

            start = page * self.width
            end = start + self.width

            self.write_data(
                self.buffer[start:end]
            )
