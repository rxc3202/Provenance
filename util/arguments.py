import argparse


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
                        dest="verbose",
                        default="info",
                        choices=["debug", "info", "warning", "error", "critical"],
                        help="""Use <debug|info|warning|error|critical> for logging levels""")

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
    c = 1
    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            c += 1
            if '#' in line or line == '':
                continue
            try:
                fields = line.split(':')
                hosts.append((fields[0], fields[1], fields[2]))
            except IndexError:
                print(f"Formatting error on line: {c}({line})")
                exit(1)
    return hosts


def get_whitelist():
    print("Please enter hosts you wish to track in the format:\n"
          "\"IP:HOSTNAME:{DNS|ICMP|HTTP}\"\n\n"
          "Or enter the subnet using CIDR_NOTATION:*:*"
          "To exit leave the line blank <ENTER>")
    hosts = []
    while True:
        x = input(">> ")
        if x == '':
            break
        hosts.append(x)
    return hosts
