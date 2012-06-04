from twisted.trial import unittest

from sockjs.cyclone.sessioncontainer import SessionContainer

class SessionFake(object):
    def __init__(self, session_id=None):
        self.session_id = session_id or 1
        self.expiry = None
        self.promoted = None

        self._delete_called = False

    def on_delete(self, *args, **kwargs):
        self._delete_called = True

class SessionContainerTest(unittest.TestCase):

    def setUp(self):
        self.sc = SessionContainer()
        self.session = SessionFake()

    def _check_session_is_in_items(self, session=None, sessioncontainer=None):
        session = session or self.session
        sessioncontainer = sessioncontainer or self.sc
        return session.session_id in sessioncontainer._items.keys()

    def _check_session_is_in_queue(self, session=None, sessioncontainer=None):
        session = session or self.session
        sessioncontainer = sessioncontainer or self.sc
        return session in sessioncontainer._queue

    def test_add_session(self):
        self.sc.add(self.session)

        self.assertTrue(self._check_session_is_in_items())

    def test_add_session_with_expiry(self):
        self.session.expiry = 10

        self.sc.add(self.session)

        self.assertTrue(self._check_session_is_in_items())

    def test_get(self):
        self.sc.add(self.session)

        self.assertTrue(self.sc.get(self.session.session_id) is self.session)

    def test_get_wrong_session_id_returns_None(self):
        self.assertTrue(self.sc.get(42) is None)

    def test_remove(self):
        self.sc.add(self.session)

        res = self.sc.remove(self.session.session_id)
        self.assertTrue(res)

        self.assertFalse(self._check_session_is_in_items())

    def test_remove_calls_session_on_delete(self):
        self.sc.add(self.session)

        self.assertFalse(self.session._delete_called)
        self.sc.remove(self.session.session_id)
        self.assertTrue(self.session._delete_called)

    def test_remove_on_non_existing_session_returns_False(self):
        res = self.sc.remove(42)
        self.assertFalse(res)

    def test_expire_with_no_sessions_doesnt_raise(self):
        self.sc.remove(42)

    def test_expire_does_nothing_if_no_sessions_are_expired(self):
        sessions = [ SessionFake() for i in range(10) ]
        for index, s in enumerate(sessions):
            s.session_id = index
            s.expiry = 10
            s.expiry_date = 10
            self.sc.add(s)

        self.sc.expire(current_time=0)

        for s in sessions:
            self.assertTrue(self._check_session_is_in_items(session=s))
            self.assertTrue(self._check_session_is_in_queue(session=s))

    def test_expire_sessions(self):
        sessions = [ SessionFake() for i in range(10) ]
        for index, s in enumerate(sessions):
            s.session_id = index
            s.expiry = index
            s.expiry_date = index
            self.sc.add(s)

        now = 5
        self.sc.expire(current_time=now)

        for s in sessions:
            if s.expiry_date > now:
                self.assertTrue(self._check_session_is_in_items(session=s))
                self.assertTrue(self._check_session_is_in_queue(session=s))
            else:
                self.assertFalse(self._check_session_is_in_items(session=s))
                self.assertFalse(self._check_session_is_in_queue(session=s))

    def test_promotion_delays_expiration(self):
        self.session.expiry = 1
        self.session.expiry_date = 1
        self.session.promoted = 10

        self.sc.add(self.session)

        self.sc.expire(current_time=5)

        self.assertTrue(self._check_session_is_in_items())
        self.assertTrue(self._check_session_is_in_queue())
    
    def test_on_delete_can_delay_expiration(self):
        self.session.expiry = 1
        self.session.expiry_date = 1

        def promote(self, forced):
            self.promoted = 10
        from types import MethodType
        self.session.on_delete = MethodType(promote, self.session, SessionFake)

        self.sc.add(self.session)

        self.sc.expire(current_time=5)

        self.assertTrue(self._check_session_is_in_items())
        self.assertTrue(self._check_session_is_in_queue())

