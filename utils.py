"""
filename: utils.py
author: Ryan Cervantes (rxc3202)
description: utility functions
"""

import sys
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
	parser.add_argument("-v", "--verbose", action="count", help="""Use -v to display [INFO].
																   Use -vv to display [INFO] and [DEBUG].""")
	parser.add_argument("--discovery", action="store_true")
	parser.add_argument("--threaded", action="store_true", help="""Thread the handlers to handle a large amount of clients""")
	parser.add_argument("--blacklist", nargs=1, help="Don't interact with these IPs")
	parser.add_argument("--whitelist", nargs=1, type=argparse.FileType('r'), help="""Only interact with these IPs.
																			Use ':' to delimit IPs to hostnames (<ip>:<hostname>).
																			Takes precedence over blacklist. If no file is given,
																			then IPs will be read in from the commandline""")
	return parser.parse_args()

def parse_whitelist(filename):
	whitelist = []
	# with open(filename, 'r') as file:
	# 	for line in file:
	# 		ip, hostname = line.strip().split(':')
	# 		whitelist.append((ip, hostname))
	return whitelist
			

