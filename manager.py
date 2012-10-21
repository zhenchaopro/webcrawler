#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import Queue
import urllib2
import urlparse
import threading
import sqlite3
import re
import logging
import HTMLParser
import httplib

from bs4 import BeautifulSoup

import spider

def crawl(url, depth, db_connect, keyword=None, sql="INSERT INTO MATCH_PAGE VALUES(?,?,?)"):
    try:
        request = urllib2.Request(url)
        page = urllib2.urlopen(request)
        page_charset = page.headers.getparam('charset')
        soup = BeautifulSoup(page, from_encoding=page_charset)

        # search and restore matched page into sqlite3
        cursor = db_connect.cursor()
        if keyword:
            keyword_re = re.compile(ur'.*%s.*' % keyword.decode('utf8'), re.UNICODE)
            if soup.find(text=keyword_re):
                logging.info("Find a match page.")
                cursor.execute(sql, (url, depth, unicode(soup)))
        else:
            cursor.execute(sql, (url, depth, unicode(soup)))
        cursor.close()

        if depth > 0:
            for link in soup('a'):
                if ('href' in dict(link.attrs)):
                    parsed_link = urlparse.urljoin(url, link['href'])
                    # remove location portion
                    parsed_link = parsed_link.split('#')[0]

                    if parsed_link[:4] != 'http' and parsed_link[:5] != 'https':
                        continue
                    logging.info("parsed_link: %s" % parsed_link)
                    yield parsed_link, depth-1, db_connect, keyword
    except (urllib2.URLError, HTMLParser.HTMLParseError, httplib.BadStatusLine), e:
        logging.info(str(e))
        yield None, None, None, None

class Manager():
    """docstring for Manager"""

    def __init__(self, url, db_name, depth=2, keyword=None,
            number_of_workers=10, timeout=0):
        self.work_queue = Queue.Queue()
        self.result_queue = Queue.Queue()
        self.db_connect = sqlite3.connect(db_name, isolation_level=None,
                check_same_thread=False)
        self.condition = threading.Condition()
        self.workers = []
        self.keyword = keyword
        self.timeout = timeout
        self._create_table()
        self.add_job(crawl, url, depth, self.db_connect, keyword)
        self._add_workers(number_of_workers)

    def __del__(self):
        """release db resources."""
        self.db_connect.commit()
        self.db_connect.close()

    def _create_table(self):
        """docstring for _create_table"""
        cursor = self.db_connect.cursor()
        cursor.execute("CREATE TABLE MATCH_PAGE(url TEXT,depth INTEGER, content TEXT)")
        self.db_connect.commit()
        cursor.close()

    def _add_workers(self, number_of_workers):
        """docstring for _add"""
        for i in range(number_of_workers):
            worker = spider.Spider(self.work_queue, self.result_queue,
                    self.condition, self.timeout)
            self.workers.append(worker)


    def poll(self):
        """wait for all task to be done"""
        self.work_queue.join()

        # where all the tasks have been done, there is some threads still
        # block on condition, so notifyAll
        self.condition.acquire()
        self.condition.notifyAll()
        self.condition.release()
        logging.info("manager notifyAll")

        for worker in self.workers:
                worker.join()

        logging.info("All jobs has been done.")

    def add_job(self, callable, *args, **kwds):
        """Add a new job to work_queue"""
        self.work_queue.put((callable, args, kwds))
        logging.info("add a new job")
