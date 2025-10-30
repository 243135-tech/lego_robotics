# src/exoskeleton/therapy_session.py
import time
import json

class TherapySession:
    """Manage complete therapy sessions for upper limb rehab"""
    
    def __init__(self, exoskeleton_controller):
        self.exo = exoskeleton_controller
        self.session_data = []
    
    def run_standard_session(self, patient_level="beginner"):
        """
        Run a standard therapy session based on patient level
        Levels: beginner, intermediate, advanced
        """
        protocols = {
            "beginner": {
                "elbow_amplitude": 30,
                "wrist_amplitude": 20,
                "speed": 20,
                "repetitions": 3
            },
            "intermediate": {
                "elbow_amplitude": 60,
                "wrist_amplitude": 45,
                "speed": 30,
                "repetitions": 5
            },
            "advanced": {
                "elbow_amplitude": 90,
                "wrist_amplitude": 70,
                "speed": 40,
                "repetitions": 8
            }
        }
        
        protocol = protocols[patient_level]
        
        print(f"\n{'='*50}")
        print(f"STARTING THERAPY SESSION - {patient_level.upper()} LEVEL")
        print(f"Repetitions: {protocol['repetitions']}")
        print(f"Elbow ROM: {protocol['elbow_amplitude']}°")
        print(f"Wrist ROM: {protocol['wrist_amplitude']}°")
        print(f"Speed: {protocol['speed']}°/sec")
        print(f"{'='*50}")
        
        session_start = time.time()
        
        # Elbow flexion-extension exercises
        for i in range(protocol['repetitions']):
            print(f"\n--- Elbow Flexion/Extension {i+1}/{protocol['repetitions']} ---")
            self.exo.perform_therapy_movement('elbow_flexion', 
                                            protocol['elbow_amplitude'], 
                                            protocol['speed'])
        
        # Wrist pronation-supination exercises  
        for i in range(protocol['repetitions']):
            print(f"\n--- Wrist Pronation {i+1}/{protocol['repetitions']} ---")
            self.exo.perform_therapy_movement('wrist_pronation',
                                            protocol['wrist_amplitude'],
                                            protocol['speed'])
            
        for i in range(protocol['repetitions']):
            print(f"\n--- Wrist Supination {i+1}/{protocol['repetitions']} ---")
            self.exo.perform_therapy_movement('wrist_supination',
                                            protocol['wrist_amplitude'], 
                                            protocol['speed'])
        
        session_duration = time.time() - session_start
        print(f"\n{'='*50}")
        print(f"SESSION COMPLETED in {session_duration:.1f} seconds")
        print(f"{'='*50}")
        
        # Record session data
        self.record_session(patient_level, protocol, session_duration)
    
    def record_session(self, level, protocol, duration):
        """Record therapy session data"""
        session_record = {
            'timestamp': time.time(),
            'patient_level': level,
            'protocol': protocol,
            'duration': duration,
            'final_angles': self.exo.get_joint_angles()
        }
        self.session_data.append(session_record)
        
        # Save to file (in real implementation)
        print(f"Session data recorded: {json.dumps(session_record, indent=2)}")
    
    def get_session_history(self):
        """Return session history"""
        return self.session_data