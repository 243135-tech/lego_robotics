# src/utils/mock_brickpi.py
class MockBrickPi3:
    """Mock implementation of BrickPi3 for development without hardware"""
    
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
        print("MockBrickPi3 initialized - Development mode")
        self.motor_power = {1: 0, 2: 0, 3: 0, 4: 0}
        self.motor_position = {1: 0, 2: 0, 3: 0, 4: 0}
    
    def set_motor_power(self, port, power):
        """Set motor power (mock implementation)"""
        if port not in [self.MOTOR_A, self.MOTOR_B, self.MOTOR_C, self.MOTOR_D]:
            raise ValueError(f"Invalid motor port: {port}")
        
        self.motor_power[port] = power
        print(f"Mock: Motor {self._port_name(port)} power set to {power}")
    
    def set_motor_position(self, port, position):
        """Set motor position (mock implementation)"""
        self.motor_position[port] = position
        print(f"Mock: Motor {self._port_name(port)} moving to position {position}")
    
    def set_motor_dps(self, port, dps):
        """Set motor speed in degrees per second (mock implementation)"""
        print(f"Mock: Motor {self._port_name(port)} set to {dps}° per second")
    
    def get_motor_encoder(self, port):
        """Get motor encoder value (mock implementation)"""
        return self.motor_position[port]
    
    def offset_motor_encoder(self, port, position):
        """Offset motor encoder (mock implementation)"""
        self.motor_position[port] = position
        print(f"Mock: Motor {self._port_name(port)} encoder offset to {position}")
    
    def reset_all(self):
        """Reset all motors and sensors (mock implementation)"""
        for port in self.motor_power:
            self.motor_power[port] = 0
        print("Mock: All motors and sensors reset")
    
    def _port_name(self, port):
        """Convert port number to name"""
        port_names = {
            self.MOTOR_A: "A",
            self.MOTOR_B: "B", 
            self.MOTOR_C: "C",
            self.MOTOR_D: "D"
        }
        return port_names.get(port, f"Unknown({port})")