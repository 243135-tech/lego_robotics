LEGO Exoskeleton for Upper Limb Rehabilitation

A Raspberry Pi-based control system for a 3 DOF (Degree of Freedom) LEGO exoskeleton designed for upper limb rehabilitation therapy. This project uses BrickPi3 to control LEGO motors for elbow flexion/extension and wrist rotation movements.

Project Structure

text
lego_robotics/

├── src/
│   ├── exoskeleton/

│   │   ├── __init__.py

│   │   ├── exoskeleton_controller.py  # Main motor control logic

│   │   └── therapy_session.py         # Therapy protocols and session management

│   ├── utils/

│   │   ├── __init__.py

│   │   └── exoskeleton_mock.py        # Mock hardware for development

│   ├── motors/                        # Low-level motor control

│   ├── sensors/                       # Sensor integration

│   └── main.py                        # Entry point

├── tests/                             # Test scripts

├── docs/                              # Documentation

├── BrickPi3/                          # BrickPi3 library

├── requirements.txt

└── README.md

Exoskeleton Specifications

3 DOF Upper Limb Rehabilitation:

Motor A: Elbow Flexion/Extension (Primary)
Motor B: Elbow Flexion/Extension (Secondary - torque support)
Motor C: Wrist Pronation/Supination (Rotation)
Safety Limits:

Elbow: 0° (extended) to 120° (flexed)
Wrist: -90° (supination) to +90° (pronation)
Quick Start

Prerequisites

Raspberry Pi 4
BrickPi3 board
LEGO motors and components
Python 3.7+
Installation

Clone the repository:
bash
git clone https://github.com/your-username/lego-robotics.git
cd lego-robotics
Install BrickPi3 library:
bash
cd BrickPi3/Software/Python
sudo python3 setup.py install
cd ../..
Install Python dependencies:
bash
pip3 install -r requirements.txt
Running Therapy Sessions

Basic Usage

Run the main exoskeleton system:

bash
python3 src/main.py
This will:

Auto-detect BrickPi3 hardware or use simulation mode
Initialize the 3 DOF exoskeleton controller
Run a sample therapy session
Show joint movements and session data
Therapy Session Levels

The system includes three patient levels:

Beginner:

Elbow range: 30°
Wrist range: 20°
Speed: 20°/sec
Repetitions: 3
Intermediate:

Elbow range: 60°
Wrist range: 45°
Speed: 30°/sec
Repetitions: 5
Advanced:

Elbow range: 90°
Wrist range: 70°
Speed: 40°/sec
Repetitions: 8
Manual Joint Control

You can create custom scripts for specific movements:

python
from src.exoskeleton.exoskeleton_controller import ExoskeletonController
from src.utils.exoskeleton_mock import ExoskeletonMockBrickPi3

# Initialize (with or without hardware)
bp = ExoskeletonMockBrickPi3()  # Or real BrickPi3()
exo = ExoskeletonController(bp)

# Control individual joints
exo.move_elbow(45)      # Move elbow to 45 degrees
exo.move_wrist(-30)     # Supinate wrist to -30 degrees
exo.reset_position()    # Return to neutral position

# Run specific therapy movements
exo.perform_therapy_movement('elbow_flexion', amplitude=60, speed=25)
exo.perform_therapy_movement('wrist_pronation', amplitude=45, speed=20)
Complete Therapy Sessions

Run structured therapy sessions:

python
from src.exoskeleton.therapy_session import TherapySession
from src.exoskeleton.exoskeleton_controller import ExoskeletonController

bp = ExoskeletonMockBrickPi3()
exo = ExoskeletonController(bp)
therapy = TherapySession(exo)

# Run different difficulty levels
therapy.run_standard_session("beginner")
therapy.run_standard_session("intermediate") 
therapy.run_standard_session("advanced")

# View session history
history = therapy.get_session_history()
for session in history:
    print(f"Level: {session['patient_level']}, Duration: {session['duration']:.1f}s")
Testing

Run Basic Tests

Test the motor control system:

bash
python3 tests/test_motors.py
Simulation Mode

The system automatically uses simulation mode when:

BrickPi3 hardware is not connected
BrickPi3 library is not installed
Running on non-Raspberry Pi systems
This allows development without physical hardware.

Hardware Testing

When BrickPi3 is connected:

bash
# Enable SPI interface
sudo raspi-config
# Go to Interface Options > SPI > Yes
sudo reboot

# Test hardware detection
python3 -c "import brickpi3; bp = brickpi3.BrickPi3(); print('Hardware detected')"
Key Features

Safety First: Built-in joint limits prevent dangerous movements
Flexible Therapy: Multiple difficulty levels and customizable protocols
Hardware Abstraction: Same code works with real hardware or simulation
Session Tracking: Record and review therapy progress
Modular Design: Easy to extend with new exercises or sensors
File Descriptions

src/main.py: Main application entry point
src/exoskeleton/exoskeleton_controller.py: Core motor control and joint management
src/exoskeleton/therapy_session.py: Therapy protocols and session management
src/utils/exoskeleton_mock.py: Hardware simulation for development
tests/test_motors.py: Basic functionality tests
Development

Adding New Therapy Exercises

Add new movement type in exoskeleton_controller.py:
python
def new_exercise(self, parameters):
    # Implement new exercise logic
    pass
Update therapy protocols in therapy_session.py:
python
protocols = {
    "beginner": {
        # Add new exercise parameters
    }
}
Customizing Safety Limits

Modify joint limits in exoskeleton_controller.py:

python
self.ELBOW_MIN = 0
self.ELBOW_MAX = 120
self.WRIST_MIN = -90
self.WRIST_MAX = 90
Troubleshooting

ModuleNotFoundError:

Ensure all init.py files are present
Check Python path includes src/ directory
BrickPi3 not detected:

Verify SPI interface is enabled
Check physical connections
Run in simulation mode for development
Motor movement issues:

Verify motor port assignments
Check power supply
Review safety limits
Safety Notes

Always test new movements in simulation first
Start with small movement ranges
Monitor patient response carefully
Keep emergency stop procedures ready
Regular maintenance check on mechanical components
