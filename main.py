'''
No common machine should have address 1.1.1.1:
>>> get_address_state('lo', '1.1.1.1')
False

But we should have 127.0.0.1:
>>> get_address_state('lo', '127.0.0.1')
True
'''

import os
import random
import netifaces
import etcd3
import logging
from time import sleep


def get_address_state(dev: str, address: str) -> bool:
    '''
    determine whether a given address is already assigned
    '''
    parsed_addresses = []
    ifaces = netifaces.ifaddresses(dev)

    for i in ifaces:
        for j in ifaces[i]:
            for a, b in j.items():
                if a == 'addr':
                    parsed_addresses.append(b)

    if address in parsed_addresses:
        return True
    else:
        return False


def provision_address(dev: str, address: str, netmask: str) -> None:
    '''
    assure an address is assigned to a device
    '''
    if get_address_state(dev, address) is False:
        logging.info('assuming address')
        os.system('ip address add ' + address + netmask + ' dev ' + dev)


def enforce_no_address(dev: str, address: str, netmask: str) -> None:
    '''
    assure an address is not assigned to a device
    '''
    if get_address_state(dev, address) is True:
        logging.info('forfeiting address')
        os.system('ip address del ' + address + netmask + ' dev ' + dev)


def main():
    address = os.getenv('TURNIP_IP')
    netmask = os.getenv('TURNIP_NETMASK')
    dev = os.getenv('TURNIP_DEV')
    me = os.getenv('TURNIP_ID')

    logging.basicConfig(level=logging.INFO)
    etcd = etcd3.client()

    while True:
        sleep(random.randrange(1, 15))
        leader = ''

        try:
            leader = str(etcd.status().leader)
        except etcd3.exceptions.ConnectionFailedError:
            logging.info('etcd3.exceptions.ConnectionFailedError')

        # if im the master, assume the address
        if me in leader:
            provision_address(dev, address, netmask)
        else:
            enforce_no_address(dev, address, netmask)


if __name__ == '__main__':
    main()
