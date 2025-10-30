# src/utils/advanced_mock.py
import time

class AdvancedBrickPi3Mock:
    """
    Advanced mock BrickPi3 that fully simulates the hardware interface
    without requiring spidev or any hardware dependencies
    """
    
    # Motor ports
    MOTOR_A = 1
    MOTOR_B = 2
    MOTOR_C = 3
    MOTOR_D = 4
    
    # Sensor ports
    PORT_1 = 1
    PORT_2 = 2
    PORT_3 = 3
    PORT_4 = 4
    
    def __init__(self):
        print("Advanced BrickPi3 Mock Initialized - No hardware required")
        self.motor_position = {1: 0, 2: 0, 3: 0, 4: 0}
        self.motor_power = {1: 0, 2: 0, 3: 0, 4: 0}
        self.motor_dps = {1: 0, 2: 0, 3: 0, 4: 0}  # degrees per second
        self.is_running = True
        
    def set_motor_power(self, port, power):
        """Set motor power (-100 to 100)"""
        if port not in [self.MOTOR_A, self.MOTOR_B, self.MOTOR_C, self.MOTOR_D]:
            raise ValueError(f"Invalid motor port: {port}")
        
        power = max(-100, min(100, power))  # Clamp power
        self.motor_power[port] = power
        
        motor_name = self._get_motor_name(port)
        print(f"MOCK: {motor_name} power set to {power}")
        
    def set_motor_position(self, port, position):
        """Set motor target position"""
        if port not in [self.MOTOR_A, self.MOTOR_B, self.MOTOR_C, self.MOTOR_D]:
            raise ValueError(f"Invalid motor port: {port}")
        
        self.motor_position[port] = position
        motor_name = self._get_motor_name(port)
        print(f"MOCK: {motor_name} moving to position {position}")
    
    def set_motor_dps(self, port, dps):
        """Set motor speed in degrees per second"""
        if port not in [self.MOTOR_A, self.MOTOR_B, self.MOTOR_C, self.MOTOR_D]:
            raise ValueError(f"Invalid motor port: {port}")
        
        self.motor_dps[port] = dps
        motor_name = self._get_motor_name(port)
        print(f"MOCK: {motor_name} speed set to {dps}° per second")
    
    def get_motor_encoder(self, port):
        """Get motor encoder value"""
        if port not in [self.MOTOR_A, self.MOTOR_B, self.MOTOR_C, self.MOTOR_D]:
            raise ValueError(f"Invalid motor port: {port}")
        
        return self.motor_position[port]
    
    def offset_motor_encoder(self, port, position):
        """Offset motor encoder"""
        if port not in [self.MOTOR_A, self.MOTOR_B, self.MOTOR_C, self.MOTOR_D]:
            raise ValueError(f"Invalid motor port: {port}")
        
        self.motor_position[port] = position
        motor_name = self._get_motor_name(port)
        print(f"MOCK: {motor_name} encoder offset to {position}")
    
    def reset_all(self):
        """Reset all motors and sensors"""
        print("MOCK: All motors and sensors reset")
        for port in self.motor_position:
            self.motor_position[port] = 0
            self.motor_power[port] = 0
            self.motor_dps[port] = 0
    
    def get_manufacturer(self):
        """Get manufacturer info"""
        return "Dexter Industries (MOCK)"
    
    def get_board(self):
        """Get board info"""
        return "BrickPi3 (MOCK)"
    
    def get_version_firmware(self):
        """Get firmware version"""
        return "1.4.0 (MOCK)"
    
    def set_sensor_type(self, port, sensor_type):
        """Set sensor type (mock implementation)"""
        print(f"MOCK: Sensor port {port} set to type {sensor_type}")
    
    def get_sensor(self, port):
        """Get sensor value (mock implementation)"""
        return 0
    
    def _get_motor_name(self, port):
        """Convert port number to name"""
        port_names = {
            self.MOTOR_A: "MOTOR_A",
            self.MOTOR_B: "MOTOR_B", 
            self.MOTOR_C: "MOTOR_C",
            self.MOTOR_D: "MOTOR_D"
        }
        return port_names.get(port, f"UNKNOWN({port})")