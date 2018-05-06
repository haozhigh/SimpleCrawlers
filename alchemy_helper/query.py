

import sys
import os
import argparse

from common import *


def parse_options():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--list", action = "store_true", help = "List all item names")
    parser.add_argument("-L", "--list_depends", action = "store_true", help = "List all item depends")
    parser.add_argument("-s", "--search", help = "Search an item", default = "")

    return parser.parse_args()

def main():

    init_db()

    args = vars(parse_options())
    #print(args)

    if args['list']:
        print(list_items())
    elif args['list_depends']:
        print(list_depends())
    elif args['search'] != "":
        assert_item_exists(args['search'])
        item, depends, items = get_item(args['search'])

        print("Item Name:")
        print("    {}".format(item['name']))

        print("Item Description:")
        print("    {}".format(item['descript']))

        print("Item '{} x {}' requires:".format(item['name'], item['bunch']))
        for depend in depends:
            print("    {} x {}".format(depend[0], depend[1]))

        print("Item '{}' can be used to compsite:".format(item['name']))
        for x in items:
            print("    {}".format(x))
    else:
        print("No option specified")

    close_db()

if __name__ == "__main__":
    # assert python version is 3
    if sys.version_info.major < 3:
        print("This script only runs in python3")
        exit()

    main()
