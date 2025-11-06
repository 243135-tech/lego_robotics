#!/usr/bin/env python3
"""
Two-motor elbow cycle (BrickPi3)

- Ports: B and C
- Flex = B +angle, C -angle
- Extend = B -angle, C +angle
- Tunables: speed (deg/s), angle (deg), reps, rest (s)

Run:
  python3 elbow_cycle.py --speed 180 --angle 45 --reps 5 --rest 1.0
"""

import time
import math
import argparse
import brickpi3 as BP

def wait_until_settled(bp, dps, timeout_s=20.0):
    """Poll encoders; consider done when both motors slow down."""
    lastB = bp.get_motor_encoder(bp.PORT_B)
    lastC = bp.get_motor_encoder(bp.PORT_C)
    t0 = time.time()
    stable = 0.0
    while True:
        time.sleep(0.05)
        eB = bp.get_motor_encoder(bp.PORT_B)
        eC = bp.get_motor_encoder(bp.PORT_C)
        vB = abs(eB - lastB) / 0.05
        vC = abs(eC - lastC) / 0.05
        lastB, lastC = eB, eC
        if vB < max(5, 0.1*dps) and vC < max(5, 0.1*dps):
            stable += 0.05
            if stable >= 0.3:
                break
        else:
            stable = 0.0
        if time.time() - t0 > timeout_s:
            break

def flex(bp, angle_deg, dps):
    angle = int(max(1, min(1440, angle_deg)))
    bp.set_motor_limits(bp.PORT_B, dps)
    bp.set_motor_limits(bp.PORT_C, dps)
    bp.set_motor_position_relative(bp.PORT_B, +angle)
    bp.set_motor_position_relative(bp.PORT_C, -angle)
    wait_until_settled(bp, dps)

def extend(bp, angle_deg, dps):
    angle = int(max(1, min(1440, angle_deg)))
    bp.set_motor_limits(bp.PORT_B, dps)
    bp.set_motor_limits(bp.PORT_C, dps)
    bp.set_motor_position_relative(bp.PORT_B, -angle)
    bp.set_motor_position_relative(bp.PORT_C, +angle)
    wait_until_settled(bp, dps)

def main():
    ap = argparse.ArgumentParser(description="Elbow flex/extend cycle on B+C")
    ap.add_argument("--speed", "-s", type=float, default=180, help="speed (deg/s) 10..720")
    ap.add_argument("--angle", "-a", type=float, default=45, help="movement angle (deg)")
    ap.add_argument("--reps", "-r",   type=int,   default=5,  help="repetitions (flex+extend)")
    ap.add_argument("--rest", "-t",   type=float, default=1.0,help="rest between reps (s)")
    args = ap.parse_args()

    dps   = int(max(10, min(720, args.speed)))
    angle = float(args.angle)
    reps  = max(1, int(args.reps))
    rest  = max(0.0, float(args.rest))

    bp = BP.BrickPi3()
    try:
        print(f"Battery: {bp.get_voltage_battery():.2f} V")
        # Zero encoders at current pose (so angles are relative to 'now')
        bp.offset_motor_encoder(bp.PORT_B, bp.get_motor_encoder(bp.PORT_B))
        bp.offset_motor_encoder(bp.PORT_C, bp.get_motor_encoder(bp.PORT_C))

        for i in range(1, reps+1):
            print(f"[{i}/{reps}] Flex: angle={angle} deg @ {dps} dps")
            flex(bp, angle, dps)

            print(f"[{i}/{reps}] Extend: angle={angle} deg @ {dps} dps")
            extend(bp, angle, dps)

            if i < reps and rest > 0:
                print(f"Rest {rest:.2f}s…")
                time.sleep(rest)

        # Coast stop
        bp.set_motor_dps(bp.PORT_B, 0)
        bp.set_motor_dps(bp.PORT_C, 0)
        bp.set_motor_power(bp.PORT_B, 0)
        bp.set_motor_power(bp.PORT_C, 0)
        print("Done.")
    except KeyboardInterrupt:
        print("\nInterrupted. Stopping…")
    finally:
        bp.reset_all()

if __name__ == "__main__":
    main()
