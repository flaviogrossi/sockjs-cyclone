#!/usr/bin/env python

import sys
import datetime
import hashlib
import json
import random

from twisted.python import log
from twisted.internet import reactor

import cyclone.escape
import cyclone.web
import cyclone.websocket



class Application(cyclone.web.Application):
    def __init__(self):
        settings = dict(
            autoescape=None,
        )

        handlers = [
                    (r"/echo/{0,1}", GreetingsHandler),
                    (r"/echo/info", InfoHandler),
                    (r"/disabled_websocket_echo/info", InfoHandler,
                        {'websockets_enabled': False}),
                    (r"/echo/iframe[^\/]*.html", IFrameHandler),
                   ]
        cyclone.web.Application.__init__(self, handlers, **settings)


class BaseHandler(cyclone.web.RequestHandler):

    CACHE_TIME = 31536000

    def disable_cache(self):
        """Disable client-side cache for the current request"""
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, '
                        'max-age=0')

    def enable_cache(self):
        """Enable client-side caching for the current request"""
        self.set_header('Cache-Control', 'max-age={0:d}, public'.format(
                                                            self.CACHE_TIME))

        d = (datetime.datetime.now() +
             datetime.timedelta(seconds=self.CACHE_TIME))
        self.set_header('Expires', d.strftime('%a, %d %b %Y %H:%M:%S'))

        self.set_header('access-control-max-age', self.CACHE_TIME)

IFRAME_TEXT = '''<!DOCTYPE html>
<html>
<head>
  <meta http-equiv="X-UA-Compatible" content="IE=edge" />
  <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
  <script>
    document.domain = document.domain;
    _sockjs_onload = function(){SockJS.bootstrap_iframe();};
  </script>
  <script src="%s"></script>
</head>
<body>
  <h2>Don't panic!</h2>
  <p>This is a SockJS hidden iframe. It's used for cross domain magic.</p>
</body>
</html>'''.strip()

class IFrameHandler(BaseHandler):
    def get(self):
        data = IFRAME_TEXT % 'http://localhost:8888' # FIXME


        hsh = hashlib.md5(data).hexdigest()

        value = self.request.headers.get('If-None-Match')
        if value and value.find(hsh) != -1:
            # TODO: Fix me? Right now it is a hack to remove content-type
            # header
            self.clear()
            del self._headers['Content-Type']

            self.set_status(304)
            return

        self.enable_cache()
        self.set_header('Etag', hsh)
        self.write(data)


class GreetingsHandler(BaseHandler):
    def get(self):
        self.set_header("Content-Type", "text/plain; charset=UTF-8")
        self.write('Welcome to SockJS!\n')


class PreflightHandler(BaseHandler):
    """ CORS preflight handler """
    # @see: https://developer.mozilla.org/en/http_access_control

    def verify_origin(self):
        """Verify if request can be served"""
        # TODO: Verify origin
        return True

    # FIXME: asynchronous?
    def options(self):
        """XHR cross-domain OPTIONS handler"""
        self.enable_cache()
        #self.handle_session_cookie() FIXME!
        self.preflight()

        if self.verify_origin():
            allowed_methods = getattr(self, 'access_methods', 'OPTIONS, POST')
            self.set_header('Access-Control-Allow-Methods', allowed_methods)
            self.set_header('Allow', allowed_methods)

            self.set_status(204)
        else:
            # Set forbidden
            self.set_status(403)
    
    def preflight(self):
        """Handles request authentication"""
        origin = self.request.headers.get('Origin', '*')

        # Respond with '*' to 'null' origin
        if origin == 'null':
            origin = '*'

        self.set_header('Access-Control-Allow-Origin', origin)

        headers = self.request.headers.get('Access-Control-Request-Headers')
        if headers:
            self.set_header('Access-Control-Allow-Headers', headers)

        self.set_header('Access-Control-Allow-Credentials', 'true')


class InfoHandler(PreflightHandler):
    def initialize(self, websockets_enabled=True, cookie_needed=False): # FIXME
        self.websockets_enabled = websockets_enabled # FIXME
        self.cookie_needed = cookie_needed # FIXME
        self.access_methods = 'OPTIONS, GET'

    def get(self):
        self.disable_cache()
        self.set_header("Content-Type", "application/json; charset=UTF-8")

        self.preflight()

        options = { 'websocket': self.websockets_enabled,
                    'cookie_needed': self.cookie_needed,
                    'origins': ['*:*'],
                    'entropy': random.randint(0, sys.maxint)
                  }

        self.write(json.dumps(options))


if __name__ == "__main__":
    def main():
        reactor.listenTCP(8888, Application())
        reactor.run()

    log.startLogging(sys.stdout)
    main()

