#!/usr/bin/env python3

import argparse
import subprocess

ROUTERS = ['r1', 'r2', 'r3', 'r4']
HOSTS = ['ha', 'hb']

def build_network():
    """ Set up the network topology. """
    print("Building network topology...")
    subprocess.run(["docker", "compose", "up", "-d"], check=True)
    print("Network started.")

def start_ospf():
    """ Set up the OSPF daemons. """
    print("Starting OSPF daemons...")
    for router in ROUTERS:
        cmd = f"docker exec part1-{router}-1 bash -c 'service frr restart'"
        subprocess.run(cmd, shell=True, check=True)
    print("OSPF started.")

def install_route(host, route_cmd):
    """
    Install a static route on a given host.

    Parameters:
    - host (str): Name of the container (e.g., "ha", "hb")
    - route_cmd (str): Route command after 'ip route add', e.g., "10.0.15.0/24 via 10.0.14.4"
    """
    print(f"Installing route on {host}: ip route add {route_cmd}")
    try:
        subprocess.run(f"docker exec {host} ip route add {route_cmd}", shell=True, check=True)
        print("Route installed.")
    except subprocess.CalledProcessError:
        print("Failed to install route.")

def switch_path(path):
    """ Switch path. """
    print(f"Switching to {path.upper()} path...")
    if path == "north":
        # Prefer R1-R2-R3: make R1-R4 cost high
        subprocess.run("docker exec part1-r1-1 vtysh -c 'conf t' -c 'interface eth1' -c 'ip ospf cost 100'", shell=True)
        subprocess.run("docker exec part1-r1-1 vtysh -c 'conf t' -c 'interface eth0' -c 'ip ospf cost 5'", shell=True)
        subprocess.run("docker exec part1-r3-1 vtysh -c 'conf t' -c 'interface eth1' -c 'ip ospf cost 100'", shell=True)
        subprocess.run("docker exec part1-r3-1 vtysh -c 'conf t' -c 'interface eth0' -c 'ip ospf cost 5'", shell=True)
    elif path == "south":
        # Prefer R1-R4-R3: make R1-R2 cost high
        subprocess.run("docker exec part1-r1-1 vtysh -c 'conf t' -c 'interface eth0' -c 'ip ospf cost 100'", shell=True)
        subprocess.run("docker exec part1-r1-1 vtysh -c 'conf t' -c 'interface eth1' -c 'ip ospf cost 5'", shell=True)
        subprocess.run("docker exec part1-r3-1 vtysh -c 'conf t' -c 'interface eth0' -c 'ip ospf cost 100'", shell=True)
        subprocess.run("docker exec part1-r3-1 vtysh -c 'conf t' -c 'interface eth1' -c 'ip ospf cost 5'", shell=True)
    else:
        print("Invalid path. Choose 'north' or 'south'.")
        return
    print(f"Switched to {path.upper()} path.")

def main():
    """ Main entry point. """
    example_text = '''
      Examples:
        ./orchestrator.py --build
        ./orchestrator.py --start-ospf
        ./orchestrator.py --install-route part1-ha-1 "10.0.15.0/24 via 10.0.14.4"
        ./orchestrator.py --install-route part1-hb-1 "10.0.14.0/24 via 10.0.15.4"
        ./orchestrator.py --switch-path north
    '''

    parser = argparse.ArgumentParser(
        description="Network Orchestrator Tool",
        epilog=example_text,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--build', action='store_true', help="Build the network topology with Docker Compose")
    parser.add_argument('--start-ospf', action='store_true', help="Start OSPF daemons on all routers")
    parser.add_argument('--install-route', nargs=2, metavar=('HOST', 'ROUTE'),
                        help='Install custom route on a host. Format: <host> "<destination via next-hop>"')
    parser.add_argument('--switch-path', choices=['north', 'south'],
                        help="Switch routing path between 'north' (R1-R2-R3) and 'south' (R1-R4-R3)")
    

    args = parser.parse_args()

    if args.build:
        build_network()
    if args.start_ospf:
        start_ospf()
    if args.switch_path:
        switch_path(args.switch_path)
    if args.install_route:
        host, route_cmd = args.install_route
        install_route(host, route_cmd)


if __name__ == "__main__":
    main()