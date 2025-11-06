
"""
Exoskeleton Flex/Extend Controller (BrickPi3, Ports B & C)

- GUI: set speed (deg/s), angle (deg), reps, and rest (s).
- Buttons: Home (zero encoders), Flex, Extend, Cycle (flex->extend ... reps), Stop.
- Live readout of encoders and battery.
- Safety: clamps speed [10..720] deg/s, angle [1..1440] deg, stop flag, and reset_all on exit.

Run:
  python3 exo_control_gui.py
"""

import threading, time, math, sys
import tkinter as tk
from tkinter import ttk, messagebox

try:
    import brickpi3 as BP
except ImportError as e:
    print("ERROR: brickpi3 library not found. Install with: sudo pip3 install brickpi3")
    raise

DEG2CNT = 1.0  # BrickPi3 encoders are in degrees by default

class ExoController:
    def __init__(self, bp):
        self.bp = bp
        self.stop_flag = threading.Event()
        # Ensure motors are idle to start
        for p in (self.bp.PORT_B, self.bp.PORT_C):
            self.bp.set_motor_power(p, 0)

    # ----- Low-level helpers -----
    def set_speed_dps(self, dps):
        dps = max(10, min(720, int(dps)))
        self.bp.set_motor_limits(self.bp.PORT_B, dps)
        self.bp.set_motor_limits(self.bp.PORT_C, dps)
        return dps

    def get_encoders(self):
        try:
            eB = self.bp.get_motor_encoder(self.bp.PORT_B)
            eC = self.bp.get_motor_encoder(self.bp.PORT_C)
        except IOError:
            eB, eC = float('nan'), float('nan')
        return eB, eC

    def get_battery(self):
        try:
            return self.bp.get_voltage_battery()
        except Exception:
            return float('nan')

    def home(self):
        # Offset both encoders to current position = 0
        self.bp.offset_motor_encoder(self.bp.PORT_B, self.bp.get_motor_encoder(self.bp.PORT_B))
        self.bp.offset_motor_encoder(self.bp.PORT_C, self.bp.get_motor_encoder(self.bp.PORT_C))

    def stop(self):
        self.stop_flag.set()
        for p in (self.bp.PORT_B, self.bp.PORT_C):
            self.bp.set_motor_dps(p, 0)
            self.bp.set_motor_power(p, 0)

    # ----- Motion primitives -----
    def flex(self, angle_deg, dps):
        """Flex: B +angle, C -angle (antagonistic pair)."""
        angle_deg = max(1, min(1440, int(angle_deg)))
        dps = self.set_speed_dps(dps)
        if self.stop_flag.is_set(): return
        self.bp.set_motor_position_relative(self.bp.PORT_B, +angle_deg)
        self.bp.set_motor_position_relative(self.bp.PORT_C, -angle_deg)
        self._wait_until_settled(dps)

    def extend(self, angle_deg, dps):
        """Extend: reverse of flex."""
        angle_deg = max(1, min(1440, int(angle_deg)))
        dps = self.set_speed_dps(dps)
        if self.stop_flag.is_set(): return
        self.bp.set_motor_position_relative(self.bp.PORT_B, -angle_deg)
        self.bp.set_motor_position_relative(self.bp.PORT_C, +angle_deg)
        self._wait_until_settled(dps)

    def cycle(self, angle_deg, dps, reps, rest_s, progress_cb=None):
        """Flex then extend for 'reps' with rest between cycles."""
        reps = max(1, int(reps))
        rest_s = max(0, float(rest_s))
        for i in range(1, reps + 1):
            if self.stop_flag.is_set(): break
            if progress_cb: progress_cb(f"Rep {i}/{reps}: Flex")
            self.flex(angle_deg, dps)
            if self.stop_flag.is_set(): break
            if progress_cb: progress_cb(f"Rep {i}/{reps}: Extend")
            self.extend(angle_deg, dps)
            if self.stop_flag.is_set(): break
            if rest_s > 0 and i < reps:
                if progress_cb: progress_cb(f"Rest {rest_s:.1f}s")
                t0 = time.time()
                while time.time() - t0 < rest_s and not self.stop_flag.is_set():
                    time.sleep(0.05)

    def _wait_until_settled(self, dps):
        """
        Simple completion wait: poll encoders and inferred velocity.
        Consider finished when velocity is low for a short window or timeout.
        """
        t_start = time.time()
        last_eB, last_eC = self.get_encoders()
        stable_time = 0.0
        while not self.stop_flag.is_set():
            time.sleep(0.05)
            eB, eC = self.get_encoders()
            dt = 0.05
            vB = abs((eB - last_eB) / dt) if (not math.isnan(eB) and not math.isnan(last_eB)) else 9999
            vC = abs((eC - last_eC) / dt) if (not math.isnan(eC) and not math.isnan(last_eC)) else 9999
            last_eB, last_eC = eB, eC
            # Consider "settled" when both are slow.
            if vB < max(5, 0.1 * dps) and vC < max(5, 0.1 * dps):
                stable_time += dt
            else:
                stable_time = 0.0
            if stable_time > 0.3:
                break
            if time.time() - t_start > max(2.0, 10.0 + 360.0 / max(10, dps)):
                # Timeout safety
                break

class App(tk.Tk):
    def __init__(self, controller):
        super().__init__()
        self.title("Exoskeleton B+C Controller")
        self.controller = controller
        self._build_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.running_thread = None
        self.after(200, self._refresh_status)

    def _build_ui(self):
        pad = dict(padx=6, pady=6)
        frm = ttk.Frame(self)
        frm.grid(row=0, column=0, sticky="nsew")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        # Inputs
        self.speed_var = tk.StringVar(value="180")   # deg/s
        self.angle_var = tk.StringVar(value="45")    # deg
        self.reps_var  = tk.StringVar(value="5")
        self.rest_var  = tk.StringVar(value="1.0")

        def add_row(r, label, var, suffix):
            ttk.Label(frm, text=label).grid(row=r, column=0, sticky="e", **pad)
            ent = ttk.Entry(frm, textvariable=var, width=8)
            ent.grid(row=r, column=1, sticky="w", **pad)
            ttk.Label(frm, text=suffix).grid(row=r, column=2, sticky="w", **pad)

        add_row(0, "Speed", self.speed_var, "deg/s")
        add_row(1, "Angle", self.angle_var, "deg")
        add_row(2, "Reps",  self.reps_var,  "count")
        add_row(3, "Rest",  self.rest_var,  "s")

        # Buttons
        btns = ttk.Frame(frm)
        btns.grid(row=4, column=0, columnspan=3, **pad)
        ttk.Button(btns, text="Home (Zero Encoders)", command=self.on_home).grid(row=0, column=0, **pad)
        ttk.Button(btns, text="Flex",   command=self.on_flex).grid(row=0, column=1, **pad)
        ttk.Button(btns, text="Extend", command=self.on_extend).grid(row=0, column=2, **pad)
        ttk.Button(btns, text="Cycle",  command=self.on_cycle).grid(row=0, column=3, **pad)
        ttk.Button(btns, text="Stop",   command=self.on_stop).grid(row=0, column=4, **pad)

        # Status
        self.status = tk.StringVar(value="Ready")
        self.battery = tk.StringVar(value="—")
        self.encB = tk.StringVar(value="—")
        self.encC = tk.StringVar(value="—")

        info = ttk.Frame(frm)
        info.grid(row=5, column=0, columnspan=3, sticky="ew", **pad)
        ttk.Label(info, text="Battery:").grid(row=0, column=0, sticky="e")
        ttk.Label(info, textvariable=self.battery).grid(row=0, column=1, sticky="w")
        ttk.Label(info, text="Enc B:").grid(row=0, column=2, sticky="e")
        ttk.Label(info, textvariable=self.encB).grid(row=0, column=3, sticky="w")
        ttk.Label(info, text="Enc C:").grid(row=0, column=4, sticky="e")
        ttk.Label(info, textvariable=self.encC).grid(row=0, column=5, sticky="w")

        ttk.Label(frm, textvariable=self.status, foreground="blue").grid(row=6, column=0, columnspan=3, sticky="w", **pad)

    def _read_inputs(self):
        try:
            dps = float(self.speed_var.get())
            angle = float(self.angle_var.get())
            reps = int(self.reps_var.get())
            rest = float(self.rest_var.get())
        except ValueError:
            messagebox.showerror("Input error", "Please enter numeric values.")
            return None
        return dps, angle, reps, rest

    # Button handlers
    def on_home(self):
        try:
            self.controller.home()
            self.status.set("Encoders zeroed")
        except Exception as e:
            messagebox.showerror("Home error", str(e))

    def _run_in_thread(self, target):
        if self.running_thread and self.running_thread.is_alive():
            self.status.set("Busy… (press Stop to interrupt)")
            return
        self.controller.stop_flag.clear()
        t = threading.Thread(target=target, daemon=True)
        self.running_thread = t
        t.start()

    def on_flex(self):
        vals = self._read_inputs()
        if not vals: return
        dps, angle, *_ = vals
        self._run_in_thread(lambda: self._action_wrapper(self.controller.flex, angle, dps, label="Flex"))

    def on_extend(self):
        vals = self._read_inputs()
        if not vals: return
        dps, angle, *_ = vals
        self._run_in_thread(lambda: self._action_wrapper(self.controller.extend, angle, dps, label="Extend"))

    def on_cycle(self):
        vals = self._read_inputs()
        if not vals: return
        dps, angle, reps, rest = vals
        def run():
            self._set_status("Starting cycle…")
            try:
                self.controller.cycle(angle, dps, reps, rest, progress_cb=self._set_status)
                if not self.controller.stop_flag.is_set():
                    self._set_status("Done")
            except Exception as e:
                self._set_status(f"Error: {e}")
        self._run_in_thread(run)

    def on_stop(self):
        self.controller.stop()
        self._set_status("Stopped")

    def _action_wrapper(self, fn, angle, dps, label="Move"):
        try:
            self._set_status(f"{label}…")
            fn(angle, dps)
            if not self.controller.stop_flag.is_set():
                self._set_status("Done")
        except Exception as e:
            self._set_status(f"Error: {e}")

    def _set_status(self, text):
        # Thread-safe status setter
        self.after(0, lambda: self.status.set(text))

    def _refresh_status(self):
        try:
            bat = self.controller.get_battery()
            eB, eC = self.controller.get_encoders()
            self.battery.set(f"{bat:.2f} V" if not math.isnan(bat) else "—")
            self.encB.set(f"{eB:.1f}°" if not math.isnan(eB) else "—")
            self.encC.set(f"{eC:.1f}°" if not math.isnan(eC) else "—")
        except Exception:
            pass
        self.after(200, self._refresh_status)

    def on_close(self):
        try:
            self.controller.stop()
            self.controller.bp.reset_all()
        except Exception:
            pass
        self.destroy()

def main():
    bp = BP.BrickPi3()
    ctl = ExoController(bp)
    app = App(ctl)
    app.geometry("520x240")
    app.mainloop()

if __name__ == "__main__":
    main()
