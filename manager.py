#!/usr/bin/env python

import Queue
import urllib2
import urlparse
import threading
import HTMLParser

from bs4 import BeautifulSoup

import spider

def crawl(url, depth):
    try:
        request = urllib2.Request(url)
        page = urllib2.urlopen(request)
        soup = BeautifulSoup(page)

        if depth > 0:
            for link in soup('a'):
                if ('href' in dict(link.attrs)):
                    parsed_link = urlparse.urljoin(url, link['href'])
                    # remove location portion
                    parsed_link = parsed_link.split('#')[0]

                    if parsed_link[:4] != 'http' and parsed_link[:5] != 'https':
                        continue
                    print "parsed_link: %s" % parsed_link
                    yield parsed_link, depth-1
    except urllib2.URLError, e:
        print str(e)
        yield None, None
    except HTMLParser.HTMLParseError, e:
        print str(e)
        yield None,None


class Manager():
    """docstring for Manager"""

    def __init__(self, url, depth=2, number_of_workers=10, timeout=0):
        self.work_queue = Queue.Queue()
        self.result_queue = Queue.Queue()
        self.condition = threading.Condition()
        self.workers = []
        self.timeout = timeout
        self.add_job(crawl, url, depth)
        self._add_workers(number_of_workers)

    def _add_workers(self, number_of_workers):
        """docstring for _add"""
        for i in range(number_of_workers):
            worker = spider.Spider(self.work_queue, self.result_queue,
                    self.condition, self.timeout)
            self.workers.append(worker)

    def poll(self):
        """wait for all task to be done"""
        for worker in self.workers:
                worker.join()

        print "All jobs has been done."

    def add_job(self, callable, *args, **kwds):
        """Add a new job to work_queue"""
        self.work_queue.put((callable, args, kwds))
        print "add a new job"

    def get_result(self, *args, **kwds):
        """Get a result information from result_queue"""
        self.result_queue.get(*args, **kwds)
