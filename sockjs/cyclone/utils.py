class SendQueue(object):
    """ Simple send queue. Stores messages and returns a string of all messages.
    """
    def __init__(self, separator=','):
        self.SEPARATOR = separator
        self._queue = []

    def put(self, msg):
        """ puts a new message in the queue. """
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

