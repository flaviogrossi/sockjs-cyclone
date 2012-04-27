import sys

from twisted.python import log
from twisted.internet import task
from twisted.internet import reactor

from cyclone import web

from sockjs.cyclone import SockJSConnection
from sockjs.cyclone import SockJSRouter


class CounterConnection(SockJSConnection):
    count = 0

    def __init__(self, *args, **kwargs):
        super(CounterConnection, self).__init__(*args, **kwargs)
        counter_task = task.LoopingCall(self.counter)
        counter_task.start(1)

    def counter(self):
        self.count += 1
        self.send(self.count)


class MainHandler(web.RequestHandler):
    def get(self):
        self.render('index.html')


class SockJsTestServer(web.Application, object):
    def __init__(self):
        settings = dict(autoescape=None)

        counterRouter = SockJSRouter(CounterConnection, prefix='/counter')

        handlers = [ (r'/', MainHandler) ] + counterRouter.urls

        super(SockJsTestServer, self).__init__(handlers, **settings)


if __name__ == '__main__':
    def main():
        reactor.listenTCP(8888, SockJsTestServer())
        reactor.run()

    log.startLogging(sys.stdout)
    main()

