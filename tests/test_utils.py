from twisted.trial import unittest

from sockjs.cyclone.utils import SendQueue


class SendQueueTest(unittest.TestCase):

    def test_single_value_doesnt_use_separator(self):
        q = SendQueue()
        q.put('xxx')
        self.assertFalse(q.SEPARATOR in q.get())

    def test_two_values_use_separator(self):
        q = SendQueue()
        one = 'one'
        two = 'two'
        q.put(one)
        q.put(two)

        self.assertEquals(q.get(), '%s%s%s' % (one, q.SEPARATOR, two))

    def test_is_empty(self):
        q = SendQueue()
        self.assertTrue(q.is_empty())
        q.put('x')
        self.assertFalse(q.is_empty())
        q.clear()
        self.assertTrue(q.is_empty())

    def test_can_clear_empty_queue(self):
        q = SendQueue()
        q.clear()

    def test_can_clear_non_empty_queue(self):
        q = SendQueue()
        q.put('x')
        q.clear()
        self.assertTrue(q._queue == [])

    def test_can_personalize_separator(self):
        sep = '+'
        q = SendQueue(separator=sep)
        value = '1+2+3'
        for i in value.split('+'):
            q.put(i)
        self.assertEquals(q.get(), value)

