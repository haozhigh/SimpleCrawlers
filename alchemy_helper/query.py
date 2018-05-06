

import sys
import os
import argparse

from common import *


def parse_options():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--list", action = "store_true", help = "List all item names")
    parser.add_argument("-L", "--list_depends", action = "store_true", help = "List all item depends")
    parser.add_argument("-s", "--search", help = "Search an item", default = "")
    parser.add_argument("-f", "--filter", help = "Filter item names and descriptions", default = "")

    return parser.parse_args()

def display_item(name):
    item, depends, items = get_item(name)

    print("[{}]".format(item['name']))

    print("  {}".format(item['descript']))

    for x in items:
        print("  -> [{}]".format(x))

    if len(depends) > 0:
        print("[{} x {}]".format(item['name'], item['bunch']))
    for depend in depends:
        print("  <- [{} x {}]".format(depend[0], depend[1]))

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
        display_item(args['search'])
    elif args['filter'] != "":
        names = filter_items(args['filter'])
        i = 0
        for name in names:
            i += 1
            print("################ Filtered {} ################".format(i))
            display_item(name)
    else:
        print("No option specified")

    close_db()

if __name__ == "__main__":
    # assert python version is 3
    if sys.version_info.major < 3:
        print("This script only runs in python3")
        exit()

    main()
