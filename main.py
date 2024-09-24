import argparse
# # import random
# import time
from pythonosc import udp_client

# from machine import Pin
# import network

#
# class InGPIOPort:
#
#     def __init__(self, port):
#         self.pin = Pin(port, Pin.IN, Pin.PULL_UP)
#
#     def wait_for_signal(self, _callback):
#         while self.pin.value() != 1:
#             pass
#         print("hello")
#
#
# class OutGPIOPort:
#
#     def __init__(self, port):
#         self.pin = Pin(port, Pin.OUT)
#         self.isBlinking = False
#
#     def send_signal_times(self, count, sleep=0.2):
#         for i in range(count):
#             self.pin.value(1)
#             time.sleep(sleep)
#             self.pin.value(0)
#             time.sleep(sleep)
#
#     def on(self):
#         self.pin.value(1)
#
#     def off(self):
#         self.pin.value(0)

class OSCClient:

    def __init__(self, ip: str = "127.0.0.1", port: int = 5005):
        self.ip = ip
        self.port = port
        

        parser = argparse.ArgumentParser()
        parser.add_argument("--ip", default=ip, help="IP address of OSC server")
        parser.add_argument("--port", default=port, type=int, help="Port of OSC server")
        args = parser.parse_args()

        self.client = udp_client.SimpleUDPClient(args.ip, args.port)

    def send_message(self, address: str, message: str):
        self.client.send_message(address, message)



# def connect_wifi():
#     wlan = network.WLAN(network.STA_IF)
#     wlan.active(True)
#     wlan.connect(ssid, password)
#     while wlan.isconnected() == False:
#         print('Waiting for connection...')
#         time.sleep(1)
#     print(wlan.ifconfig())


if __name__ == '__main__':
    # onboardled = OutGPIOPort(18)
    #
    # try:
    #     onboardled.send_signal_times(3)
    #
    #     ssid = 'ILikeToes'
    #     password = 'Jesus7712!xy'
    #
    #     # Indicate Connection
    #     connect_wifi()
    #     onboardled.on()
    #
    #
    # except Exception as e:
    #     onboardled.off()

    oscclient = OSCClient("192.168.0.2", 49900)

    oscclient.send_message(address="/ip", message="Hello World")


    # portIn = InGPIOPort(14)
    #
    # portIn.wait_for_signal(lambda: print("Detected"))

    # client.send_message("/filter", random.random())
