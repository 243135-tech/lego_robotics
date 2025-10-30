# src/exoskeleton/exoskeleton_controller.py
import time
import math

class ExoskeletonController:
    """
    3 DOF Upper Limb Exoskeleton Controller
    - Motor A: Elbow Flexion/Extension (primary)
    - Motor B: Elbow Flexion/Extension (secondary - for torque/support)
    - Motor C: Wrist Pronation/Supination (rotation)
    """
    
    def __init__(self, brickpi_instance):
        self.bp = brickpi_instance
        self.setup_motors()
        
        # Exoskeleton parameters
        self.elbow_angle = 0  # degrees (0 = extended, 90 = flexed)
        self.wrist_angle = 0  # degrees (0 = neutral, +90 = pronation, -90 = supination)
        
        # Safety limits (degrees)
        self.ELBOW_MIN = 0
        self.ELBOW_MAX = 120
        self.WRIST_MIN = -90
        self.WRIST_MAX = 90
        
        # Movement parameters
        self.movement_speed = 30  # degrees per second
        
        print("Exoskeleton Controller Initialized")
        print(f"Safety limits - Elbow: {self.ELBOW_MIN}° to {self.ELBOW_MAX}°")
        print(f"Safety limits - Wrist: {self.WRIST_MIN}° to {self.WRIST_MAX}°")
    
    def setup_motors(self):
        """Assign motors to exoskeleton joints"""
        self.ELBOW_MOTOR_PRIMARY = self.bp.MOTOR_A    # Main elbow flexion
        self.ELBOW_MOTOR_SECONDARY = self.bp.MOTOR_B   # Support elbow flexion  
        self.WRIST_MOTOR = self.bp.MOTOR_C             # Wrist rotation
        
        print("Motor assignments:")
        print("  - Elbow (primary): Motor A")
        print("  - Elbow (secondary): Motor B") 
        print("  - Wrist rotation: Motor C")
    
    def move_elbow(self, target_angle, speed=None):
        """
        Move elbow to specific angle
        target_angle: degrees (0 = extended, 90 = flexed)
        """
        if speed is None:
            speed = self.movement_speed
            
        # Safety check
        target_angle = max(self.ELBOW_MIN, min(self.ELBOW_MAX, target_angle))
        
        print(f"Moving elbow from {self.elbow_angle}° to {target_angle}°")
        
        # Calculate movement parameters
        angle_diff = target_angle - self.elbow_angle
        direction = 1 if angle_diff > 0 else -1
        duration = abs(angle_diff) / speed
        
        # Simulate movement (in real hardware, this would use position control)
        print(f"  Elbow movement: {abs(angle_diff)}° at {speed}°/sec")
        print(f"  Estimated duration: {duration:.1f} seconds")
        
        # Update current angle
        self.elbow_angle = target_angle
        
        # In real hardware, you'd use:
        # self.bp.set_motor_position(self.ELBOW_MOTOR_PRIMARY, target_angle)
        # self.bp.set_motor_position(self.ELBOW_MOTOR_SECONDARY, target_angle)
    
    def move_wrist(self, target_angle, speed=None):
        """
        Move wrist to specific rotation angle
        target_angle: degrees (0 = neutral, + = pronation, - = supination)
        """
        if speed is None:
            speed = self.movement_speed
            
        # Safety check
        target_angle = max(self.WRIST_MIN, min(self.WRIST_MAX, target_angle))
        
        print(f"Moving wrist from {self.wrist_angle}° to {target_angle}°")
        
        # Calculate movement parameters
        angle_diff = target_angle - self.wrist_angle
        direction = 1 if angle_diff > 0 else -1
        duration = abs(angle_diff) / speed
        
        print(f"  Wrist rotation: {abs(angle_diff)}° at {speed}°/sec")
        print(f"  Estimated duration: {duration:.1f} seconds")
        
        # Update current angle
        self.wrist_angle = target_angle
        
        # In real hardware:
        # self.bp.set_motor_position(self.WRIST_MOTOR, target_angle)
    
    def perform_therapy_movement(self, movement_type, amplitude=45, speed=25):
        """
        Perform common therapy movements
        movement_type: 'elbow_flexion', 'wrist_pronation', 'wrist_supination'
        amplitude: range of motion in degrees
        speed: movement speed in degrees/second
        """
        print(f"\n--- Starting {movement_type} therapy ---")
        print(f"Amplitude: {amplitude}°, Speed: {speed}°/sec")
        
        if movement_type == 'elbow_flexion':
            start_angle = 0
            end_angle = amplitude
            self.move_elbow(end_angle, speed)
            time.sleep(1)  # Hold position
            self.move_elbow(start_angle, speed)
            
        elif movement_type == 'wrist_pronation':
            start_angle = 0
            end_angle = amplitude
            self.move_wrist(end_angle, speed)
            time.sleep(1)
            self.move_wrist(start_angle, speed)
            
        elif movement_type == 'wrist_supination':
            start_angle = 0
            end_angle = -amplitude
            self.move_wrist(end_angle, speed)
            time.sleep(1)
            self.move_wrist(start_angle, speed)
        
        print(f"--- {movement_type} therapy completed ---")
    
    def get_joint_angles(self):
        """Return current joint angles"""
        return {
            'elbow': self.elbow_angle,
            'wrist': self.wrist_angle
        }
    
    def reset_position(self):
        """Return to neutral position"""
        print("Resetting to neutral position...")
        self.move_elbow(0)
        self.move_wrist(0)
        print("Reset complete")
    
    def set_safety_limits(self, elbow_min=0, elbow_max=120, wrist_min=-90, wrist_max=90):
        """Update safety limits"""
        self.ELBOW_MIN = elbow_min
        self.ELBOW_MAX = elbow_max
        self.WRIST_MIN = wrist_min
        self.WRIST_MAX = wrist_max
        print(f"Safety limits updated: Elbow({elbow_min}°-{elbow_max}°), Wrist({wrist_min}°-{wrist_max}°)")