import RPi.GPIO as GPIO
import time
import osc_library as osc

# Set up GPIO mode and pin
GPIO.setmode(GPIO.BOARD)  # Use BOARD pin numbering (physical pins)
GPIO.setup(8, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Set pin 8 as an input

double_click_time = 0.6  # Max time between clicks to be considered a double-click
single_click_timeout = 0.4  # Time to wait before confirming a single click
last_click_time = 0
click_count = 0
button_pressed = False

# OSC
osc_client = osc.OSCClient(namespace="/yosc:req/", ip="192.168.1.201", port=49900)
osc_client.set_osc_address("MIXER:Current/Fx/Fader/On")

try:
    while True:
        # Read the value of pin 8 (button state)
        value = GPIO.input(8)

        if value == 0:  # Button press detected
            current_time = time.time()

            # If first click
            if click_count == 0:
                click_count = 1
                last_click_time = current_time
                print("First click detected, waiting for second click...")

            # If second click happens within the double-click time
            elif click_count == 1 and (current_time - last_click_time) < double_click_time:
                print("ON (Double-click detected)")
                osc_client.multi_message_set(fx_channels=[1, 2], state=1)
                click_count = 0  # Reset after detecting a double-click

            # Debounce the button
            time.sleep(0.2)

        # Check if it's a single-click after the timeout
        if click_count == 1 and (time.time() - last_click_time) >= single_click_timeout:
            print("OFF (Single-click detected)")
            osc_client.multi_message_set(fx_channels=[1, 2], state=0)
            click_count = 0  # Reset after confirming a single-click

        time.sleep(0.05)  # Small delay to prevent high CPU usage

except KeyboardInterrupt:
    print("Program stopped by user")

finally:
    GPIO.cleanup()  # Clean up GPIO settings when the program exits


try:
    while True:
        # Read the value of pin 8 (button state)
        value = GPIO.input(8)

        if value == 0 and not button_pressed:  # Button press detected (transition from released to pressed)
            button_pressed = True  # Mark that the button is now pressed
            current_time = time.time()

            if click_count == 0:  # First press
                click_count = 1
                last_click_time = current_time
                print("First click detected, waiting for release...")

            elif click_count == 1 and (current_time - last_click_time) < double_click_time:  # Second press within time limit
                print("ON (Double-click detected)")
                osc_client.multi_message_set(fx_channels=[1, 2], state=1)
                click_count = 0  # Reset after detecting a double-click
                button_pressed = False

        if value == 1 and button_pressed:  # Button release detected (transition from pressed to released)
            button_pressed = False  # Mark that the button is now released

            # Check for single click after release if no second click occurs in time
            if click_count == 1 and (time.time() - last_click_time) >= single_click_timeout:
                print("OFF (Single-click detected)")
                osc_client.multi_message_set(fx_channels=[1, 2], state=0)
                click_count = 0  # Reset after confirming a single-click

        time.sleep(0.05)  # Small delay to prevent high CPU usage

except KeyboardInterrupt:
    print("Program stopped by user")

finally:
    GPIO.cleanup()  # Clean up GPIO settings when the program exits
