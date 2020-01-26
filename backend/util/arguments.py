import argparse
from ipaddress import ip_network, ip_address, \
    IPv4Address, IPv4Network, IPv6Address, IPv6Network


def parse_arguments():
    parser = argparse.ArgumentParser(description="The Provenance C2 Server")
    # Positional Arguments
    parser.add_argument("ui",
                        choices=["gui", "cli"],
                        help="Run the server as a command line application or spawn a GUI")
    parser.add_argument("interface", help="The interface the C2 Sever is located on")
    parser.add_argument("port", type=int, default=53, help="The port on which the server listens")
    # Optional Arguments
    parser.add_argument("-v", "--verbose", action="count", default=0,
                        help="""Use -v to display [INFO]. Use -vv to display [INFO] and [DEBUG].""")

    parser.add_argument("--no-discovery", dest="discovery", action="store_false",
                        help="""Turn of automatic adding of hosts as they connect to the server.
                        They must be added manually or using the --whitelist command at program start""")

    parser.add_argument("--threaded", action="store_true",
                        help="""Thread the handlers to handle a large amount of clients""")

    parser.add_argument("--blacklist", nargs=1, help="Don't interact with these IPs")

    parser.add_argument("--whitelist", nargs=1, type=argparse.FileType('r'),
                        help="""Only interact with these IPs. One IP per line of text file.
                        Blacklisted IPs are invalid even if they are on the whitelist""")
    return parser.parse_args()


def verbosity(level):
    return (3 - level) * 10


def parse_ips(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file]


def ip_in_list(ip, ip_list):
    if not ip_list:
        return False

    for x in ip_list:
        y = ip_network(x) if '/' in x else ip_address(x)
        if isinstance(y, IPv4Network) or isinstance(y, IPv6Network):
            if ip_address(ip) in y:
                return True
        if isinstance(y, IPv4Address) or isinstance(y, IPv6Address):
            if ip_address(ip) == y:
                return True
