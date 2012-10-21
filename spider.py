#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import threading
import Queue
import logging


class Spider(threading.Thread):
    """docstring for Spider"""

    # the number of workers
    worker_id = 0

    def __init__(self, work_queue, result_queue, condition,
            timeout=0, **kwds):
        threading.Thread.__init__(self, **kwds)
        self.id = Spider.worker_id
        Spider.worker_id += 1
        self.setDaemon(True)
        self.work_queue = work_queue
        self.result_queue = result_queue
        self.condition = condition
        self.timeout = timeout
        self.start()

    def run(self):
        """main loop of get-work, do-work of the spider."""
        while True:
            try:
                self.condition.acquire()

                callable, args, kwds = self.work_queue.get(timeout=self.timeout)
                logging.info("get a new task from queue")

                # get all links in the given url with specified depth
                for link,r_depth,db_connect,keyword in callable(*args, **kwds):
                    if link:
                        self.work_queue.put((callable, (link, r_depth, db_connect, keyword), {}))
                        self.condition.notifyAll()
                        logging.info("notifyAll")
                self.work_queue.task_done()
                self.condition.release()
            except Queue.Empty:
                # acquire the task_done condition of work_queue
                self.work_queue.all_tasks_done.acquire()
                # if all the task in work_queue has been done, break the main loop
                if not self.work_queue.unfinished_tasks:
                    logging.info("All task has been done")
                    self.work_queue.all_tasks_done.release()
                    self.condition.release()
                    break
                else:
                    # at least one of the spiders are processing task, while the queue is empty
                    logging.info("Queue is empty, but other threads are in procedure. wait...")
                    self.work_queue.all_tasks_done.release()
                    self.condition.wait
                    continue
