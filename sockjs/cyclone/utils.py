class SendQueue(object):
    def __init__(self):
        self.SEPARATOR = ','
        self._queue = []

    def put(self, msg):
        self._queue.append(msg)

    def get(self):
        return self.SEPARATOR.join(self._queue)
    
    def clear(self):
        self._queue = []

    def is_empty(self):
        return not self._queue

