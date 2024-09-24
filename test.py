import argparse
from pythonosc import udp_client, dispatcher, osc_server
import threading
#
# # Define the IP address and port of your mixer
# ip = "192.168.0.2"  # Replace with the IP address of your mixer
# port = 49900     # Replace with the correct port for OSC communication
#
# # Create an OSC client
# client = udp_client.SimpleUDPClient(ip, port)
#
# # Function to send the FX return channel fader OSC command
# def set_fx_return_channel_fader(channel_num, state):
#     """ Sends an OSC command to set the FX return channel fader to on/off.
#     Args:
#         channel_num (int): The FX return channel number (1 or other depending on your setup).
#         state (int): 0 for OFF, 1 for ON.
#     """
#     osc_address = f"/yosc:req/set/MIXER:Current/Fx/Fader/On/{channel_num}"
#     client.send_message(osc_address, state)
#     print(f"Sent {osc_address} with state {state}")
#
# # Example usage:
# fx_channel = 1  # Replace with the FX return channel number you want to control
# state = 1  # 1 for ON, 0 for OFF
#
# set_fx_return_channel_fader(1, state)
# set_fx_return_channel_fader(2, state)


# class OSCClient:
#
#     def __init__(self, namespace: str, ip: str = "192.168.0.2", port: int = 49900):
#         self.osc_address = None
#         self.ip = ip
#         self.port = port
#         self.namespace = namespace
#
#         parser = argparse.ArgumentParser()
#         parser.add_argument("--ip", default=ip, help="IP address of OSC server")
#         parser.add_argument("--port", default=port, type=int, help="Port of OSC server")
#         args = parser.parse_args()
#
#         self.client = udp_client.SimpleUDPClient(args.ip, args.port)
#
#     def set_osc_address(self, address):
#         self.osc_address = address
#
#     def message_set(self, fx_channel, state):
#         self.client.send_message(self._get_osc_command("set", fx_channel), state)
#         print(f"Sent {self.osc_address} with state {state}")
#
#     def multi_message_set(self, fx_channels, state):
#         for fx_channel in fx_channels:
#             self.message_set(fx_channel, state)
#
#     def _get_osc_command(self, action, fx_channel):
#         # if not self.namespace.endswith("/"):
#         #     self.namespace = self.namespace + "/"
#
#         return f"{self.namespace}{action}/{self.osc_address}/{fx_channel}"

class OSCClient:

    def __init__(self, namespace: str, ip: str = "192.168.0.2", port: int = 49900):
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

        # OSC server for listening to incoming messages
        self.dispatcher = dispatcher.Dispatcher()
        self.dispatcher.map("/*", self.handle_response)  # catch-all handler for incoming responses
        self.server = osc_server.ThreadingOSCUDPServer((args.ip, args.port + 1), self.dispatcher)

        # Start the server in a separate thread to listen for incoming messages
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True
        self.server_thread.start()

    def set_osc_address(self, address):
        self.osc_address = address

    def message_set(self, fx_channel, state):
        self.client.send_message(self._get_osc_command("set", fx_channel), state)
        print(f"Sent {self.osc_address} with fx_channel {fx_channel} and state {state}")

    def multi_message_set(self, fx_channels, state):
        for fx_channel in fx_channels:
            self.message_set(fx_channel, state)

    def _get_osc_command(self, action, fx_channel):
        return f"{self.namespace}{action}/{self.osc_address}/{fx_channel}"

    def toggle_fx_channels(self, fx_channels):
        """
        Sends a request to get the current states of the provided fx_channels and toggles them once the response is received.
        """
        self.fx_states = {}  # Reset the state dictionary
        for fx_channel in fx_channels:
            # Send request to get the current state for each fx_channel
            self.client.send_message(self._get_osc_command("get", fx_channel), None)

    def handle_response(self, unused_addr, args, fx_channel, current_state):
        """
        Handle the incoming response from the server indicating the current state of the fx_channel.
        This function checks the states of all channels and toggles accordingly.
        """
        self.fx_states[fx_channel] = current_state
        print(f"Received current state {current_state} for fx_channel {fx_channel}")

        # Once we have all the responses for the given channels, process the toggle logic
        if len(self.fx_states) == len(self.fx_states):  # Ensure all channels have responded
            if any(state == 1 for state in self.fx_states.values()):
                # If any of the channels is 1, send 0 to all
                print(f"One or more channels are 1. Setting all channels to 0.")
                self.multi_message_set(self.fx_states.keys(), state=0)
            else:
                # If none of the channels is 1, send 1 to all
                print(f"All channels are 0. Setting all channels to 1.")
                self.multi_message_set(self.fx_states.keys(), state=1)


if __name__ == '__main__':

    osc_client = OSCClient(namespace="/yosc:req/", ip="192.168.0.2", port=49900)

    osc_client.set_osc_address("MIXER:Current/Fx/Fader/On")

    while True:
        state = input("> ")
        # osc_client.multi_message_set(fx_channels=[1, 2], state=state)
        osc_client.toggle_fx_channels([1, 2])

