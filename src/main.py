# src/main.py
import sys
import os

# Add the BrickPi3 library to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'BrickPi3', 'Software', 'Python'))

try:
    import brickpi3
    HARDWARE_AVAILABLE = True
    print("✓ BrickPi3 hardware detected")
except ImportError as e:
    print(f"✗ BrickPi3 library not found: {e}")
    HARDWARE_AVAILABLE = False
except Exception as e:
    print(f"✗ Hardware error: {e}")
    HARDWARE_AVAILABLE = False

class Robot:
    def __init__(self):
        if HARDWARE_AVAILABLE:
            try:
                self.bp = brickpi3.BrickPi3()
                self.hardware_connected = True
                print("✓ BrickPi3 initialized successfully")
            except Exception as e:
                print(f"⚠ BrickPi3 hardware not connected: {e}")
                self.hardware_connected = False
                self._create_mock_bp()
        else:
            self.hardware_connected = False
            self._create_mock_bp()
    
    def _create_mock_bp(self):
        """Create a mock BrickPi3 instance for development"""
        print("⚠ Using MockBrickPi3 for development")
        from utils.mock_brickpi import MockBrickPi3
        self.bp = MockBrickPi3()
    
    def setup_motors(self):
        """Configure motor ports"""
        self.MOTOR_LEFT = self.bp.MOTOR_A
        self.MOTOR_RIGHT = self.bp.MOTOR_B
        self.MOTOR_ARM = self.bp.MOTOR_C
        self.MOTOR_GRIPPER = self.bp.MOTOR_D
        
        print("✓ Motors configured")
    
    def move_forward(self, power=50, duration=2):
        """Move forward for specified duration"""
        print(f"Moving forward: power={power}, duration={duration}s")
        self.bp.set_motor_power(self.MOTOR_LEFT, power)
        self.bp.set_motor_power(self.MOTOR_RIGHT, power)
        
        # In real hardware, you'd use time.sleep(duration)
        # For mock, we just log the action
    
    def stop(self):
        """Stop all motors"""
        print("Stopping all motors")
        self.bp.set_motor_power(self.MOTOR_LEFT, 0)
        self.bp.set_motor_power(self.MOTOR_RIGHT, 0)
    
    def cleanup(self):
        """Clean up resources"""
        if self.hardware_connected:
            self.bp.reset_all()
        print("✓ Cleanup completed")

if __name__ == "__main__":
    robot = Robot()
    robot.setup_motors()
    
    try:
        # Test movements
        robot.move_forward(power=50, duration=2)
        robot.stop()
        
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
    finally:
        robot.cleanup()