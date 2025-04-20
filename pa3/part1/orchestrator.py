#!/usr/bin/env python3

import argparse
import subprocess

ROUTERS = ['r1', 'r2', 'r3', 'r4']
HOSTS = ['ha', 'hb']

# === Network Setup ===
def build_network():
    print("Building network topology...")
    subprocess.run(["docker", "compose", "up", "-d"], check=True)
    print("Network started.")

# === OSPF Setup ===
def start_ospf():
    print("Starting OSPF daemons...")
    for router in ROUTERS:
        cmd = f"docker exec part1-{router}-1 bash -c 'service frr restart'"
        subprocess.run(cmd, shell=True, check=True)
    print("OSPF started.")

# === Route Installation ===
def install_routes():
    print("Installing static routes on hosts...")
    # Replace these IPs with your actual topology
    subprocess.run("docker exec part1-ha-1 ip route add 10.0.15.0/24 via 10.0.14.4", shell=True, check=True)
    subprocess.run("docker exec part1-hb-1 ip route add 10.0.14.0/24 via 10.0.15.4", shell=True, check=True)
    print("Static routes installed.")

# === Path Switching ===
def switch_path(path):
    print(f"Switching to {path.upper()} path...")
    if path == "north":
        # Prefer R1-R2-R3: make R1-R4 cost high
        subprocess.run("docker exec part1-r1-1 vtysh -c 'conf t' -c 'interface eth1' -c 'ip ospf cost 100'", shell=True)
        subprocess.run("docker exec part1-r1-1 vtysh -c 'conf t' -c 'interface eth0' -c 'ip ospf cost 5'", shell=True)
        subprocess.run("docker exec part1-r3-1 vtysh -c 'conf t' -c 'interface eth2' -c 'ip ospf cost 100'", shell=True)
        subprocess.run("docker exec part1-r3-1 vtysh -c 'conf t' -c 'interface eth1' -c 'ip ospf cost 5'", shell=True)
    elif path == "south":
        # Prefer R1-R4-R3: make R1-R2 cost high
        subprocess.run("docker exec part1-r1-1 vtysh -c 'conf t' -c 'interface eth0' -c 'ip ospf cost 100'", shell=True)
        subprocess.run("docker exec part1-r1-1 vtysh -c 'conf t' -c 'interface eth1' -c 'ip ospf cost 5'", shell=True)
        subprocess.run("docker exec part1-r3-1 vtysh -c 'conf t' -c 'interface eth2' -c 'ip ospf cost 100'", shell=True)
        subprocess.run("docker exec part1-r3-1 vtysh -c 'conf t' -c 'interface eth1' -c 'ip ospf cost 5'", shell=True)
    else:
        print("Invalid path. Choose 'north' or 'south'.")
        return
    print(f"Switched to {path.upper()} path.")

# === Main Entry Point ===
def main():
    parser = argparse.ArgumentParser(description="Network Orchestrator Tool")
    parser.add_argument('--build', action='store_true', help="Build the network topology with Docker Compose")
    parser.add_argument('--start-ospf', action='store_true', help="Start OSPF daemons on all routers")
    parser.add_argument('--setup-routes', action='store_true', help="Install static routes on hosts")
    parser.add_argument('--switch-path', choices=['north', 'south'], help="Switch routing path")

    args = parser.parse_args()

    if args.build:
        build_network()
    if args.start_ospf:
        start_ospf()
    if args.setup_routes:
        install_routes()
    if args.switch_path:
        switch_path(args.switch_path)

if __name__ == "__main__":
    main()