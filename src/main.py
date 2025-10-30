# src/main.py
import sys
import os
import time

# Add the current directory and parent directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, current_dir)
sys.path.insert(0, parent_dir)

# Add BrickPi3 to path
brickpi_path = os.path.join(parent_dir, 'BrickPi3', 'Software', 'Python')
if os.path.exists(brickpi_path):
    sys.path.insert(0, brickpi_path)

try:
    import brickpi3
    HARDWARE_AVAILABLE = True
    print("✓ BrickPi3 hardware detected - REAL MODE")
except ImportError as e:
    HARDWARE_AVAILABLE = False
    print(f"⚠ BrickPi3 not available - SIMULATION MODE: {e}")

# Now import our custom modules
try:
    from exoskeleton.exoskeleton_controller import ExoskeletonController
    from exoskeleton.therapy_session import TherapySession
    print("✓ Exoskeleton modules imported successfully")
except ImportError as e:
    print(f"✗ Error importing exoskeleton modules: {e}")
    print("Current Python path:")
    for path in sys.path:
        print(f"  {path}")
    sys.exit(1)

def main():
    # Initialize hardware or mock
    if HARDWARE_AVAILABLE:
        try:
            bp = brickpi3.BrickPi3()
            print("✓ Connected to real BrickPi3 hardware")
        except Exception as e:
            from utils.exoskeleton_mock import ExoskeletonMockBrickPi3
            bp = ExoskeletonMockBrickPi3()
            print(f"⚠ Using exoskeleton simulation mode: {e}")
    else:
        from utils.exoskeleton_mock import ExoskeletonMockBrickPi3
        bp = ExoskeletonMockBrickPi3()
        print("✓ Running in exoskeleton simulation mode")
    
    # Initialize exoskeleton controller
    exo = ExoskeletonController(bp)
    therapy = TherapySession(exo)
    
    try:
        # Test individual movements
        print("\n1. Testing individual joint movements:")
        exo.move_elbow(45)
        exo.move_wrist(30)
        time.sleep(1)
        
        exo.move_elbow(90)
        exo.move_wrist(-30)
        time.sleep(1)
        
        # Run therapy sessions
        print("\n2. Running therapy sessions:")
        therapy.run_standard_session("beginner")
        
        print("\n3. Session summary:")
        history = therapy.get_session_history()
        for i, session in enumerate(history):
            print(f"Session {i+1}: {session['patient_level']} level, {session['duration']:.1f}s")
        
        # Return to neutral
        print("\n4. Returning to neutral position:")
        exo.reset_position()
        
    except KeyboardInterrupt:
        print("\n\nTherapy session interrupted by user")
    finally:
        # Safety cleanup
        if HARDWARE_AVAILABLE:
            try:
                bp.reset_all()
            except:
                pass
        print("✓ Exoskeleton system shutdown complete")

if __name__ == "__main__":
    main()