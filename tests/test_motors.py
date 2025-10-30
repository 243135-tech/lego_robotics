# tests/test_motors.py
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.main import Robot

def test_basic_movements():
    """Test basic robot movements"""
    robot = Robot()
    robot.setup_motors()
    
    print("Testing basic movements...")
    
    # Test sequence
    movements = [
        ("Forward", lambda: robot.move_forward(50, 1)),
        ("Stop", robot.stop),
        ("Backward", lambda: robot.move_forward(-50, 1)),
        ("Stop", robot.stop),
        ("Left turn", lambda: robot.bp.set_motor_power(robot.MOTOR_LEFT, -30)),
        ("Right turn", lambda: robot.bp.set_motor_power(robot.MOTOR_RIGHT, -30)),
    ]
    
    for name, movement in movements:
        print(f"Testing: {name}")
        movement()
    
    robot.cleanup()
    print("✓ All tests completed")

if __name__ == "__main__":
    test_basic_movements()