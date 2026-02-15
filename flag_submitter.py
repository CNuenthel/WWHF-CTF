import json
import os
import time
from api import submit_flag

FLAGS_FILE = "flags.json"


def load_flags() -> list:
    if not os.path.exists(FLAGS_FILE):
        return []
    with open(FLAGS_FILE, "r") as f:
        return json.load(f)


def save_flags(flags: list):
    with open(FLAGS_FILE, "w") as f:
        json.dump(flags, f, indent=2)


def main():
    print("[+] Flag submitter started")
    while True:
        flags = load_flags()
        if not flags:
            time.sleep(5)
            continue

        print(f"[+] {len(flags)} flag(s) queued for submission")
        remaining = []
        for flag in flags:
            result = submit_flag(flag)
            if result:
                print(f"[$] Submitted: {flag}")
            else:
                print(f"[!] Failed to submit: {flag}, keeping in queue")
                remaining.append(flag)

        save_flags(remaining)
        time.sleep(5)


if __name__ == "__main__":
    main()
