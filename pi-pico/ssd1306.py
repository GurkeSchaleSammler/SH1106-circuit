# Minimaler SSD1306-I2C-Treiber fuer MicroPython.
# Basierend auf dem ueblichen MicroPython-FrameBuffer-Ansatz.

from micropython import const
import framebuf


_SET_CONTRAST = const(0x81)
_SET_ENTIRE_ON = const(0xA4)
_SET_NORM_INV = const(0xA6)
_SET_DISP = const(0xAE)
_SET_MEM_ADDR = const(0x20)
_SET_COL_ADDR = const(0x21)
_SET_PAGE_ADDR = const(0x22)
_SET_DISP_START_LINE = const(0x40)
_SET_SEG_REMAP = const(0xA0)
_SET_MUX_RATIO = const(0xA8)
_SET_COM_OUT_DIR = const(0xC0)
_SET_DISP_OFFSET = const(0xD3)
_SET_COM_PIN_CFG = const(0xDA)
_SET_DISP_CLK_DIV = const(0xD5)
_SET_PRECHARGE = const(0xD9)
_SET_VCOM_DESEL = const(0xDB)
_SET_CHARGE_PUMP = const(0x8D)


class SSD1306:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.pages = height // 8

        self.buffer = bytearray(
            self.pages * self.width
        )

        self.framebuf = framebuf.FrameBuffer(
            self.buffer,
            self.width,
            self.height,
            framebuf.MONO_VLSB,
        )

        self.init_display()

    def init_display(self):
        for cmd in (
            _SET_DISP | 0x00,
            _SET_MEM_ADDR,
            0x00,
            _SET_DISP_START_LINE | 0x00,
            _SET_SEG_REMAP | 0x01,
            _SET_MUX_RATIO,
            self.height - 1,
            _SET_COM_OUT_DIR | 0x08,
            _SET_DISP_OFFSET,
            0x00,
            _SET_COM_PIN_CFG,
            0x12 if self.height == 64 else 0x02,
            _SET_DISP_CLK_DIV,
            0x80,
            _SET_PRECHARGE,
            0xF1,
            _SET_VCOM_DESEL,
            0x30,
            _SET_CONTRAST,
            0xFF,
            _SET_ENTIRE_ON,
            _SET_NORM_INV,
            _SET_CHARGE_PUMP,
            0x14,
            _SET_DISP | 0x01,
        ):
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


class SSD1306_I2C(SSD1306):
    def __init__(
        self,
        width,
        height,
        i2c,
        addr=0x3C,
    ):
        self.i2c = i2c
        self.addr = addr
        self.temp = bytearray(2)

        super().__init__(width, height)

    def write_cmd(self, cmd):
        self.temp[0] = 0x80
        self.temp[1] = cmd

        self.i2c.writeto(
            self.addr,
            self.temp,
        )

    def show(self):
        self.write_cmd(_SET_COL_ADDR)
        self.write_cmd(0)
        self.write_cmd(self.width - 1)

        self.write_cmd(_SET_PAGE_ADDR)
        self.write_cmd(0)
        self.write_cmd(self.pages - 1)

        self.i2c.writevto(
            self.addr,
            [
                b"\x40",
                self.buffer,
            ],
        )
