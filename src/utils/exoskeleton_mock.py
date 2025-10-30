# src/utils/exoskeleton_mock.py
class ExoskeletonMockBrickPi3:
    """Enhanced mock specifically for exoskeleton simulation"""
    
    MOTOR_A = 1  # Elbow primary
    MOTOR_B = 2  # Elbow secondary  
    MOTOR_C = 3  # Wrist rotation
    MOTOR_D = 4  # Unused
    
    def __init__(self):
        print("Exoskeleton Mock BrickPi3 Initialized")
        self.motor_positions = {1: 0, 2: 0, 3: 0, 4: 0}
        self.motor_power = {1: 0, 2: 0, 3: 0, 4: 0}
    
    def set_motor_power(self, port, power):
        self.motor_power[port] = power
        motor_name = self._get_motor_name(port)
        print(f"EXOSKELETON MOCK: {motor_name} power set to {power}")
    
    def set_motor_position(self, port, position):
        self.motor_positions[port] = position
        motor_name = self._get_motor_name(port)
        print(f"EXOSKELETON MOCK: {motor_name} moving to position {position}°")
    
    def set_motor_dps(self, port, dps):
        motor_name = self._get_motor_name(port)
        print(f"EXOSKELETON MOCK: {motor_name} speed set to {dps}° per second")
    
    def get_motor_encoder(self, port):
        return self.motor_positions[port]
    
    def reset_all(self):
        print("EXOSKELETON MOCK: All motors reset to zero")
        for port in self.motor_positions:
            self.motor_positions[port] = 0
            self.motor_power[port] = 0
    
    def _get_motor_name(self, port):
        names = {
            self.MOTOR_A: "ELBOW_PRIMARY",
            self.MOTOR_B: "ELBOW_SECONDARY", 
            self.MOTOR_C: "WRIST_ROTATION",
            self.MOTOR_D: "MOTOR_D"
        }
        return names.get(port, f"UNKNOWN({port})")