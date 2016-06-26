import time
import telepot
from urllib2 import *
from bs4 import BeautifulSoup
from pprint import pprint
import pymysql
import scrape
import os.path
import json

DOWNLOAD_PATH = '/home/rajdeep1008/Downloads/'

LOG_PATH = '/home/rajdeep1008/kitaab_bot/users/'

welcome_msg = 'Hey there %s!!\nTo start using kitaab bot (the book bot),\
 all you have to do is send the name of the book and it will\
 revert you with choices e.g., you send programming python and it will\
 respond with 125 : Programming python.\nThe next\
 step is to send /book 125 and it will automagically download and send\
 you the book.\n.If the bot is not responding, it may be due to internet\
 fault in my laptop, be patient and wait for the reply before sending a new message.\
 \nFor any help, send /help\nEnjoy ;)'

help_msg = 'Just type the book name as accurate as possible\
 to get best results. Maximum size of book telegram supports\
 as of now is 50mb so some pdfs can\'t be sent. After typing the book\
 name you will get response of the form number : name. Last step is to\
 send /book <number> without brackets with number selected from results.'

BOOK_DETAILS_LINK = 'http://it-ebooks.info/book/%s/'

def search_name(book_name):
    conn = pymysql.connect(host='127.0.0.1',
                                unix_socket='/var/run/mysqld/mysqld.sock',
                                user='root',
                                passwd='your password',
                                db='mysql')
    cur = conn.cursor()
    cur.execute("USE books;")

    query_name = '"' + '%' + book_name + '%' + '";'
    cur.execute('SELECT * FROM names where name like ' + query_name)
    result = cur.fetchall()

    cur.close()
    conn.close()
    return result

def send_list(msg, book_list):
    content_type, chat_type, chat_id = telepot.glance(msg)
    user_name = msg['from']['first_name']

    string = ''
    for number, name in book_list:
        string += number + '   :   ' + name + '\n\n'

    bot.sendMessage(chat_id, string)
    print('list sent to ' + user_name + '\n')
    save_user_logs(msg, 'list sent to ' + user_name)

def get_book_name(number):
    conn = pymysql.connect(host='127.0.0.1',
                                unix_socket='/var/run/mysqld/mysqld.sock',
                                user='root',
                                passwd='your password',
                                db='mysql')
    cur = conn.cursor()
    cur.execute("USE books;")

    query_name = number + ';'
    cur.execute('SELECT name FROM names where number = ' + query_name)
    result = cur.fetchall()

    cur.close()
    conn.close()
    return result


def send_book(msg, name):
    content_type, chat_type, chat_id = telepot.glance(msg)
    user_name = msg['from']['first_name']

    bot.sendMessage(chat_id, 'Your book has been downloaded ' + user_name + ', sending it to you now....')
    bot.sendChatAction(chat_id, 'upload_document')
    book = open(DOWNLOAD_PATH + name + '.pdf', 'rb')
    bot.sendMessage(chat_id, 'Started to upload the book, it may take some time')
    bot.sendDocument(chat_id, book)
    print('book sent to ' + user_name)

def save_user_logs(msg, message):
    user_name = msg['from']['first_name']
    final_message = json.dumps(message, sort_keys=True, indent=4, separators=(',', ': '))

    with open(LOG_PATH + user_name + '.txt', 'a') as text_file:
        text_file.write(final_message)
        text_file.write('\n')

    with open('/home/rajdeep1008/kitaab_bot/logs.txt', 'a') as log_file:
        log_file.write(final_message)
        log_file.write('\n')

def scrape_book_details(number):
    html = urlopen(BOOK_DETAILS_LINK % number)
    bsObj = BeautifulSoup(html.read(), 'html.parser')

    book_name = bsObj.find("h1", {"itemprop" : "name"}).get_text()
    book_publisher = bsObj.find("a", {"itemprop" : "publisher"}).get_text()
    book_author = bsObj.find("b", {"itemprop" : "author"}).get_text()
    book_date = bsObj.find("b", {"itemprop" : "datePublished"}).get_text()
    book_pages = bsObj.find("b", {"itemprop" : "numberOfPages"}).get_text()

    size_table = bsObj.find("b", {"itemprop" : "bookFormat"}).parent.parent.parent
    table_rows = size_table.findAll('tr')

    description = "Book name : " + book_name + "\nPublisher : " + book_publisher + \
    "\nAuthor : " + book_author + "\nDate : " + book_date + "\nPages : " + book_pages + \
    "\n" + table_rows[7].get_text() + "\nBuy original from : " + table_rows[12].a['href']

    return description

def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    user_name = msg['from']['first_name']

    if content_type == 'text':
        message = msg['text']
        pprint(msg)
        save_user_logs(msg, msg)
        if message == '/start':
            bot.sendMessage(chat_id, welcome_msg % user_name)
            save_user_logs(msg, welcome_msg % user_name)
        elif message == '/help':
            bot.sendMessage(chat_id, help_msg)
            save_user_logs(msg, help_msg)
        elif message.split(' ')[0] == '/book':
            number = str(message.split(' ')[1])
            book_name = get_book_name(number)[0][0]
            book_description = scrape_book_details(number)
            bot.sendMessage(chat_id, book_description)
            save_user_logs(msg, book_description)
            print(book_description)

            if os.path.isfile('/home/rajdeep1008/Downloads/' + book_name + '.pdf'):
                bot.sendMessage(chat_id, "Downloading your book, it may take some time\nWait for the bot to send this book before requesting any other book.")
                save_user_logs(msg, 'book already existed')
                send_book(msg, book_name)
            else:
                save_user_logs(msg, 'downloading the book')
                bot.sendMessage(chat_id, "Downloading your book, it may take some time.\nWait for the bot to send this book before requesting any other book.")
                scrape.download_book('http://it-ebooks.info/book/' + number, book_name)
                send_book(msg, book_name)

        else:
            book_list = search_name(message.lower())
            try:
                send_list(msg, book_list)
            except TelegramError as e:
                print(e)

    else:
        bot.sendMessage(chat_id, 'Please send a book name only!!')
        save_user_logs(msg, 'Error! user sent some file')


TOKEN = 'telegram bot api key'

bot = telepot.Bot(TOKEN)
bot.message_loop(handle)
print('Listening....')

while 1:
    time.sleep(5)
