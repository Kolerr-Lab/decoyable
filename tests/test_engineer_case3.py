def run_ping(host):
    # vulnerable
    os.system("ping -c 1 " + host)

if __name__ == "__main__":
    run_ping("8.8.8.8")

"""
Test Case 3: Command Injection via os.system
NOTE: This file contains intentional use of dangerous patterns (os.system, subprocess with shell=True, etc.)
for the purpose of testing, demonstration, and validation of security scanners. These are NOT used in production code.
"""
import os
