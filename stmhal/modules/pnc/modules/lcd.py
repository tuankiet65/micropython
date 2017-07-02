from pnc.uart_request.value import *
from pnc.modules.base import ModuleBase


class LCD_16x2(ModuleBase):
    column = None
    row = None

    CMD_INFO = const(0x00)
    CMD_WRITE = const(0x01)
    CMD_HOME = const(0x02)
    CMD_CLEAR = const(0x03)
    CMD_SET_DISPLAY = const(0x04)
    CMD_SET_CURSOR = const(0x05)
    CMD_SET_BLINK = const(0x06)
    CMD_SET_POSITION = const(0x07)
    CMD_SET_BACKLIGHT = const(0x08)
    CMD_INIT = const(0x09)

    def get_module_info(self):
        req = self.send(self.CMD_INFO, ret = [
            ("type", UInt8Value()),
            ("column", UInt8Value()),
            ("row", UInt8Value())
        ])

        self.column = req.data["column"]
        self.row = req.data["row"]

        self.init()

    def init(self):
        self.send(self.CMD_INIT)
    
    def home(self):
        self.send(self.CMD_HOME)

    def clear(self):
        self.send(self.CMD_CLEAR)

    def set_display(self, state: bool):
        self.send(self.CMD_SET_DISPLAY, args = [BooleanValue(state)])

    def set_cursor(self, state: bool):
        self.send(self.CMD_SET_CURSOR, args = [BooleanValue(state)])

    def set_blink(self, state: bool):
        self.send(self.CMD_SET_BLINK, args = [BooleanValue(state)])

    def set_position(self, row: int, col: int):
        self.send(self.CMD_SET_POSITION, args = [UInt8Value(row), UInt8Value(col)])

    def set_backlight(self, backlight: int):
        self.send(self.CMD_SET_BACKLIGHT, args = [UInt8Value(backlight)])

    def write(self, string: str):
        byte_string = string.encode('ascii')

        if len(string) != len(byte_string):
            raise Exception('string must not contain Unicode characters')

        for ptr in range(0, len(byte_string), 8):
            self.send(self.CMD_WRITE, args = [CharValue(string[ptr:ptr+8])])
