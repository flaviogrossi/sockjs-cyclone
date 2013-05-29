import heapq
import itertools


class SendQueue(object):
    """ Simple send queue. Stores messages and returns a string of all messages.
    """
    def __init__(self, separator=','):
        self.SEPARATOR = separator
        self._queue = []

    def push(self, msg):
        """ pushes a new message in the queue. """
        self._queue.append(msg)

    def get(self):
        """ returns enqueued messages in a single string, separator-joined """
        return self.SEPARATOR.join(self._queue)
    
    def clear(self):
        """ empties the queue. """
        self._queue = []

    def is_empty(self):
        """ check if the queue is empty. """
        return not self._queue


class PriorityQueue(object):
    """ Simplistic priority queue.
    """
    def __init__(self):
        self._queue = []

        self.counter = itertools.count()   # needed to preserve insertion order
                                           # in elements with the same priority

    def push(self, el):
        """ Put a new element in the queue. """
        count = next(self.counter)
        heapq.heappush(self._queue, (el, count))

    def peek(self):
        """ Returns the highest priority element from the queue without
        removing it. """
        return self._queue[0][0]
    
    def pop(self):
        """ Remove and returns the highest priority element form the queue. """
        return heapq.heappop(self._queue)[0]

    def is_empty(self):
        """ Checks if the queue is empty. """
        return not self._queue
    
    def __contains__(self, el):
        return el in ( e[0] for e in self._queue )

    def __len__(self):
        return len(self._queue)
