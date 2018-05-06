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
    print("#### Opening database '{}'".format("./data/data.db"))
    conn = sqlite3.connect("./data/data.db")

    # get cursor
    c = conn.cursor()

    # create table items
    c.execute('''
        select name from sqlite_master
        where type='table' and name='items'
        ''')
    if c.fetchone() == None:
        print("#### Creating table '{}' in database".format('items'))
        c.execute('''
            create table items (
                name text primary key not null,
                bunch integer not null,
                descript text not null)
            ''')

    # create table depends
    c.execute('''
        select name from sqlite_master
        where type='table' and name='depends'
        ''')
    if c.fetchone() == None:
        print("#### Creating table '{}' in database".format('depends'))
        c.execute('''
            create table depends (
                name text not null,
                depend_name text not null,
                depend_bunch integer not null)
            ''')

def assert_item_exists(name):
    global conn
    global c

    c.execute('''
        select name from items 
        where name='{}'
        '''.format(name))
    if c.fetchone() == None:
        print("Item '{}' does not exist in database".format(name))
        exit(-1)

def assert_item_not_exist(name):
    global conn
    global c

    c.execute('''
        select name from items 
        where name='{}'
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
        delete from items
        where name='{}'
        '''.format(name))

    print("#### Remove item '{}' from table depends in database".format(name))
    # remove depends of item
    c.execute('''
        delete from depends
        where name='{}'
        '''.format(name))

def add_item(args):
    global conn
    global c

    # add item
    print("#### Adding item '{}' to table items in database".format(args['name']))
    c.execute('''
        insert into items
        (name, bunch, descript)
        values('{}', '{}', '{}')
        '''.format(args['name'], args['bunch'], args['descript']))

    # add item depends
    for x in args['depend']:
        print("#### Add depend '{}' <- '{}' to table depends in database".format(args['name'], x[0]))
        c.execute('''
            insert into depends
            (name, depend_name, depend_bunch)
            values('{}', '{}', '{}')
            '''.format(args['name'], x[0], x[1]))

def close_db():
    global conn
    global c

    # commit connection changes
    conn.commit()

    # close cursor and db
    print("#### Closing database")
    c.close()
    conn.close()

def list_items():
    global conn
    global c

    c.execute('''
        select name from items
        ''')

    items = list()
    row = c.fetchone()
    while row != None:
        items.append(row[0])
        row = c.fetchone()
    return items

def list_depends():
    global conn
    global c

    c.execute('''
        select name, depend_name from depends
        ''')

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
        select bunch, descript from items
        where name='{}'
        '''.format(name))
    row = c.fetchone()
    assert row != None and c.fetchone() == None
    item['name'] = name
    item['bunch'] = row[0]
    item['descript'] = row[1]

    c.execute('''
        select depend_name, depend_bunch from depends
        where name='{}'
        '''.format(name))
    row = c.fetchone()
    while row != None:
        depends.append((row[0], row[1]))
        row = c.fetchone()

    c.execute('''
        select name from depends
        where depend_name='{}'
        '''.format(name))
    row = c.fetchone()
    while row != None:
        items.append(row[0])
        row = c.fetchone()

    return item, depends, items
