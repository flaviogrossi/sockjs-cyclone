from twisted.trial import unittest

from sockjs.cyclone.session import SessionMixin
from sockjs.cyclone.conn import ConnectionInfo


class ConnectionInfoTest(unittest.TestCase):

    def test_get_cookie(self):
        c = ConnectionInfo(None, dict(cookie='mycookie'), None, {}, None)
        self.assertEquals(c.get_cookie('cookie'), 'mycookie')

    def test_get_cookie_returns_None_on_not_found(self):
        c = ConnectionInfo(None, dict(), None, {}, None)
        self.assertTrue(c.get_cookie('cookie') is None)


    def test_get_argument(self):
        c = ConnectionInfo(None, None, dict(arg=('myarg', '')), {}, None)
        self.assertEquals(c.get_argument('arg'), 'myarg')

    def test_get_argument_returns_None_on_not_found(self):
        c = ConnectionInfo(None, None, dict(), {}, None)
        self.assertTrue(c.get_argument('arg') is None)

    def test_dont_expose_unknown_headers(self):
        c = ConnectionInfo(None, None, {}, {'StrangeHeader': '42'}, None)
        self.assertTrue(c.get_header('StrangeHeader') is None)

    def test_expose_whitelisted_headers(self):
        headers = dict((h, '42') for h in ConnectionInfo._exposed_headers)
        c = ConnectionInfo(None, None, {}, headers, None)
        for h in headers.keys():
            self.assertTrue(c.get_header(h) is not None)


class TimeMock(object):
    def __init__(self, returned_time):
        self.returned_time = returned_time
    def set(self, time):
        self.returned_time = time
    def time(self):
        return self.returned_time


class SessionMixinTest(unittest.TestCase):
    def test_repr(self):
        s = SessionMixin()
        s.expiry_date = 10
        s.session_id = 42
        s.promoted = 1
        self.assertTrue(str(s.expiry_date) in repr(s))
        self.assertTrue(str(s.session_id) in repr(s))
        self.assertTrue(str(s.expiry_date) in repr(s))

    def test_repr_with_no_expiry_date(self):
        s = SessionMixin()
        self.assertTrue('-1' in repr(s))

    def test_repr_with_unpromoted_session(self):
        s = SessionMixin()
        s.promoted = None
        self.assertTrue('0' in repr(s))

    def test_creation_with_no_sid_sets_a_random_one(self):
        s = SessionMixin()
        self.assertTrue(s.session_id is not None)

    def test_creation_with_expiry_arg_also_sets_expiry_date(self):
        s = SessionMixin(expiry=42)
        self.assertTrue(s.expiry_date is not None)

    def test_is_alive_correctly_handles_expiration(self):
        time = TimeMock(0)

        s = SessionMixin(expiry=42, time_module=time)
        self.assertTrue(s.is_alive())

        s = SessionMixin(expiry=42, time_module=time)
        time.set(43)
        self.assertFalse(s.is_alive())

    def test_promote(self):
        time = TimeMock(42)

        s = SessionMixin(expiry=10, time_module=time)
        s.promote()
        self.assertEquals(s.expiry_date, 52)

    def test_cmp(self):
        def session_factory(expiry):
            time = TimeMock(0)
            return SessionMixin(expiry=expiry, time_module=time)
        self.assertTrue( session_factory(10) == session_factory(10) )
        self.assertTrue( session_factory(9) < session_factory(10) )
        self.assertTrue( session_factory(11) > session_factory(10) )

