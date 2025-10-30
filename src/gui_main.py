# src/gui_main.py
import sys
import os

# Add the current directory and parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, current_dir)
sys.path.insert(0, parent_dir)

# Add BrickPi3 to path
brickpi_path = os.path.join(parent_dir, 'BrickPi3', 'Software', 'Python')
if os.path.exists(brickpi_path):
    sys.path.insert(0, brickpi_path)

try:
    import brickpi3
    HARDWARE_AVAILABLE = True
    print("BrickPi3 hardware detected - REAL MODE")
except ImportError as e:
    HARDWARE_AVAILABLE = False
    print(f"BrickPi3 not available - SIMULATION MODE: {e}")

from exoskeleton.exoskeleton_controller import ExoskeletonController
from gui.exoskeleton_gui import ExoskeletonGUI

def main():
    # Initialize hardware or mock
    if HARDWARE_AVAILABLE:
        try:
            bp = brickpi3.BrickPi3()
            print("Connected to real BrickPi3 hardware")
        except Exception as e:
            from utils.exoskeleton_mock import ExoskeletonMockBrickPi3
            bp = ExoskeletonMockBrickPi3()
            print(f"Using exoskeleton simulation mode: {e}")
    else:
        from utils.exoskeleton_mock import ExoskeletonMockBrickPi3
        bp = ExoskeletonMockBrickPi3()
        print("Running in exoskeleton simulation mode")
    
    # Initialize exoskeleton controller
    exo = ExoskeletonController(bp)
    
    # Start GUI
    print("Starting Exoskeleton GUI...")
    gui = ExoskeletonGUI(exo)
    gui.run()

if __name__ == "__main__":
    main()