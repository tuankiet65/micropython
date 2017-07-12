from pnc.uart_request.request import Request, PacketResponse
import pyb

class ModuleBase:
    port = None

    def get_module_info(self):
        raise NotImplementedError

    def __init__(self, port_id):
        self.port = Request(port_id)
        self.get_module_info()

    def send(self, *args, **kwargs) -> PacketResponse:
        result = self.port.send(*args, **kwargs)
        return result
