#!/usr/bin/env python3
"""
Elbow power-cycle (BrickPi3) — same-direction dual-motor drive
- Trapezoidal power profile (ramp up -> cruise -> ramp down)
- Mid-phase rest
- Per-phase smoothness metrics from encoder sampling
- Velocity clamp (soft + hard) based on encoder velocities

Examples:
  python3 test_exo_movements.py --power 40 --tflex 2.0 --textend 2.0 \
    --reps 3 --rest 0.8 --ramp 0.8 --midrest 0.5 \
    --vmax 60 --vhard 150
"""

import time
import argparse
import math
import brickpi3 as BP

SAMPLE_DT = 0.02  # 50 Hz encoder sampling for smoothness metrics


def clamp(val, lo, hi):
    return max(lo, min(hi, val))


def set_both_power(bp, p):
    p = int(clamp(p, -100, 100))
    bp.set_motor_power(bp.PORT_B, p)
    bp.set_motor_power(bp.PORT_C, p)


def get_joint_angle(bp):
    """
    Returns current joint angle in degrees, as average of B and C encoders.
    Encoders are assumed to have been offset at neutral pose in main().
    (Currently only used if you want to debug angles.)
    """
    eB = bp.get_motor_encoder(bp.PORT_B)
    eC = bp.get_motor_encoder(bp.PORT_C)
    return 0.5 * (eB + eC)


def phased_power_profile(t, duration, ramp, duty):
    """
    Symmetric ramp up -> cruise -> ramp down triangle/trapezoid profile.
    Returns the instantaneous commanded duty at time t in [0, duration].
    """
    ramp = clamp(ramp, 0.0, duration / 2.0)
    cruise_start = ramp
    cruise_end = duration - ramp

    if t <= 0:
        return 0.0
    if t < cruise_start and ramp > 0:
        return duty * (t / ramp)                  # ramp up
    if t <= cruise_end:
        return duty                                # cruise
    if t < duration and ramp > 0:
        return duty * (1.0 - (t - cruise_end) / ramp)  # ramp down
    return 0.0


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
        return dict(
            rms_jerk=float('nan'),
            acc_zero_cross=0,
            peak_vel=0.0,
            move_time=(ts[-1] - ts[0] if ts else 0.0),
            smoothness_score=0.0,
        )

    v = []
    a = []
    j = []

    # velocities
    for i in range(1, len(ts)):
        dt = ts[i] - ts[i - 1]
        if dt <= 0:
            dt = SAMPLE_DT
        v.append((xs[i] - xs[i - 1]) / dt)

    # accelerations
    for i in range(1, len(v)):
        dt = ts[i + 1] - ts[i]
        if dt <= 0:
            dt = SAMPLE_DT
        a.append((v[i] - v[i - 1]) / dt)

    # jerk
    for i in range(1, len(a)):
        dt = ts[i + 2] - ts[i + 1] if (i + 2) < len(ts) else SAMPLE_DT
        if dt <= 0:
            dt = SAMPLE_DT
        j.append((a[i] - a[i - 1]) / dt)

    if j:
        rms_jerk = math.sqrt(sum(val * val for val in j) / len(j))
    else:
        rms_jerk = 0.0

    acc_zero_cross = 0
    for i in range(1, len(a)):
        if (a[i - 1] > 0 and a[i] < 0) or (a[i - 1] < 0 and a[i] > 0):
            acc_zero_cross += 1

    peak_vel = max((abs(val) for val in v), default=0.0)
    move_time = ts[-1] - ts[0] if ts else 0.0

    # Heuristic score: normalize by peak_vel to reduce amplitude dependence
    # and map to ~[0..100]. Lower jerk -> higher score.
    denom = max(1e-6, peak_vel)  # avoid div by zero
    norm_jerk = rms_jerk / denom
    smoothness_score = 100.0 / (1.0 + 15.0 * norm_jerk)  # 15.0 tunes sensitivity

    return dict(
        rms_jerk=rms_jerk,
        acc_zero_cross=acc_zero_cross,
        peak_vel=peak_vel,
        move_time=move_time,
        smoothness_score=smoothness_score,
    )


def run_phase(bp, label, duty, duration, ramp,
              hold_power=0, hold_time=0.0,
              vmax=80.0, vhard=200.0):
    """
    Executes one phase with a trapezoidal duty profile.
    Applies a velocity clamp based on encoder velocity (deg/s).
    Samples encoders at ~50 Hz to compute smoothness metrics.
    Returns (enc_delta_B, enc_delta_C, metrics_dict)
    """
    duty = int(clamp(duty, -100, 100))
    ramp = clamp(ramp, 0.0, duration / 2.0)

    # start sampling
    t0 = time.time()
    ts = []
    xb = []
    xc = []

    eB0 = bp.get_motor_encoder(bp.PORT_B)
    eC0 = bp.get_motor_encoder(bp.PORT_C)

    # initial state for velocity estimation (use average angle)
    last_angleB = eB0
    last_angleC = eC0
    last_t_abs = time.time()

    print(f"-> {label}: duty {duty:+d}%, T={duration:.2f}s, ramp={ramp:.2f}s")

    # time-stepped control
    while True:
        now_abs = time.time()
        t_rel = now_abs - t0
        if t_rel > duration:
            break

        # nominal command from trapezoidal profile
        cmd = phased_power_profile(t_rel, duration, ramp, duty)

        # current joint angle (average of B & C)
        angleB = bp.get_motor_encoder(bp.PORT_B)
        angleC = bp.get_motor_encoder(bp.PORT_C)
        angle = 0.5 * (angleB + angleC)

        # ---- compute velocity (deg/s) from average angle ----
        last_angle = 0.5 * (last_angleB + last_angleC)
        dt = now_abs - last_t_abs
        if dt <= 0:
            dt = SAMPLE_DT
        vel = (angle - last_angle) / dt  # deg/s

        last_angleB = angleB
        last_angleC = angleC
        last_t_abs = now_abs

        # ---- HARD velocity limit ----
        if abs(vel) > vhard:
            print(f"[HARD-VEL] |v|={abs(vel):.1f}°/s > {vhard:.1f}°/s — stopping.")
            set_both_power(bp, 0)
            raise RuntimeError("Hard velocity limit exceeded")

        # ---- SOFT velocity clamp ----
        if abs(vel) > vmax and abs(cmd) > 1e-3:
            scale = vmax / abs(vel)
            cmd = cmd * scale
            # Optional debug:
            # print(f"[VEL CLAMP] v={vel:.1f}°/s, cmd scaled by {scale:.2f}")

        # apply motor command
        set_both_power(bp, cmd)

        # sample encoders for smoothness
        ts.append(t_rel)
        xb.append(angleB)
        xc.append(angleC)

        time.sleep(SAMPLE_DT)

    # ensure stop at end of motion phase
    set_both_power(bp, 0)

    # optional endpoint hold (counter gravity/straps)
    if hold_time > 0 and hold_power != 0:
        hp = int(clamp(hold_power if duty >= 0 else -hold_power, -100, 100))
        set_both_power(bp, hp)
        time.sleep(hold_time)
        set_both_power(bp, 0)

    eB1 = bp.get_motor_encoder(bp.PORT_B)
    eC1 = bp.get_motor_encoder(bp.PORT_C)
    dB = eB1 - eB0
    dC = eC1 - eC0

    # metrics (use average of B & C positions to reduce single-encoder noise)
    xavg = [(xb[i] + xc[i]) * 0.5 for i in range(len(xb))]
    metrics = compute_smoothness(ts, xavg)

    print(
        f"   enc Δ: B={dB:+.1f}°, C={dC:+.1f}° | "
        f"smoothness: score={metrics['smoothness_score']:.1f}, "
        f"rms_jerk={metrics['rms_jerk']:.3f}, "
        f"acc_zero_cross={metrics['acc_zero_cross']}, "
        f"peak_vel={metrics['peak_vel']:.1f}°/s"
    )

    return dB, dC, metrics


def main():
    ap = argparse.ArgumentParser(
        description=(
            "Elbow flex/extend in power mode (B and C same direction) "
            "with midrest, velocity clamp, and smoothness metrics"
        )
    )

    # Motion parameters
    ap.add_argument(
        "--power", type=int, default=40,
        help="duty %% magnitude for flex/extend (0..100)"
    )
    ap.add_argument(
        "--tflex", type=float, default=2.0,
        help="flex duration (s)"
    )
    ap.add_argument(
        "--textend", type=float, default=2.0,
        help="extend duration (s)"
    )
    ap.add_argument(
        "--reps", type=int, default=3,
        help="number of repetitions"
    )
    ap.add_argument(
        "--rest", type=float, default=1.0,
        help="rest between repetitions (s)"
    )
    ap.add_argument(
        "--midrest", type=float, default=0.5,
        help="rest between EXTEND and FLEX (s)"
    )
    ap.add_argument(
        "--ramp", type=float, default=0.8,
        help="accel/decel ramp time each side (s)"
    )
    ap.add_argument(
        "--hold-power", type=int, default=0,
        help="endpoint hold duty %% (0..50 suggested)"
    )
    ap.add_argument(
        "--hold-time", type=float, default=0.0,
        help="seconds to hold at end of each phase"
    )
    ap.add_argument(
        "--invert", action="store_true",
        help="invert signs (swap flex/extend direction) if your build is mirrored"
    )

    # Velocity limits
    ap.add_argument(
        "--vmax", type=float, default=60.0,
        help="soft velocity limit in deg/s (motor power scaled when exceeded)"
    )
    ap.add_argument(
        "--vhard", type=float, default=150.0,
        help="hard velocity cutoff in deg/s (motor stops immediately when exceeded)"
    )

    args = ap.parse_args()

    duty = int(clamp(abs(args.power), 0, 100))
    tflex = max(0.1, float(args.tflex))
    textend = max(0.1, float(args.textend))
    reps = max(1, int(args.reps))
    rest = max(0.0, float(args.rest))
    midrest = max(0.0, float(args.midrest))
    ramp = max(0.0, min(2.5, float(args.ramp)))
    hold_power = int(clamp(abs(args.hold_power), 0, 100))
    hold_time = max(0.0, float(args.hold_time))
    vmax = float(args.vmax)
    vhard = float(args.vhard)

    # Signs: FLEX = +duty, EXTEND = -duty (both motors same sign)
    s_flex, s_ext = (+1, -1)
    if args.invert:
        s_flex, s_ext = (-s_flex, -s_ext)

    bp = BP.BrickPi3()
    try:
        vbat = bp.get_voltage_battery()
        print(f"Battery: {vbat:.2f} V")
        if vbat < 8.0:
            print("[note] Low battery reduces torque; consider charging/new cells.")

        # Zero encoders relative to current pose (current elbow pose becomes 0°)
        bp.offset_motor_encoder(bp.PORT_B, bp.get_motor_encoder(bp.PORT_B))
        bp.offset_motor_encoder(bp.PORT_C, bp.get_motor_encoder(bp.PORT_C))

        # Make sure motors are off before starting
        set_both_power(bp, 0)

        scores = []  # collect per-phase smoothness scores

        for i in range(1, reps + 1):
            print(f"\nRep {i}/{reps}")

            # EXTEND
            _, _, m_ext = run_phase(
                bp,
                label="EXTEND",
                duty=s_ext * duty,
                duration=textend,
                ramp=ramp,
                hold_power=hold_power,
                hold_time=hold_time,
                vmax=vmax,
                vhard=vhard,
            )
            scores.append(m_ext["smoothness_score"])

            # Mid-rest between phases
            if midrest > 0:
                print(f"Mid-rest {midrest:.2f}s")
                time.sleep(midrest)

            # FLEX
            _, _, m_flex = run_phase(
                bp,
                label="FLEX",
                duty=s_flex * duty,
                duration=tflex,
                ramp=ramp,
                hold_power=hold_power,
                hold_time=hold_time,
                vmax=vmax,
                vhard=vhard,
            )
            scores.append(m_flex["smoothness_score"])

            # Rest between repetitions
            if i < reps and rest > 0:
                print(f"Rest {rest:.2f}s")
                time.sleep(rest)

        if scores:
            avg_score = sum(scores) / len(scores)
            print(f"\nAverage Smoothness Score across phases: {avg_score:.1f}")

        print("\nDone.")
    except KeyboardInterrupt:
        print("\nInterrupted — stopping.")
    except RuntimeError as e:
        print(f"\n{e}")
    finally:
        set_both_power(bp, 0)
        bp.reset_all()


if __name__ == "__main__":
    main()
