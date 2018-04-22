
import sys
import os

import sqlite3

from configs import *



def main():
    # assert python version is 3
    if sys.version_info.major < 3:
        print("This script only runs in python3")
        return

    # create data directory
    if not os.path.isdir("./data"):
        os.makedirs("./data")
        if not os.path.isdir("./data"):
            print("Failed to create data path './data'")
            return

    # open db
    conn = sqlite3.connect("./data/data.db")

    # get cursor
    c = conn.cursor()

    # create table
    c.execute('''
        select name from sqlite_master
        where type='table' and name='wallpapers'
        ''')
    if c.fetchone() == None:
        c.execute('''
            create table wallpapers (
                id integer primary key autoincrement not null,
                image_date text not null,
                url_base text not null,
                copyright text not null)
            ''')

    # insert record
    c.execute('''
        insert into wallpapers (image_date, url_base, copyright)
        values ('aa', 'bb', 'cc')
        ''')

    # query records
    c.execute("select * from wallpapers order by id desc limit 0,10")
    print(c.fetchall())

    # commit connection changes
    conn.commit()

    # close cursor and db
    c.close()
    conn.close()


if __name__ == "__main__":
    main()
