import sys

from twisted.internet import reactor
from twisted.internet import task
from twisted.python import log

from cyclone.web import RequestHandler, Application

from sockjs.cyclone import SockJSConnection, SockJSRouter, proto


class IndexHandler(RequestHandler):
    def get(self):
        self.render('index.html')


class StatsHandler(RequestHandler):
    def get(self):
        self.render('stats.html')


class BroadcastConnection(SockJSConnection):
    clients = set()

    def connectionMade(self, info):
        self.clients.add(self)

    def messageReceived(self, msg):
        self.broadcast(self.clients, msg)

    def connectionLost(self):
        self.clients.remove(self)


BroadcastRouter = SockJSRouter(BroadcastConnection, '/broadcast')


class StatsConnection(SockJSConnection):
    def connectionMade(self, info):
        self.loop = task.LoopingCall(self._send_stats)
        self.loop.start(1)

    def messageReceived(self):
        pass

    def connectionLost(self):
        self.loop.stop()

    def _send_stats(self):
        data = proto.json_encode(BroadcastRouter.stats.dump())
        self.sendMessage(data)


if __name__ == "__main__":
    def main():
        StatsRouter = SockJSRouter(StatsConnection, '/statsconn')

        app = Application( [ (r"/", IndexHandler),
                             (r'/stats', StatsHandler)
                           ] + BroadcastRouter.urls + StatsRouter.urls )
        reactor.listenTCP(8888, app)
        reactor.run()

    log.startLogging(sys.stdout)
    main()
