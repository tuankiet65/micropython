import pyb

PORTS = {
    "UART0": pyb.UART(1),
    "UART1": pyb.UART(2),
    "UART2": pyb.UART(6)
}

def get_port(port_id):
    port = PORTS[port_id]
    if type(port) is pyb.UART:
        port.init(9600, timeout = 100)
    return port