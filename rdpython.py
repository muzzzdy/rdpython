#!/usr/bin/env python
# -*- coding: utf8 -*-

import firewall.client as client
import re
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('-d', '--delport', action='store', help='delete forwarded port')
parser.add_argument('-D', '--deladdr', action='store', help='delete forwarded port')
parser.add_argument('-a', '--addport', action='store', help='add port to forward', nargs=2)
parser.add_argument('-v', '--view', action='store_true', help='View forwarded ports')
parser.add_argument('-i', '--interactive', action='store_true', help='Interactive mode')

args = parser.parse_args()
parser.format_help()

clnt = client.FirewallClient()
frwrd = clnt.getForwardPorts('external')


def viewforwards():
    """
    Displays currently forwarded ports and addresses that they are forwarded to
    """
    for i in range(len(frwrd)):
        port, proto, toport, toaddr = tuple(frwrd[i])
        print('| ' + str(
            i) + ' | FromPort: ' + port + ' | ToPort: ' + toport + ' | IpAddress: ' + '%-15s' % toaddr + ' | Protocol:' + proto)


def check_port(port):
    """
    Placeholder for port validity check
    :param port: TCP Port that is not in "known port" range
    :return: Boolean
    """
    try:
        assert int(port) >= 1000
        return False
    except (AssertionError, ValueError}:
        return True


def check_toaddr(toaddr):
    """
    Checks if provided address is a valid local ip address
    :param toaddr: Ip address matching 192.168.2 or 192.168.3 scheme
    :return: Boolean
    """
    if (re.match(r'192.168.3.[0123456789]', toaddr)
        or re.match(r'192.168.2.[0123456789]', toaddr)) is None \
            or int(toaddr[10:]) > 255:
        return True
    return False


def add_fport(port, toaddr):
    """
    Adds port forward as:
    firewall-cmd --zone=external --add-forward-port=port=port:proto=tcp:toport=3389:toaddr=toaddr
    :param port: external port that is forwarded
    :param toaddr: local ip address to forward to
    """
    clnt.addForwardPort('external', port, 'tcp', '3389', toaddr)
    print ('Forwarded external port: ' + port + ' to local address ' + toaddr + ":3389")


def rem_fport(port, proto, toport, toaddr):
    """
    Removes forwarded port as:
    firewall-cmd --zone=external --remove-forward-port=port=port:proto=tcp:toport=toport:toaddr=toaddr
    :param port: Forwarded port in external zone
    :param proto: Network protocol usually TCP
    :param toport: Port of internal address 3389 for RDP
    :param toaddr: Local ip address
    """
    clnt.removeForwardPort('external', port, proto, toport, toaddr)
    print(
        'Removed forwarding FromPort: ' + port + ' | ToPort: ' + toport + ' | IpAddress: ' + '%-15s' % toaddr + ' | Protocol:' + proto)


if args.view:
    viewforwards()

if args.deladdr:

    if check_toaddr(args.deladdr):
        exit("That's not a valid local IP!")

    for lst in frwrd:
        if args.deladdr in lst:
            port, proto, toport, toaddr = tuple(lst)
            rem_fport(port, proto, toport, toaddr)

if args.delport:

    if check_port(args.delport):
        exit("That's not a valid tcp port!")

    for lst in frwrd:
        if args.delport in lst:
            port, proto, toport, toaddr = tuple(lst)
            rem_fport(port, proto, toport, toaddr)

if args.addport:
    port, toaddr = tuple(args.addport)

    if check_port(port):
        exit('Please do not use "known ports".')

    if check_toaddr(toaddr):
        exit("That's not a valid local IP!")

    add_fport(port, toaddr)

if args.interactive:

    viewforwards()

    while True:
        prm = raw_input('Choose the action - (a)dd/(d)elete/(v)iew/(q)uit:')
        if prm == 'q':
            exit()

        elif prm == 'v':
            viewforwards()

        elif prm == 'a':

            port = raw_input("External port: ")
            if check_port(port):
                print('Please do not use "known ports".')
                continue
            toaddr = raw_input("Local ip: ")
            if check_toaddr(toaddr):
                print("That's not a valid local IP!")
                continue
            add_fport(port, toaddr)

        elif prm == 'd':
            while True:

                try:

                    lntdel = raw_input('Choose which of above to delete (enter number, (v)iew or (q)uit):')

                    if lntdel == 'q':
                        break

                    elif lntdel == 'v':
                        viewforwards()

                    elif int(lntdel) in range(len(frwrd)):

                        port, proto, toport, toaddr = tuple(frwrd[int(lntdel)])

                        rem_fport(port, proto, toport, toaddr)
                        break
                except ValueError:
                    continue
        else:
            continue
