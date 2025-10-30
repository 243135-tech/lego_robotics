# src/motors/motor_controller.py
import time

class MotorController:
    def __init__(self, brickpi_instance):
        self.bp = brickpi_instance
        
        # Define motor assignments
        self.left_motor = self.bp.MOTOR_A
        self.right_motor = self.bp.MOTOR_B
        self.arm_motor = self.bp.MOTOR_C
        self.gripper_motor = self.bp.MOTOR_D
        
    def tank_drive(self, left_power, right_power):
        """Tank drive style movement"""
        self.bp.set_motor_power(self.left_motor, left_power)
        self.bp.set_motor_power(self.right_motor, right_power)
    
    def move_forward(self, power=50, duration=None):
        """Move forward"""
        self.tank_drive(power, power)
        if duration:
            time.sleep(duration)
            self.stop()
    
    def move_backward(self, power=50, duration=None):
        """Move backward"""
        self.tank_drive(-power, -power)
        if duration:
            time.sleep(duration)
            self.stop()
    
    def turn_left(self, power=30, duration=None):
        """Turn left (spot turn)"""
        self.tank_drive(-power, power)
        if duration:
            time.sleep(duration)
            self.stop()
    
    def turn_right(self, power=30, duration=None):
        """Turn right (spot turn)"""
        self.tank_drive(power, -power)
        if duration:
            time.sleep(duration)
            self.stop()
    
    def stop(self):
        """Stop all drive motors"""
        self.tank_drive(0, 0)