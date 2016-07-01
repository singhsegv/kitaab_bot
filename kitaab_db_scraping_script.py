# book index ranges from 1 to 7035
# update name of database and columns by your choice

from urllib2 import *
from bs4 import BeautifulSoup
import pymysql
conn = pymysql.connect(host='127.0.0.1',unix_socket='/var/run/mysqld/mysqld.sock', user='root', passwd='your password', db='mysql')
cur = conn.cursor()
cur.execute("USE books;")

def get_link(counter, fileObj):
    try:
        url = 'http://it-ebooks.info/book/%s/' % (str(counter))
        html = urlopen(url)
        bsObj = BeautifulSoup(html.read())
        heading = bsObj.find("h1", {"itemprop" : "name"})
        heading = heading.get_text()

        insert_values(str(counter), heading)
        fileObj.write('%s - %s\n' %(str(counter), heading))
        print(str(counter), heading)

    except AttributeError as e:
        print("stopped at %s" % (str(counter)))
        for i in range(counter, 7036):
            get_link(i, fileObj)

def insert_values(number, name):
    cur.execute("insert into names(number, name) values (\"%(number)s\", \"%(name)s\");" % {'number': number, 'name' : name})
    conn.commit()

fileObj = open('names.txt', 'a')

for i in range(1,7036):
    get_link(i, fileObj)

fileObj.close()
cur.close()
conn.close()
