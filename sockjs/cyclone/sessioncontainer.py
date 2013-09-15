import time

from sockjs.cyclone.utils import PriorityQueue


class SessionContainer(object):
    """ Session container object. """
    def __init__(self):
        self._items = dict()
        self._queue = PriorityQueue()

    def add(self, session):
        """ Add session to the container.

        @param session: Session object
        """
        self._items[session.session_id] = session

        if session.expiry is not None:
            self._queue.push(session)

    def get(self, session_id):
        """ Return session object or None if it is not available

        @param session_id: Session identifier
        """
        return self._items.get(session_id, None)

    def remove(self, session_id):
        """ Remove session object from the container

        @param session_id: Session identifier
        """
        session = self._items.get(session_id, None)

        if session is not None:
            session.promoted = -1
            session.on_delete(True)
            del self._items[session_id]
            return True

        return False

    def expire(self, current_time=None):
        """ Expire any old entries

        @param current_time: Optional time to be used to clean up queue (can be
                             used in unit tests)
        """
        if self._queue.is_empty():
            return

        if current_time is None:
            current_time = time.time()

        while not self._queue.is_empty():
            # Get top most item
            top = self._queue.peek()

            # Early exit if item was not promoted and its expiration time
            # is greater than now.
            if top.promoted is None and top.expiry_date > current_time:
                break

            # Pop item from the stack
            top = self._queue.pop()

            need_reschedule = (top.promoted is not None
                               and top.promoted > current_time)

            # Give chance to reschedule
            if not need_reschedule:
                top.promoted = None
                top.on_delete(False)

                need_reschedule = (top.promoted is not None
                                   and top.promoted > current_time)

            # If item is promoted and expiration time somewhere in future
            # just reschedule it
            if need_reschedule:
                top.expiry_date = top.promoted
                top.promoted = None
                self._queue.push(top)
            else:
                del self._items[top.session_id]
