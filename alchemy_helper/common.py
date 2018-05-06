import sys
import os

import sqlite3

conn = None
c = None

def init_db():
    global conn
    global c

    # create data directory
    data_dir = "./data"
    if not os.path.isdir(data_dir):
        os.makedirs(data_dir)
        if not os.path.isdir(data_dir):
            print("Failed to create data path '{}'".format(data_dir))
            return

    # open db
    #print("#### Opening database '{}'".format("./data/data.db"))
    conn = sqlite3.connect("./data/data.db")

    # get cursor
    c = conn.cursor()

    # create table items
    c.execute('''
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='items'
        ''')
    if c.fetchone() == None:
        #print("#### Creating table '{}' in database".format('items'))
        c.execute('''
            CREATE TABLE items (
                name TEXT PRIMARY KEY NOT NULL,
                bunch INTEGER NOT NULL,
                descript TEXT NOT NULL)
            ''')

    # create table depends
    c.execute('''
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='depends'
        ''')
    if c.fetchone() == None:
        #print("#### Creating table '{}' in database".format('depends'))
        c.execute('''
            CREATE TABLE depends (
                name TEXT NOT NULL,
                depend_name TEXT NOT NULL,
                depend_bunch INTEGER NOT NULL)
            ''')

def assert_item_exists(name):
    global conn
    global c

    c.execute('''
        SELECT name FROM items 
        WHERE name='{}'
        '''.format(name))
    if c.fetchone() == None:
        print("Item '{}' does not exist in database".format(name))
        exit(-1)

def assert_item_not_exist(name):
    global conn
    global c

    c.execute('''
        SELECT name FROM items 
        WHERE name='{}'
        '''.format(name))
    if c.fetchone() != None:
        print("Item '{}' already exists in database".format(name))
        exit(-1)

# remove existing depends of item if --force is specified in options
def remove_existing_item(name):
    global conn
    global c

    print("#### Remove item '{}' from table items in database".format(name))
    # remove item
    c.execute('''
        DELETE FROM items
        WHERE name='{}'
        '''.format(name))

    print("#### Remove item '{}' from table depends in database".format(name))
    # remove depends of item
    c.execute('''
        DELETE FROM depends
        WHERE name='{}'
        '''.format(name))

def add_item(args):
    global conn
    global c

    # add item
    print("#### Adding item '{}' to table items in database".format(args['name']))
    c.execute('''
        INSERT INTO items
        (name, bunch, descript)
        VALUES('{}', '{}', '{}')
        '''.format(args['name'], args['bunch'], args['descript']))

    # add item depends
    for x in args['depend']:
        print("#### Add depend '{}' <- '{}' to table depends in database".format(args['name'], x[0]))
        c.execute('''
            INSERT INTO depends
            (name, depend_name, depend_bunch)
            VALUES('{}', '{}', '{}')
            '''.format(args['name'], x[0], x[1]))

def close_db():
    global conn
    global c

    # commit connection changes
    conn.commit()

    # close cursor and db
    #print("#### Closing database")
    c.close()
    conn.close()

def list_items():
    global conn
    global c

    c.execute("SELECT name FROM items")

    items = list()
    row = c.fetchone()
    while row != None:
        items.append(row[0])
        row = c.fetchone()
    return items

def filter_items(pattern):
    global conn
    global c

    c.execute('''
        SELECT name FROM items
        WHERE name LIKE '%{}%' OR descript LIKE '%{}%'
        '''.format(pattern, pattern))

    names = list()
    row = c.fetchone()
    while row != None:
        names.append(row[0])
        row = c.fetchone()
    return names

def list_depends():
    global conn
    global c

    c.execute("SELECT name, depend_name FROM depends")

    depends = list()
    row = c.fetchone()
    while row != None:
        depends.append((row[0], row[1]))
        row = c.fetchone()
    return depends

def get_item(name):
    global conn
    global c

    item = dict()
    depends = list()
    items = list()

    c.execute('''
        SELECT bunch, descript FROM items
        WHERE name='{}'
        '''.format(name))
    row = c.fetchone()
    assert row != None and c.fetchone() == None
    item['name'] = name
    item['bunch'] = row[0]
    item['descript'] = row[1]

    c.execute('''
        SELECT depend_name, depend_bunch FROM depends
        WHERE name='{}'
        '''.format(name))
    row = c.fetchone()
    while row != None:
        depends.append((row[0], row[1]))
        row = c.fetchone()

    c.execute('''
        SELECT name FROM depends
        WHERE depend_name='{}'
        '''.format(name))
    row = c.fetchone()
    while row != None:
        items.append(row[0])
        row = c.fetchone()

    return item, depends, items
