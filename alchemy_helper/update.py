
import sys
import os
import argparse

from common import *


def parse_options():
    parser = argparse.ArgumentParser()
    parser.add_argument("name", help = "Name of the item to be added.")
    parser.add_argument("-b", "--bunch", type = int, default = "1", help = "Number of items composed once.")
    parser.add_argument("-d", "--depend", nargs = "*", default = [], help = "Required depend items of this item, and number of each depend item needed each time.")
    parser.add_argument("-s", "--descript", default = "", help = "Description of the item.")
    parser.add_argument("-f", "--force", action = "store_true", help = "Update item if already exists; Create dpendent items if not existing.")

    return parser.parse_args()

# rearrange depends
# each item in option depends may be followed by a number,
# item name cannot be number
def parse_depends(args):
    depends = args['depend']
    args['depend'] = list()
    i = 0
    while i < len(depends):
        if depends[i].isdigit():
            print("Error, depend item name '{}' is digit".format(depends[i]))
            exit(-1)
        if (i + 1 < len(depends)) and depends[i + 1].isdigit():
            args['depend'].append((depends[i], depends[i + 1]))
            i += 2
        else:
            args['depend'].append((depends[i], '1'))
            i += 1


def main():

    init_db()

    args = vars(parse_options())
    #print(args)

    parse_depends(args)

    if args['force']:
        remove_existing_item(args['name'])
    else:
        assert_item_not_exist(args['name'])
        for x in args['depend']:
            assert_item_exists(x[0])

    add_item(args)

    close_db()

if __name__ == "__main__":
    # assert python version is 3
    if sys.version_info.major < 3:
        print("This script only runs in python3")
        exit()

    main()
