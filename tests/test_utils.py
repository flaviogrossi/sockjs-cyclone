from twisted.trial import unittest

from sockjs.cyclone.utils import SendQueue, PriorityQueue


class PriorityQueueTest(unittest.TestCase):
    def setUp(self):
        self.q = PriorityQueue()

    def test_is_empty(self):
        self.assertTrue(self.q.is_empty())
        self.q.put(1)
        self.assertFalse(self.q.is_empty())
        self.q.pop()
        self.assertTrue(self.q.is_empty())

    def test_put_pop(self):
        self.q.put(1)
        self.assertEquals(self.q.pop(), 1)

    def test_pop_from_empty_queue_raises_indexerror(self):
        self.assertRaises(IndexError, self.q.pop)

    def test_peek_doesnt_pop(self):
        self.q.put(1)
        self.assertEquals(self.q.peek(), 1)
        self.assertFalse(self.q.is_empty())

    def test_insertion_order_is_preserved_for_same_priority_elements(self):
        class El(object):
            def __init__(self, id, val):
                self.id = id
                self.val = val

            def __cmp__(self, other):
                return cmp(self.val, other.val)

        self.q.put(El('other', 2))
        self.q.put(El('first', 1))
        self.q.put(El('second', 1))
        self.q.put(El('third', 1))

        self.assertEquals(self.q.pop().id, 'first')
        self.assertEquals(self.q.pop().id, 'second')
        self.assertEquals(self.q.pop().id, 'third')
        self.assertEquals(self.q.pop().id, 'other')


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

