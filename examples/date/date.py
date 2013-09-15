import sys
import time

from twisted.python import log
from twisted.internet import task
from twisted.internet import reactor

from cyclone import web

from sockjs.cyclone import SockJSConnection
from sockjs.cyclone import SockJSRouter


class DateConnection(SockJSConnection):

    def __init__(self, *args, **kwargs):
        super(DateConnection, self).__init__(*args, **kwargs)
        timer_task = task.LoopingCall(self.send_time)
        timer_task.start(1)

    def send_time(self):
        now = time.localtime()
        self.sendMessage(time.strftime('%H:%M:%S', now))


class MainHandler(web.RequestHandler):
    def get(self):
        self.render('index.html')


class SockJsTestServer(web.Application, object):
    def __init__(self):
        settings = dict(autoescape=None)

        timerRouter = SockJSRouter(DateConnection, prefix='/timer')

        handlers = [ (r'/', MainHandler) ] + timerRouter.urls

        super(SockJsTestServer, self).__init__(handlers, **settings)


if __name__ == '__main__':
    def main():
        reactor.listenTCP(8888, SockJsTestServer())
        reactor.run()

    log.startLogging(sys.stdout)
    main()
