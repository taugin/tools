#!/bin/env python
# -*- coding:utf-8 -*-

"""
@lx
created on 2016-04-14
"""

import queue
import sys
import threading
import time
import io
import traceback
import os

class MyThread(threading.Thread):
    """Background thread connected to the requests/results queues."""
    def __init__(self, workQueue, resultQueue, timeout=0.1, **kwds):
        threading.Thread.__init__(self, **kwds)
        self.setDaemon(True)
        self._workQueue = workQueue
        self._resultQueue = resultQueue
        self._timeout = timeout
        self._dismissed = threading.Event()
        self.start()

    def run(self):
        """Repeatedly process the job queue until told to exit."""
        while True:
            if self._dismissed.isSet():
                break

            handlerKey = None  # unique key
            code = 0  # callback return code
            handlerRet = None
            errMsg = ""

            try:
                callable, args, kwds = self._workQueue.get(True, self._timeout)
            except queue.Empty:
                continue
            except:
                exceptMsg = io.StringIO()
                traceback.print_exc(file=exceptMsg)
                errMsg = exceptMsg.getvalue()
                code = 3301  # system error
                self._resultQueue.put(
                        (handlerKey, code, (callable, args, kwds), errMsg))
                break

            if self._dismissed.isSet():
                self._workQueue.put((callable, args, kwds))
                break

            try:
                if "handlerKey" in kwds:
                    handlerKey = kwds["handlerKey"]
                handlerRet = callable(*args, **kwds)  # block
                self._resultQueue.put((handlerKey, code, handlerRet, errMsg))
            except:
                exceptMsg = io.StringIO()
                traceback.print_exc(file=exceptMsg)
                errMsg = exceptMsg.getvalue()
                code = 3303
                self._resultQueue.put((handlerKey, code, handlerRet, errMsg))

    def dismiss(self):
        """Sets a flag to tell the thread to exit when done with current job."""
        self._dismissed.set()


class ThreadPool(object):
    def __init__(self, workerNums=3, timeout=0.1):
        self._workerNums = workerNums
        self._timeout = timeout
        self._workQueue = queue.Queue()  # no maximum
        self._resultQueue = queue.Queue()
        self.workers = []
        self.dismissedWorkers = []
        self._createWorkers(self._workerNums)

    def _createWorkers(self, workerNums):
        """Add num_workers worker threads to the pool."""
        for i in range(workerNums):
            worker = MyThread(self._workQueue, self._resultQueue,
                              timeout=self._timeout)
            self.workers.append(worker)

    def _dismissWorkers(self, workerNums, _join=False):
        """Tell num_workers worker threads to quit after their current task."""
        dismissList = []
        for i in range(min(workerNums, len(self.workers))):
            worker = self.workers.pop()
            worker.dismiss()
            dismissList.append(worker)

        if _join:
            for worker in dismissList:
                worker.join()
        else:
            self.dismissedWorkers.extend(dismissList)

    def _joinAllDissmissedWorkers(self):
        """
        Perform Thread.join() on all
        worker threads that have been dismissed.
        """
        for worker in self.dismissedWorkers:
            worker.join()
        self.dismissedWorkers = []

    def addJob(self, callable, *args, **kwds):
        self._workQueue.put((callable, args, kwds))

    def getResult(self, block=False, timeout=0.1):
        try:
            item = self._resultQueue.get(block, timeout)
            return item
        except queue.Empty as e:
            return None
        except:
            raise

    def waitForComplete(self, timeout=0.1):
        """
        Last function. To dismiss all worker threads. Delete ThreadPool.
        :param timeout
        """
        while True:
            workerNums = self._workQueue.qsize()  # 释放掉所有线程
            runWorkers = len(self.workers)

            if 0 == workerNums:
                time.sleep(timeout)  # waiting for thread to do job 
                self._dismissWorkers(runWorkers)
                break
            # if workerNums < runWorkers:  # 不能这样子乱取消
            #     self._dismissWorkers(runWorkers - workerNums)
            time.sleep(timeout)
        self._joinAllDissmissedWorkers()

    def workSize(self):
        '''返回剩余任务数量'''
        return self._workQueue.qsize()

if "__main__" == __name__:
    def doSomething_(*args, **kwds):
        sleep = int(args[0])
        msgTxt = "sleep %ds.." % sleep
        time.sleep(sleep)
        return msgTxt


    wm = ThreadPool(10)
    result = []
    for i in range(10):
        data = 5
        wm.addJob(doSomething_, data)

    while 1:
        res = wm.getResult()
        if res:
            result.append(res)
        if 10 == len(result):
            break
        print ("sleep 0.1")
        time.sleep(0.1)
    print (time.time())
    wm.waitForComplete()
    print (time.time())