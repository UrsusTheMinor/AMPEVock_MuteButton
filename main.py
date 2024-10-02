from cgi import print_exception

import RPi.GPIO as GPIO
import time
import osc_library as osc
import json
import os

# File input
file_path = "/var/www/sites/config/settings.txt"

last_modified_time = None

# Function to read the JSON file and extract values into variables
def read_network_config(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)

    # Extract values from the JSON object
    network_mode = data.get("network_mode")
    ip_address = data.get("ip_address")
    gateway = data.get("gateway")
    subnet_mask = data.get("subnet_mask")
    mixer_address = data.get("mixer_address")
    fx1 = data.get("fx1")
    fx2 = data.get("fx2")

    return network_mode, ip_address, gateway, subnet_mask, mixer_address, fx1, fx2

network_mode, ip_address, gateway, subnet_mask, mixer_address, fx1, fx2 = read_network_config(file_path)

fx_channels = []
if bool(fx1):
    fx_channels.append(fx1)
if bool(fx2):
    fx_channels.append(fx2)

# Set up GPIO mode and pin
GPIO.setmode(GPIO.BOARD)  # Use BOARD pin numbering (physical pins)
GPIO.setup(8, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Set pin 8 as an input

PRESS_UNTIL_TOGGLE = 0.8

# OSC
osc_client = osc.OSCClient(namespace="/yosc:req/", ip=mixer_address, port=49900)
osc_client.set_osc_address("MIXER:Current/Fx/Fader/On")

DEFAULT_VALUE = GPIO.input(8)
CHECKED_VALUE = 1 if DEFAULT_VALUE == 0 else 0





try:
    while True:
        current_modified_time = os.path.getmtime(file_path)

        if last_modified_time is None or current_modified_time != last_modified_time:
            # Update last modified time
            last_modified_time = current_modified_time

            # Read the file and update the variables
            network_mode, ip_address, gateway, subnet_mask, mixer_address, fx1, fx2 = read_network_config(file_path)

            osc_client = osc.OSCClient(namespace="/yosc:req/", ip=mixer_address, port=49900)

            fx_channels = []
            if bool(fx1):
                fx_channels.append(fx1)
            if bool(fx2):
                fx_channels.append(fx2)

        if GPIO.input(8) == CHECKED_VALUE:  # Check if the button is pressed
            start_time = time.time()  # Record the time when button is pressed
            while GPIO.input(8) == CHECKED_VALUE:  # Wait until the button is released
                if (time.time() - start_time) > PRESS_UNTIL_TOGGLE:
                    break
            press_duration = time.time() - start_time  # Calculate how long the button was pressed

            if press_duration < PRESS_UNTIL_TOGGLE:
                print("off")  # Button pressed for less than 1 second
                osc_client.multi_message_set(fx_channels=fx_channels, state=0)
            else:
                print("on")  # Button pressed for more than 1 second
                osc_client.multi_message_set(fx_channels=fx_channels, state=1)

            while GPIO.input(8) == CHECKED_VALUE:  # Wait until the button is released
                pass
        time.sleep(0.1)  # Add a small delay to avoid CPU overload

except KeyboardInterrupt:
    GPIO.cleanup()  # Clean up GPIO when program is terminated
except FileNotFoundError:
    print("File not found. Retrying...")

