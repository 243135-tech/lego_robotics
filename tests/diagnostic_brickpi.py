# power_check.py
import time
import RPi.GPIO as GPIO

def check_brickpi_power():
    """Check if we can detect BrickPi3 power via GPIO"""
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Try to read a GPIO pin that might be affected by BrickPi3
        GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        state = GPIO.input(4)
        
        print(f"GPIO 4 state: {state}")
        
        if state == GPIO.LOW:
            print("⚠ BrickPi3 might be affecting GPIO - good sign")
        else:
            print("ℹ GPIO not affected - BrickPi3 may not be powered")
            
        GPIO.cleanup()
        
    except Exception as e:
        print(f"GPIO check error: {e}")

if __name__ == "__main__":
    check_brickpi_power()