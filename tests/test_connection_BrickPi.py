# test_basic.py
import sys
import os
import time

# Add BrickPi3 to path
sys.path.append('/home/pi/lego_arm/BrickPi3/Software/Python')

try:
    import brickpi3
    print("✓ BrickPi3 library imported successfully")
    
    # Try to create BrickPi3 instance
    bp = brickpi3.BrickPi3()
    print("✓ BrickPi3 object created")
    
    # Test basic communication
    manufacturer = bp.get_manufacturer()
    board = bp.get_board()
    firmware = bp.get_version_firmware()
    
    print(f"✓ Hardware detected:")
    print(f"  Manufacturer: {manufacturer}")
    print(f"  Board: {board}")
    print(f"  Firmware: {firmware}")
    
except Exception as e:
    print(f"✗ Error: {e}")