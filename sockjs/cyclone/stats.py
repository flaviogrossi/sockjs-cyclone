from __future__ import division

from collections import deque

from twisted.internet import task, reactor


class MovingAverage(object):
    """ Moving average class implementation """
    def __init__(self, period=10):
        """Constructor.

        @param period: Moving window size. Average will be calculated from the
                       data in the window.
        """
        self.period = period
        self.stream = deque()
        self.sum = 0
        self.accumulator = 0
        self.last_average = 0

    def add(self, n):
        """ Add value to the current accumulator

        @param n: Value to add
        """
        self.accumulator += n

    def flush(self):
        """ Add accumulator to the moving average queue and reset it. For
        example, called by the StatsCollector once per second to calculate
        per-second average.
        """
        n = self.accumulator
        self.accumulator = 0

        stream = self.stream
        stream.append(n)
        self.sum += n

        streamlen = len(stream)

        if streamlen > self.period:
            self.sum -= stream.popleft()
            streamlen -= 1

        if streamlen == 0:
            self.last_average = 0
        else:
            self.last_average = self.sum / streamlen


class StatsCollector(object):
    def __init__(self):
        # Sessions
        self.sess_active = 0

        # Avoid circular reference
        self.sess_transports = dict()

        # Connections
        self.conn_active = 0
        self.conn_ps = MovingAverage()

        # Packets
        self.pack_sent_ps = MovingAverage()
        self.pack_recv_ps = MovingAverage()

        self._callback = task.LoopingCall(self._update)
        self._callback.start(1)

        reactor.addSystemEventTrigger('before', 'shutdown', self._callback.stop)

    def _update(self):
        self.conn_ps.flush()

        self.pack_sent_ps.flush()
        self.pack_recv_ps.flush()

    def dump(self):
        """Return dictionary with current statistical information"""
        data = dict( # Sessions
                     sessions_active=self.sess_active,

                     # Connections
                     connections_active=self.conn_active,
                     connections_ps=self.conn_ps.last_average,

                     # Packets
                     packets_sent_ps=self.pack_sent_ps.last_average,
                     packets_recv_ps=self.pack_recv_ps.last_average
        )

        for k, v in self.sess_transports.iteritems():
            data['transp_' + k] = v

        return data

    # Various event callbacks
    def sessionOpened(self, transport):
        self.sess_active += 1

        if transport not in self.sess_transports:
            self.sess_transports[transport] = 0

        self.sess_transports[transport] += 1

    def sessionClosed(self, transport):
        self.sess_active -= 1
        self.sess_transports[transport] -= 1

    def connectionOpened(self):
        self.conn_active += 1
        self.conn_ps.add(1)

    def connectionClosed(self):
        self.conn_active -= 1

    def packSent(self, num):
        self.pack_sent_ps.add(num)

    def packReceived(self, num):
        self.pack_recv_ps.add(num)
