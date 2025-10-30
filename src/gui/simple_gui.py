# src/gui/simple_gui.py
import tkinter as tk
from tkinter import ttk
import math
import time
import threading

class SimpleExoskeletonGUI:
    def __init__(self, exoskeleton_controller):
        self.exo = exoskeleton_controller
        self.root = tk.Tk()
        self.root.title("LEGO Exoskeleton Rehabilitation Simulator")
        self.root.geometry("900x700")
        
        # Control variables
        self.is_running = False
        self.therapy_thread = None
        
        self.setup_gui()
        
    def setup_gui(self):
        # Create main frames
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        visualization_frame = ttk.Frame(self.root, padding="10")
        visualization_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=2)
        self.root.rowconfigure(0, weight=1)
        
        # Control Panel
        self.setup_control_panel(control_frame)
        
        # Visualization Panel
        self.setup_visualization_panel(visualization_frame)
        
        # Status Panel
        self.setup_status_panel(control_frame)
        
    def setup_control_panel(self, parent):
        # Title
        title_label = ttk.Label(parent, text="Exoskeleton Control Panel", 
                               font=('Arial', 14, 'bold'))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Joint Control Section
        joint_frame = ttk.LabelFrame(parent, text="Joint Control", padding="10")
        joint_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Elbow Control
        ttk.Label(joint_frame, text="Elbow Angle (0°-120°):").grid(row=0, column=0, sticky=tk.W)
        self.elbow_var = tk.IntVar(value=0)
        elbow_scale = ttk.Scale(joint_frame, from_=0, to=120, 
                               variable=self.elbow_var, orient=tk.HORIZONTAL,
                               command=self.on_elbow_scale_move)
        elbow_scale.grid(row=0, column=1, sticky=(tk.W, tk.E))
        self.elbow_label = ttk.Label(joint_frame, text="0°")
        self.elbow_label.grid(row=0, column=2)
        ttk.Button(joint_frame, text="Move Elbow", 
                  command=self.move_elbow_gui).grid(row=0, column=3, padx=(10, 0))
        
        # Wrist Control
        ttk.Label(joint_frame, text="Wrist Angle (-90° to 90°):").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.wrist_var = tk.IntVar(value=0)
        wrist_scale = ttk.Scale(joint_frame, from_=-90, to=90, 
                               variable=self.wrist_var, orient=tk.HORIZONTAL,
                               command=self.on_wrist_scale_move)
        wrist_scale.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(10, 0))
        self.wrist_label = ttk.Label(joint_frame, text="0°")
        self.wrist_label.grid(row=1, column=2, pady=(10, 0))
        ttk.Button(joint_frame, text="Move Wrist", 
                  command=self.move_wrist_gui).grid(row=1, column=3, padx=(10, 0), pady=(10, 0))
        
        # Reset button
        ttk.Button(joint_frame, text="Reset to Neutral", 
                  command=self.reset_position_gui).grid(row=2, column=0, columnspan=4, pady=(10, 0))
        
        # Therapy Session Section
        therapy_frame = ttk.LabelFrame(parent, text="Therapy Sessions", padding="10")
        therapy_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Patient level selection
        ttk.Label(therapy_frame, text="Patient Level:").grid(row=0, column=0, sticky=tk.W)
        self.level_var = tk.StringVar(value="beginner")
        level_combo = ttk.Combobox(therapy_frame, textvariable=self.level_var,
                                  values=["beginner", "intermediate", "advanced"])
        level_combo.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # Therapy buttons
        ttk.Button(therapy_frame, text="Start Therapy Session", 
                  command=self.start_therapy_session).grid(row=1, column=0, pady=(10, 0))
        ttk.Button(therapy_frame, text="Stop Therapy", 
                  command=self.stop_therapy_session).grid(row=1, column=1, pady=(10, 0))
        
        # Custom exercise section
        custom_frame = ttk.LabelFrame(parent, text="Custom Exercise", padding="10")
        custom_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Label(custom_frame, text="Exercise Type:").grid(row=0, column=0, sticky=tk.W)
        self.exercise_var = tk.StringVar(value="elbow_flexion")
        exercise_combo = ttk.Combobox(custom_frame, textvariable=self.exercise_var,
                                     values=["elbow_flexion", "wrist_pronation", "wrist_supination"])
        exercise_combo.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        ttk.Label(custom_frame, text="Amplitude:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        self.amplitude_var = tk.IntVar(value=45)
        ttk.Entry(custom_frame, textvariable=self.amplitude_var, width=10).grid(row=1, column=1, sticky=tk.W, pady=(5, 0))
        
        ttk.Label(custom_frame, text="Speed:").grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        self.speed_var = tk.IntVar(value=25)
        ttk.Entry(custom_frame, textvariable=self.speed_var, width=10).grid(row=2, column=1, sticky=tk.W, pady=(5, 0))
        
        ttk.Button(custom_frame, text="Run Custom Exercise", 
                  command=self.run_custom_exercise).grid(row=3, column=0, columnspan=2, pady=(10, 0))
        
        # Configure column weights
        joint_frame.columnconfigure(1, weight=1)
        therapy_frame.columnconfigure(1, weight=1)
        custom_frame.columnconfigure(1, weight=1)
        parent.columnconfigure(1, weight=1)
        
    def setup_visualization_panel(self, parent):
        # Create a canvas for arm visualization
        self.canvas = tk.Canvas(parent, width=400, height=400, bg='white', relief='sunken')
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Initial visualization
        self.update_visualization()
        
    def setup_status_panel(self, parent):
        status_frame = ttk.LabelFrame(parent, text="Status Information", padding="10")
        status_frame.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # Current angles
        self.angles_label = ttk.Label(status_frame, text="Current Angles: Elbow: 0°, Wrist: 0°")
        self.angles_label.grid(row=0, column=0, sticky=tk.W)
        
        # Safety status
        self.safety_label = ttk.Label(status_frame, text="Safety: Within Limits")
        self.safety_label.grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        # Therapy status
        self.therapy_label = ttk.Label(status_frame, text="Therapy: Not Running")
        self.therapy_label.grid(row=2, column=0, sticky=tk.W, pady=(5, 0))
        
        # Session info
        self.session_label = ttk.Label(status_frame, text="Sessions Completed: 0")
        self.session_label.grid(row=3, column=0, sticky=tk.W, pady=(5, 0))
        
        # Motor status
        self.motor_label = ttk.Label(status_frame, text="Motors: A(0°) B(0°) C(0°)")
        self.motor_label.grid(row=4, column=0, sticky=tk.W, pady=(5, 0))
        
        parent.columnconfigure(0, weight=1)
        
    def draw_arm(self, elbow_angle, wrist_angle):
        self.canvas.delete("all")
        
        # Canvas dimensions
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        # Center point (shoulder)
        center_x = width // 4
        center_y = height // 2
        
        # Scale factor
        scale = min(width, height) / 300
        
        # Convert angles to radians
        elbow_rad = math.radians(elbow_angle)
        wrist_rad = math.radians(wrist_angle)
        
        # Upper arm (from shoulder to elbow)
        upper_arm_length = 80 * scale
        elbow_x = center_x + upper_arm_length * math.sin(elbow_rad)
        elbow_y = center_y - upper_arm_length * math.cos(elbow_rad)
        
        # Lower arm (from elbow to wrist)
        lower_arm_length = 70 * scale
        wrist_x = elbow_x + lower_arm_length * math.sin(elbow_rad + wrist_rad)
        wrist_y = elbow_y - lower_arm_length * math.cos(elbow_rad + wrist_rad)
        
        # Draw arm segments
        self.canvas.create_line(center_x, center_y, elbow_x, elbow_y, 
                               width=8, fill='blue', tags="arm")
        self.canvas.create_line(elbow_x, elbow_y, wrist_x, wrist_y, 
                               width=6, fill='red', tags="arm")
        
        # Draw joints
        self.canvas.create_oval(center_x-8, center_y-8, center_x+8, center_y+8, 
                               fill='black', tags="joint")
        self.canvas.create_oval(elbow_x-6, elbow_y-6, elbow_x+6, elbow_y+6, 
                               fill='black', tags="joint")
        self.canvas.create_oval(wrist_x-5, wrist_y-5, wrist_x+5, wrist_y+5, 
                               fill='black', tags="joint")
        
        # Add labels
        self.canvas.create_text(center_x, center_y-20, text="Shoulder", tags="label")
        self.canvas.create_text(elbow_x, elbow_y-15, text="Elbow", tags="label")
        self.canvas.create_text(wrist_x, wrist_y-10, text="Wrist", tags="label")
        
        # Add angle labels
        self.canvas.create_text(center_x + 100, 30, 
                               text=f"Elbow: {elbow_angle}°\nWrist: {wrist_angle}°",
                               font=('Arial', 12, 'bold'), tags="label")
        
    def on_elbow_scale_move(self, value):
        self.elbow_label.config(text=f"{float(value):.0f}°")
        
    def on_wrist_scale_move(self, value):
        self.wrist_label.config(text=f"{float(value):.0f}°")
        
    def move_elbow_gui(self):
        target_angle = self.elbow_var.get()
        self.exo.move_elbow(target_angle)
        self.update_display()
        
    def move_wrist_gui(self):
        target_angle = self.wrist_var.get()
        self.exo.move_wrist(target_angle)
        self.update_display()
        
    def reset_position_gui(self):
        self.exo.reset_position()
        self.elbow_var.set(0)
        self.wrist_var.set(0)
        self.elbow_label.config(text="0°")
        self.wrist_label.config(text="0°")
        self.update_display()
        
    def start_therapy_session(self):
        if self.is_running:
            return
            
        self.is_running = True
        level = self.level_var.get()
        
        def run_therapy():
            from src.exoskeleton.therapy_session import TherapySession
            therapy = TherapySession(self.exo)
            therapy.run_standard_session(level)
            self.is_running = False
            self.update_display()
            
        self.therapy_thread = threading.Thread(target=run_therapy)
        self.therapy_thread.daemon = True
        self.therapy_thread.start()
        self.therapy_label.config(text=f"Therapy: Running {level} session")
        
    def stop_therapy_session(self):
        self.is_running = False
        self.therapy_label.config(text="Therapy: Stopped by user")
        
    def run_custom_exercise(self):
        exercise = self.exercise_var.get()
        amplitude = self.amplitude_var.get()
        speed = self.speed_var.get()
        
        def run_exercise():
            self.exo.perform_therapy_movement(exercise, amplitude, speed)
            self.update_display()
            
        exercise_thread = threading.Thread(target=run_exercise)
        exercise_thread.daemon = True
        exercise_thread.start()
        
    def update_visualization(self):
        angles = self.exo.get_joint_angles()
        self.draw_arm(angles['elbow'], angles['wrist'])
        
    def update_display(self):
        # Update visualization
        self.update_visualization()
        
        # Update status labels
        angles = self.exo.get_joint_angles()
        self.angles_label.config(text=f"Current Angles: Elbow: {angles['elbow']}°, Wrist: {angles['wrist']}°")
        
        # Update safety status
        elbow_ok = self.exo.ELBOW_MIN <= angles['elbow'] <= self.exo.ELBOW_MAX
        wrist_ok = self.exo.WRIST_MIN <= angles['wrist'] <= self.exo.WRIST_MAX
        
        if elbow_ok and wrist_ok:
            self.safety_label.config(text="Safety: Within Limits", foreground="green")
        else:
            self.safety_label.config(text="Safety: LIMIT EXCEEDED!", foreground="red")
            
        # Update motor status
        motor_a = self.exo.bp.get_motor_encoder(self.exo.bp.MOTOR_A)
        motor_b = self.exo.bp.get_motor_encoder(self.exo.bp.MOTOR_B)
        motor_c = self.exo.bp.get_motor_encoder(self.exo.bp.MOTOR_C)
        self.motor_label.config(text=f"Motors: A({motor_a:.0f}°) B({motor_b:.0f}°) C({motor_c:.0f}°)")
        
    def run(self):
        # Start periodic updates
        def update_loop():
            self.update_display()
            self.root.after(100, update_loop)  # Update every 100ms
            
        self.root.after(100, update_loop)
        self.root.mainloop()