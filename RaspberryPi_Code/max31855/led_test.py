import RPi.GPIO as GPIO
import time

# Define the GPIO pin for the LED
LED_PIN = 17  

# Setup GPIO
GPIO.setmode(GPIO.BCM)  # Use Broadcom (BCM) numbering
GPIO.setup(LED_PIN, GPIO.OUT)  # Set LED_PIN as an output

try:
    while True:
        GPIO.output(LED_PIN, GPIO.HIGH)  # Turn LED ON
        time.sleep(1)  # Wait 1 second
        GPIO.output(LED_PIN, GPIO.LOW)  # Turn LED OFF
        time.sleep(1)  # Wait 1 second

except KeyboardInterrupt:
    print("Exiting program...")
    GPIO.cleanup()  # Reset GPIO settings before exiting
