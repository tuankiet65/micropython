# Looks like in MicroPython
# OrderedDict is implemented in the exact same way as dict
# The same functions, the same code, just different name
# Let's hope that dict is OrderedDict and not the vice versa

from pnc.uart_request.port import get_port
from pnc.uart_request.value import *


class Request:
    port = None

    def __init__(self, port_id):
        self.port = get_port(port_id)

    def send(self, request_type, args = None, ret = None) -> PacketResponse:
        if args is None:
            args = []

        # Clear any remaining data
        self.port.read(self.port.any())

        packet = PacketRequest(request_type, args)
        packet.send(self.port)

        req = PacketResponse()
        req.read_response(self.port)
        req.raise_for_status()
        req.decode_data(ret)
        return req


class PacketBase:
    STATUS_CODE_SUCCESS = const(0x00)
    STATUS_CODE_FAILURE = const(0x01)

    ERROR_TIMEOUT = const(0x00)
    ERROR_SIZE_TOO_LARGE = const(0x01)
    ERROR_WRONG_NUMBER_OF_ARGUMENT = const(0x02)
    ERROR_INVALID_COMMAND = const(0x03)


class PacketRequest(PacketBase):
    request_type = None
    args = []

    packet = bytes()

    def __init__(self, request_type, args):
        self.request_type = request_type
        self.args = args

    def assemble_packet(self) -> bytes:
        data_size = sum([arg.size for arg in self.args])
        if data_size > 8:
            raise Value("args size is too large, maximum size is 8 bytes")

        tmp_args = [UInt8Value(self.request_type), UInt8Value(data_size)]
        tmp_args.extend(self.args)

        for arg in tmp_args:
            self.packet += arg.__bytes__()

        return self.packet

    def send(self, port):
        port.write(self.assemble_packet())


class PacketResponse(PacketBase):
    status_code = None
    raw_data_size = None
    raw_data = None
    data = None

    def read_response(self, port):
        self.status_code = port.readchar()
        if self.status_code < 0:
            raise TimeoutException

        self.raw_data_size = port.readchar()
        if self.raw_data_size < 0:
            raise TimeoutException

        if self.raw_data_size > 0:
            self.raw_data = port.read(self.raw_data_size)
            if (self.raw_data is None) or (len(self.raw_data) != self.raw_data_size):
                raise TimeoutException
        else:
            self.raw_data = b''

    def raise_for_status(self):
        if self.status_code == self.STATUS_CODE_FAILURE:
            if self.raw_data_size == 0:
                return
                raise Exception("Unknown error, module does not return error code")
            # TODO add various type of failure codes
            if self.data[0] == self.ERROR_INVALID_COMMAND:
                raise Exception("Invalid command")
            elif self.data[0] == self.ERROR_WRONG_NUMBER_OF_ARGUMENT:
                raise Exception("Wrong number of argument")
            elif self.data[0] == self.ERROR_TIMEOUT:
                raise TimeoutException
            elif self.data[0] == self.ERROR_SIZE_TOO_LARGE:
                raise Exception("Data size too large")

    def decode_data(self, args: list = None):
        # args is a tuple of (<name>, <type>)
        if args is None:
            args = []

        data_size = sum([arg[1].size for arg in args])
        if data_size != self.raw_data_size:
            raise ValueError("total args size is different from data len ({} vs {})".format(data_size, len(self.data)))

        data_ptr = 0
        self.data = {}

        for arg in args:
            self.data[arg[0]] = arg[1].from_bytes(self.raw_data[data_ptr:data_ptr + arg[1].size])
            data_ptr += arg[1].size


class TimeoutException(Exception):
    pass
