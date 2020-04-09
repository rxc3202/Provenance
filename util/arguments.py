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
    parser.add_argument("-v", "--verbose",
                        action="count",
                        default=0,
                        help="""Use -v to display [INFO]. Use -vv to display [INFO] and [DEBUG].""")

    parser.add_argument("--no-discovery",
                        dest="discovery",
                        action="store_false",
                        help="""Turn of automatic adding of hosts as they connect to the server.
                        They must be added manually or using the --whitelist command at program start""")

    parser.add_argument("--no-threading",
                        action="store_false",
                        dest="threading",
                        help="""Do not thread the client handlers, run all requests on one thread""")

    parser.add_argument("--restore",
                        dest="restore",
                        nargs=1,
                        type=str,
                        help="""Restore tracked machines and commands from a file""")

    parser.add_argument("--blacklist",
                        dest="blacklist",
                        nargs=1,
                        help="Don't interact with these IPs")

    # TODO: add modification to format -> OS:IP:HOSTNAME:{DNS|ICMP|HTTP}
    parser.add_argument("--whitelist",
                        dest="whitelist",
                        nargs='?',
                        default=None,
                        const=None,
                        type=str,
                        help="""Only interact with these IPs. One IP per line of text file.
                        in the format IP:HOSTNAME:{DNS|ICMP|HTTP}
                        Blacklisted IPs are invalid even if they are on the whitelist. """)
    return parser.parse_args()


def verbosity(level):
    return (3 - level) * 10


def parse_whitelist(filename):
    hosts = []
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip().split(':')
            hosts.append((line[0], line[1], line[2]))
    return hosts


def get_whitelist():
    print( "Please enter hosts you wish to track in the format:\n"
           "\"IP:HOSTNAME:{DNS|ICMP|HTTP}\"\n"
           "To exit leave the line blank <ENTER>")
    hosts = []
    while True:
        x = input(">> ")
        if x == '':
            break
        hosts.append(x)
    return hosts



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
