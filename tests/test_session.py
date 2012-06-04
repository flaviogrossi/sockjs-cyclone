from twisted.trial import unittest

from sockjs.cyclone import session


class ConnectionInfoTest(unittest.TestCase):

    def test_instantiate(self):
        session.ConnectionInfo(None, None, None)
    
    def test_get_cookie(self):
        c = session.ConnectionInfo(None, dict(cookie='mycookie'), None)
        self.assertEquals(c.get_cookie('cookie'), 'mycookie')

    def test_get_cookie_returns_None_on_not_found(self):
        c = session.ConnectionInfo(None, dict(), None)
        self.assertIsNone(c.get_cookie('cookie'))


    def test_get_argument(self):
        c = session.ConnectionInfo(None, None, dict(arg=('myarg', '')))
        self.assertEquals(c.get_argument('arg'), 'myarg')

    def test_get_argument_returns_None_on_not_found(self):
        c = session.ConnectionInfo(None, None, dict())
        self.assertIsNone(c.get_argument('arg'))

