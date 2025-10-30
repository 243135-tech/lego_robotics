# src/gui_main.py
import sys
import os

# Add the current directory and parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, current_dir)
sys.path.insert(0, parent_dir)

from src.utils.advanced_mock import AdvancedBrickPi3Mock
from src.exoskeleton.exoskeleton_controller import ExoskeletonController

def main():
    # Initialize with advanced mock (no hardware required)
    bp = AdvancedBrickPi3Mock()
    
    # Initialize exoskeleton controller
    exo = ExoskeletonController(bp)
    
    # Start GUI
    try:
        from src.gui.simple_gui import SimpleExoskeletonGUI
        print("Starting Exoskeleton GUI...")
        gui = SimpleExoskeletonGUI(exo)
        gui.run()
    except ImportError as e:
        print(f"GUI not available: {e}")
        print("Make sure Tkinter is installed")
    except Exception as e:
        print(f"Error starting GUI: {e}")

if __name__ == "__main__":
    main()