#!/usr/bin/env python3
"""
Elbow position-cycle (BrickPi3) — same-direction dual-motor drive
Position-based with smooth trajectory and encoder-based control.

Example:
  python3 elbow_pos_cycle.py --amp-deg 90 --Tflex 2.0 --Textend 2.0 \
      --reps 5 --rest 0.8 --midrest 0.5 --kp 0.7 --max-power 80
"""

import time
import argparse
import math
import brickpi3 as BP

SAMPLE_DT = 0.02  # 50 Hz sampling for control + smoothness

# ----------------- Helpers -----------------

def clamp(val, lo, hi):
    return max(lo, min(hi, val))

def set_both_power(bp, p):
    p = int(clamp(p, -100, 100))
    bp.set_motor_power(bp.PORT_B, p)
    bp.set_motor_power(bp.PORT_C, p)

def get_avg_encoder_deg(bp):
    return 0.5 * (bp.get_motor_encoder(bp.PORT_B) +
                  bp.get_motor_encoder(bp.PORT_C))

def smooth_profile_01(t, T):
    """
    Smooth s(t) in [0,1] with zero vel at t=0,T.
    Cosine 'minimum jerk-like' (not exact min-jerk, but very smooth):
      s(t) = 0.5 - 0.5*cos(pi * t / T)
    """
    t = clamp(t, 0.0, T)
    return 0.5 - 0.5 * math.cos(math.pi * t / T)

# ----------------- Smoothness metrics (unchanged) -----------------

def compute_smoothness(ts, xs):
    """
    Compute simple smoothness features from a sampled (t, encoder) trajectory:
      - rms_jerk (deg/s^3)
      - acc_zero_cross (count)
      - peak_vel (deg/s)
      - move_time (s)
      - smoothness_score (higher ~ smoother), heuristic from rms_jerk
    """
    if len(ts) < 5:
        return dict(rms_jerk=float('nan'), acc_zero_cross=0, peak_vel=0.0,
                    move_time=(ts[-1]-ts[0] if ts else 0.0), smoothness_score=0.0)

    v, a, j = [], [], []
    for i in range(1, len(ts)):
        dt = ts[i] - ts[i-1]
        if dt <= 0: dt = SAMPLE_DT
        v.append((xs[i] - xs[i-1]) / dt)
    for i in range(1, len(v)):
        dt = ts[i+1] - ts[i] if (i+1) < len(ts) else SAMPLE_DT
        if dt <= 0: dt = SAMPLE_DT
        a.append((v[i] - v[i-1]) / dt)
    for i in range(1, len(a)):
        dt = ts[i+2] - ts[i+1] if (i+2) < len(ts) else SAMPLE_DT
        if dt <= 0: dt = SAMPLE_DT
        j.append((a[i] - a[i-1]) / dt)

    rms_jerk = math.sqrt(sum(val*val for val in j) / len(j)) if j else 0.0
    acc_zero_cross = 0
    for i in range(1, len(a)):
        if (a[i-1] > 0 and a[i] < 0) or (a[i-1] < 0 and a[i] > 0):
            acc_zero_cross += 1
    peak_vel = max((abs(val) for val in v), default=0.0)
    move_time = ts[-1] - ts[0] if ts else 0.0

    # Heuristic score: normalize by peak_vel to reduce amplitude dependence
    denom = max(1e-6, peak_vel)
    norm_jerk = rms_jerk / denom
    smoothness_score = 100.0 / (1.0 + 15.0 * norm_jerk)

    return dict(rms_jerk=rms_jerk,
                acc_zero_cross=acc_zero_cross,
                peak_vel=peak_vel,
                move_time=move_time,
                smoothness_score=smoothness_score)

# ----------------- Position-based phase -----------------

def run_phase_pos(bp, label, start_angle, target_angle,
                  T, kp, max_power, hold_power=0, hold_time=0.0):
    """
    Execute one movement phase using a *position trajectory*:

      - start_angle: starting joint angle (deg, from encoders)
      - target_angle: final joint angle (deg)
      - T: duration (s)
      - kp: proportional gain (deg -> %power)
      - max_power: |power| saturation

    Uses a smooth cosine profile between start and target.
    Returns: (enc_delta_B, enc_delta_C, metrics_dict, final_angle)
    """
    T = max(0.1, float(T))
    max_power = int(clamp(max_power, 0, 100))
    hold_power = int(clamp(hold_power, 0, 100))

    delta = target_angle - start_angle

    # Prepare logs for smoothness
    t0 = time.time()
    ts, xb, xc = [], [], []

    eB0 = bp.get_motor_encoder(bp.PORT_B)
    eC0 = bp.get_motor_encoder(bp.PORT_C)

    print(f"-> {label}: {start_angle:+.1f}° -> {target_angle:+.1f}° "
          f"in {T:.2f}s (Δ={delta:+.1f}°), kp={kp:.2f}, maxP={max_power:d}%")

    while True:
        now = time.time()
        t = now - t0
        if t > T:
            break

        s = smooth_profile_01(t, T)
        x_des = start_angle + delta * s
        x_meas_B = bp.get_motor_encoder(bp.PORT_B)
        x_meas_C = bp.get_motor_encoder(bp.PORT_C)
        x_meas = 0.5 * (x_meas_B + x_meas_C)

        err = x_des - x_meas
        cmd = clamp(kp * err, -max_power, max_power)
        set_both_power(bp, cmd)

        ts.append(t)
        xb.append(x_meas_B)
        xc.append(x_meas_C)

        time.sleep(SAMPLE_DT)

    # Stop motion
    set_both_power(bp, 0)

    # Optional endpoint hold (counter gravity/straps)
    if hold_time > 0 and hold_power > 0:
        # hold in the direction of the last motion
        sign = 1.0 if delta >= 0 else -1.0
        hp = int(clamp(sign * hold_power, -100, 100))
        set_both_power(bp, hp)
        time.sleep(hold_time)
        set_both_power(bp, 0)

    eB1 = bp.get_motor_encoder(bp.PORT_B)
    eC1 = bp.get_motor_encoder(bp.PORT_C)
    dB = eB1 - eB0
    dC = eC1 - eC0

    # Metrics on average position
    xavg = [(xb[i] + xc[i]) * 0.5 for i in range(len(xb))]
    metrics = compute_smoothness(ts, xavg)

    print(f"   enc Δ: B={dB:+.1f}°, C={dC:+.1f}° | "
          f"smoothness: score={metrics['smoothness_score']:.1f}, "
          f"rms_jerk={metrics['rms_jerk']:.3f}, "
          f"acc_zero_cross={metrics['acc_zero_cross']}, "
          f"peak_vel={metrics['peak_vel']:.1f}°/s")

    final_angle = get_avg_encoder_deg(bp)
    return dB, dC, metrics, final_angle

# ----------------- Main -----------------

def main():
    ap = argparse.ArgumentParser(
        description="Elbow flex/extend in POSITION mode (B and C same direction) "
                    "with midrest and smoothness metrics"
    )
    ap.add_argument("--amp-deg", type=float, default=90.0,
                    help="movement amplitude (deg) for EXTEND and FLEX (e.g. 90)")
    ap.add_argument("--Textend", type=float, default=0.8,
                    help="EXTEND duration (s)")
    ap.add_argument("--Tflex", type=float, default=2.2,
                    help="FLEX duration (s)")
    ap.add_argument("--reps", type=int, default=3,
                    help="number of repetitions")
    ap.add_argument("--rest", type=float, default=1.0,
                    help="rest between repetitions (s)")
    ap.add_argument("--midrest", type=float, default=1.0,
                    help="rest between EXTEND and FLEX (s)")
    ap.add_argument("--kp", type=float, default=0.7,
                    help="P gain: power = kp * (deg error)")
    ap.add_argument("--max-power", type=int, default=80,
                    help="max |power| for controller (0..100)")
    ap.add_argument("--hold-power", type=int, default=0,
                    help="endpoint hold duty %% (0..50 suggested)")
    ap.add_argument("--hold-time", type=float, default=0.5,
                    help="seconds to hold at end of each phase")
    ap.add_argument("--invert", action="store_true",
                    help="invert sign of angles if build is mirrored (flip direction)")
    args = ap.parse_args()

    amp = abs(float(args.amp_deg))
    Textend = max(0.1, float(args.Textend))
    Tflex = max(0.1, float(args.Tflex))
    reps = max(1, int(args.reps))
    rest = max(0.0, float(args.rest))
    midrest = max(0.0, float(args.midrest))
    kp = float(args.kp)
    max_power = int(clamp(args.max_power, 0, 100))
    hold_power = int(clamp(abs(args.hold_power), 0, 100))
    hold_time = max(0.0, float(args.hold_time))

    # Sign of motion: EXTEND = -amp, FLEX = +amp by default
    sign = -1.0 if args.invert else 1.0
    delta_extend = sign * (-amp)   # go "down"
    delta_flex   = sign * (+amp)   # go "up"

    bp = BP.BrickPi3()
    try:
        vbat = bp.get_voltage_battery()
        print(f"Battery: {vbat:.2f} V")
        if vbat < 8.0:
            print("[note] Low battery reduces torque; consider charging/new cells.")

        # Define current pose as 0 deg
        bp.offset_motor_encoder(bp.PORT_B, bp.get_motor_encoder(bp.PORT_B))
        bp.offset_motor_encoder(bp.PORT_C, bp.get_motor_encoder(bp.PORT_C))
        set_both_power(bp, 0)

        logical_angle = 0.0  # our running estimate of joint angle [deg]
        scores = []

        for i in range(1, reps + 1):
            print(f"\nRep {i}/{reps}")

            # ----- EXTEND phase -----
            start_angle = logical_angle
            target_angle = start_angle + delta_extend
            _, _, m_ext, logical_angle = run_phase_pos(
                bp,
                label="EXTEND",
                start_angle=start_angle,
                target_angle=target_angle,
                T=Textend,
                kp=kp,
                max_power=max_power,
                hold_power=hold_power,
                hold_time=hold_time,
            )
            scores.append(m_ext["smoothness_score"])

            if midrest > 0:
                print(f"Mid-rest {midrest:.2f}s")
                time.sleep(midrest)

            # ----- FLEX phase -----
            start_angle = logical_angle
            target_angle = start_angle + delta_flex
            _, _, m_flex, logical_angle = run_phase_pos(
                bp,
                label="FLEX",
                start_angle=start_angle,
                target_angle=target_angle,
                T=Tflex,
                kp=kp,
                max_power=max_power,
                hold_power=hold_power,
                hold_time=hold_time,
            )
            scores.append(m_flex["smoothness_score"])

            if i < reps and rest > 0:
                print(f"Rest {rest:.2f}s")
                time.sleep(rest)

        if scores:
            avg_score = sum(scores) / len(scores)
            print(f"\nAverage Smoothness Score across phases: {avg_score:.1f}")

        print("\nDone.")
    except KeyboardInterrupt:
        print("\nInterrupted — stopping.")
    finally:
        set_both_power(bp, 0)
        bp.reset_all()

if __name__ == "__main__":
    main()
