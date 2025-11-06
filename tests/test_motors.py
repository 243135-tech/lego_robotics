'''
# test_single_motor.py
import sys
import os
import time

# Add BrickPi3 to path
sys.path.append('/home/pi/lego_robotics/BrickPi3/Software/Python')

try:
    import brickpi3
except ImportError as e:
    print(f"BrickPi3 not available: {e}")
    sys.exit(1)

def test_single_motor():
    bp = brickpi3.BrickPi3()
    
    print("SINGLE MOTOR TEST")
    print("=" * 40)
    print("Make sure the motor is free to move!")
    print("The motor will:")
    print("1. Rotate FORWARD for 2 seconds")
    print("2. Stop for 1 second") 
    print("3. Rotate BACKWARD for 2 seconds")
    print("4. Stop completely")
    print("=" * 40)
    
    # Ask which port the motor is connected to
    port = input("Which port is the motor connected to? (A, B, C, or D): ").upper().strip()
    
    port_map = {
        'A': bp.MOTOR_A,
        'B': bp.MOTOR_B, 
        'C': bp.MOTOR_C,
        'D': bp.MOTOR_D
    }
    
    if port not in port_map:
        print("Invalid port! Please use A, B, C, or D")
        return
    
    motor_port = port_map[port]
    
    try:
        input("Press Enter to start the test...")
        
        # Test 1: Forward rotation
        print(f"\n🔄 Testing FORWARD rotation on Port {port}...")
        bp.set_motor_power(motor_port, 50)  # 50% power forward
        time.sleep(2)
        
        # Stop briefly
        print("⏹️  Stopping...")
        bp.set_motor_power(motor_port, 0)
        time.sleep(1)
        
        # Test 2: Backward rotation  
        print(f"🔄 Testing BACKWARD rotation on Port {port}...")
        bp.set_motor_power(motor_port, -50)  # 50% power backward
        time.sleep(2)
        
        # Final stop
        print("⏹️  Test complete - stopping motor")
        bp.set_motor_power(motor_port, 0)
        
        print("✓ Motor test completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⚠ Test interrupted by user")
    except Exception as e:
        print(f"❌ Motor error: {e}")
    finally:
        # Always ensure motor stops
        bp.set_motor_power(motor_port, 0)
        print("✓ Motor safely stopped")

if __name__ == "__main__":
    test_single_motor()

    '''

import time, brickpi3 as BP
bp = BP.BrickPi3()
try:
    print("Battery:", bp.get_voltage_battery(), "V")
    bp.set_motor_power(bp.PORT_C, 50)  # run forward
    time.sleep(2)
    bp.set_motor_power(bp.PORT_C, -50) # run reverse
    time.sleep(2)
    bp.set_motor_power(bp.PORT_C, 0)   # coast/stop
finally:
    bp.reset_all()