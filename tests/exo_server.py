#!/usr/bin/env python3
import socket, json, subprocess

# UDP settings (must match MATLAB exoPort)
LISTEN_IP = "0.0.0.0"   # listen on all interfaces
LISTEN_PORT = 5014

# Path to your movement script
EXO_SCRIPT = "/home/pi/lego_arm/tests/test_exo_movements.py"

def run_exo_action(action: str):
    """
    Map 'grab' / 'lift' actions to specific exo movements.
    Adjust the parameters as you like.
    """
    if action == "grab":
        # e.g. slower, smaller movement
        cmd = [
            "python3", EXO_SCRIPT,
            "--power", "0",
            "--tflex", "2.0",
            "--textend", "2.0",
            "--reps", "1",
            "--ramp", "0.8",
            "--vmax", "50",
            "--vhard", "120",
        ]
    elif action == "lift":
        # e.g. a bit stronger/faster
        cmd = [
            "python3", EXO_SCRIPT,
            "--power", "80",
            "--tflex", "3.4",
            "--textend", "2.0",
            "--reps", "1",
            "--ramp", "0.6",
            "--vmax", "160",
            "--vhard", "280",
        ]
    else:
        print(f"[WARN] Unknown action '{action}', ignoring.")
        return

    print(f"[EXO] Running action '{action}' with command: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
        print("[EXO] Movement done.")
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Movement script failed: {e}")


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((LISTEN_IP, LISTEN_PORT))
    print(f"[SERVER] Listening on {LISTEN_IP}:{LISTEN_PORT}")

    while True:
        data, addr = sock.recvfrom(4096)
        msg_str = data.decode("utf-8", errors="ignore")
        print(f"[RX] From {addr}: {msg_str}")

        try:
            msg = json.loads(msg_str)
        except json.JSONDecodeError:
            print("[WARN] Not valid JSON, skipping.")
            continue

        msg_type = msg.get("type", "")
        if msg_type == "ping":
            print("[INFO] Ping received from MATLAB/Unity.")
            continue

        if msg_type != "pred":
            print(f"[WARN] Unknown message type '{msg_type}', skipping.")
            continue

        action   = msg.get("class", None)
        conf     = msg.get("conf", None)
        trial_id = msg.get("trial_id", None)

        print(f"[PRED] trial={trial_id}, class={action}, conf={conf}")

        # Optional: confidence check on the Pi too
        if conf is not None and conf < 0.1:
            print("[INFO] Low confidence, ignoring prediction on Pi.")
            continue

        if action in ("grab", "lift"):
            run_exo_action(action)
        else:
            print(f"[WARN] Unsupported class '{action}', ignoring.")


if __name__ == "__main__":
    main()
