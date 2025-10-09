# Test Case 3: Command Injection via os.system
# tools/run_ping.py
import os

def run_ping(host):
    # vulnerable
    os.system("ping -c 1 " + host)

if __name__ == "__main__":
    run_ping("8.8.8.8")
