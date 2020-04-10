from ipaddress import ip_address, ip_network, IPv4Address, IPv4Network, \
    IPv6Network, IPv6Address


def ip_validator(ips: str):
    """
    Checks if the IPs and Subnets given as a string separated by commas
    are all valid notation
    :param ips: a string of IPs and Subnets in CIDR notation
    :return: None if no error else the first element that was a problem
    """
    data = ips.replace(' ', '').split(",")
    failure = None
    try:
        input_ips = set(filter(lambda x: "/" not in x, data))
        for target in input_ips:
            failure = target
            IPv4Address(target)
    except ValueError:
        return failure

    try:
        input_subnets = filter(lambda x: "/" in x, data)
        for target in input_subnets:
            failure = target
            IPv4Network(target)
    except ValueError:
        return failure

    return None
