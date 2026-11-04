#!/usr/bin/env python3
"""Run every reference self-test in one go (no network, no credentials)."""
import subprocess
import sys

TESTS = [
    ("pipe_proto", [sys.executable, "pipe_proto.py"]),
    ("auth_build", [sys.executable, "auth_build.py"]),
]

failed = 0
for name, cmd in TESTS:
    print(f"=== {name} " + "=" * (40 - len(name)))
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout.strip())
    if result.returncode != 0:
        failed += 1
        print(result.stderr.strip()[:400])

print("\nresult:", "all self-tests passed" if not failed else f"{failed} test(s) failed")
sys.exit(1 if failed else 0)
