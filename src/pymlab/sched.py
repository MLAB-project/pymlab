#!/usr/bin/python
# -*- coding: utf-8 -*-
"""pymlab.sched module.

Author: Jan Milík <milikjan@fit.cvut.cz>
"""


import heapq
import select


class PriorityQueue(object):
    def __init__(self, items = None):
        items = list(items or [])
        self.items = heapq.heapify(items)

    def __len__(self):
        return len(self.items)

    def pop(self):
        return heapq.heappop(self.items)

    def push(self, item):
        return heapq.heappush(self.items, item)

    def peek(self):
        return self.items[0]


class Task(object):
    def __init__(self, name = None, parent = None):
        self.name   = name
        self.parent = parent

    def __str__(self):
        cls_name = type(self).__name__

        if self.name is not None:
            return "<%s %s>" % (cls_name, self.name, )
        elif self.parent is not None:
            return "<Child %s of %s>" % (cls_name, self.parent, )
        else:
            return "<%s %d>" % (cls_name, id(self), )


class Scheduler(object):
    def __init__(self):
        self.timed_tasks = PriorityQueue()
        self.once_tasks  = []
        self.read_tasks  = []

        self.interval = 500
        self._quit    = False

    def _do_timed_tasks(self):
        while len(self.timed_tasks) > 0:
            t, task, args = self.timed_tasks.peek()
            if t > time.time():
                break
            task(self, *args)
            self.timed_tasks.pop()

    def tick(self):
        once_tasks = self.once_tasks
        self.once_tasks = []

        self._do_timed_tasks()
        for task in once_tasks:
            task(self)
            self._do_timed_tasks()

        if len(self.timed_tasks) > 0:
            t, task, args = self.timed_tasks.peek()
            timeout = min(t - time.time(), self.interval)
        else:
            timeout = self.interval

        read_tasks, write_tasks, x_tasks = select.select(self.read_tasks, [], [], timeout = timeout)
        
        for read_task in read_tasks:
            self.once_tasks.append(read_task)
    
    def run(self):
        self._quit = False
        while not self._quit:
            self.tick()

    def quit(self):
        self._quit = True


def main():
    print __doc__


if __name__ == "__main__":
    main()
