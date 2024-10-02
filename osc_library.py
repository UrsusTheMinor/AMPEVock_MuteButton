import argparse
from pythonosc import udp_client, dispatcher, osc_server

class OSCClient:

    def __init__(self, namespace: str, ip: str = "192.168.1.203", port: int = 49900):
        self.osc_address = None
        self.ip = ip
        self.port = port
        self.namespace = namespace
        self.fx_states = {}  # To store the current states of fx_channels

        parser = argparse.ArgumentParser()
        parser.add_argument("--ip", default=ip, help="IP address of OSC server")
        parser.add_argument("--port", default=port, type=int, help="Port of OSC server")
        args = parser.parse_args()

        # UDP client to send messages
        self.client = udp_client.SimpleUDPClient(args.ip, args.port)


    def set_osc_address(self, address):
        self.osc_address = address

    def message_set(self, fx_channel, state):
        self.client.send_message(self._get_osc_command("set", fx_channel), state)
        print(f"Sent {self.osc_address} with fx_channel {fx_channel} and state {state}")

    def multi_message_set(self, fx_channels, state):
        for fx_channel in fx_channels:
            self.message_set(fx_channel, state)

    def _get_osc_command(self, action, fx_channel):
        if action is None:
            return f"{self.namespace}{self.osc_address}/{fx_channel}"

        return f"{self.namespace}{action}/{self.osc_address}/{fx_channel}"