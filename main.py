import RPi.GPIO as GPIO
import time
import osc_library as osc

# Set up GPIO mode and pin
GPIO.setmode(GPIO.BOARD)  # Use BOARD pin numbering (physical pins)
GPIO.setup(8, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)  # Set pin 8 as an input

PRESS_UNTIL_TOGGLE = 1

# OSC
osc_client = osc.OSCClient(namespace="/yosc:req/", ip="192.168.1.200", port=49900)
osc_client.set_osc_address("MIXER:Current/Fx/Fader/On")


try:
    while True:
        if GPIO.input(8) == GPIO.HIGH:  # Check if the button is pressed
            start_time = time.time()  # Record the time when button is pressed
            while GPIO.input(8) == GPIO.HIGH:  # Wait until the button is released
                pass
            press_duration = time.time() - start_time  # Calculate how long the button was pressed

            if press_duration < PRESS_UNTIL_TOGGLE:
                print("off")  # Button pressed for less than 1 second
                osc_client.multi_message_set(fx_channels=[1, 2], state=0)
            else:
                print("on")  # Button pressed for more than 1 second
                osc_client.multi_message_set(fx_channels=[1, 2], state=1)

        time.sleep(0.1)  # Add a small delay to avoid CPU overload

except KeyboardInterrupt:
    GPIO.cleanup()  # Clean up GPIO when program is terminated

