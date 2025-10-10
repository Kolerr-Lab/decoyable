
"""
Test file for v1.1.1 auto-fix features.
NOTE: This file contains intentional use of dangerous patterns (os.system, subprocess with shell=True, etc.)
for the purpose of testing, demonstration, and validation of security scanners. These are NOT used in production code.
CLI tool with command injection vulnerabilities
"""

import os
import argparse

def ping_host(host):
    """Command Injection - os.system with concatenation"""
    os.system("ping -c 4 " + host)

def traceroute(target):
    """Command Injection - os.system with variable"""
    command = "traceroute " + target
    os.system(command)

def nslookup(domain):
    """Command Injection - os.system with format string"""
    os.system("nslookup %s" % domain)

def dig_query(hostname):
    """Command Injection - os.system in function"""
    os.system("dig " + hostname)

def main():
    parser = argparse.ArgumentParser(description='Network utilities')
    parser.add_argument('--host', help='Host to ping')
    parser.add_argument('--target', help='Target for traceroute')
    parser.add_argument('--domain', help='Domain for nslookup')
    
    args = parser.parse_args()
    
    if args.host:
        ping_host(args.host)
    if args.target:
        traceroute(args.target)
    if args.domain:
        nslookup(args.domain)

if __name__ == '__main__':
    main()
