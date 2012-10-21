#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
import manager
import optparse

def main():
    parser = optparse.OptionParser()
    parser.add_option("-u", "--url", dest="url", help="Address to start with")
    parser.add_option("-d", "--depth", dest="depth", type="int", default=2, help="Crawl depth")
    parser.add_option("--thread", dest="threads_number", type="int", default=10, help="How many threads the threadpoll create")
    parser.add_option("--dbfile", dest="dbfile", help="The file name which to store matched pages")
    parser.add_option("--key", dest="key", default=None, help="Keyword")
    parser.add_option("-l", "--logfile", dest="logfile", default="spider.log", help="Application log file")
    parser.add_option("--testself", dest="testself", action="store_false", default=False, help="Application self test option.")

    (options, args) = parser.parse_args()

    option_url = options.url
    option_depth = options.depth
    option_thread = options.threads_number
    option_dbfile = options.dbfile
    option_key = options.key
    option_logfile = options.logfile
    option_testself = options.testself

    logging.basicConfig(filename=option_logfile,
            format='%(asctime)s --%(threadName)s-- %(message)s',
            level=logging.INFO)

    logging.info("webcrawler started...")
    mg = manager.Manager(option_url, option_dbfile, option_depth, option_key, option_thread)
    mg.poll()
    logging.info("webcrawler finished.")

if __name__ == '__main__':
    main()
