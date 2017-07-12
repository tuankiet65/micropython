import pyb

PORTS = {
    "UART1": pyb.UART(1),
    "UART2": pyb.UART(2),
    "UART3": pyb.UART(6)
}

def get_port(port_id):
    port = PORTS[port_id]
    if type(port) is pyb.UART:
        port.init(38400, timeout = 1000)
    return port