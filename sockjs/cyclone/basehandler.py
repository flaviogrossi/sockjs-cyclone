""" Various base http handlers """

import datetime

from cyclone.web import asynchronous, RequestHandler


class BaseHandler(RequestHandler):
    """ Base request handler with set of helpers."""

    CACHE_TIME = 31536000


    def initialize(self, server):
        """ Initialize request

        @param server: SockJSRouter instance.

        """
        self.server = server
        self.logged = False

    # Statistics
    def prepare(self):
        """ Increment connection count """
        self.logged = True
        self.server.stats.connectionOpened()

    def _log_disconnect(self):
        """ Decrement connection count """
        if self.logged:
            self.server.stats.connectionClosed()
            self.logged = False

    def finish(self):
        """ Cyclone C{finish} handler """
        self._log_disconnect()

        super(BaseHandler, self).finish()

    def on_connection_close(self, reason):
        self._log_disconnect()

    # Various helpers
    def enable_cache(self):
        """ Enable client-side caching for the current request """
        self.set_header('Cache-Control', 'max-age=%d, public' % self.CACHE_TIME)

        now = datetime.datetime.now()
        expires = now + datetime.timedelta(seconds=self.CACHE_TIME)
        self.set_header('Expires', expires.strftime('%a, %d %b %Y %H:%M:%S'))

        self.set_header('access-control-max-age', self.CACHE_TIME)

    def disable_cache(self):
        """ Disable client-side cache for the current request """
        self.set_header('Cache-Control',
                        'no-store, no-cache, must-revalidate, max-age=0')

    def handle_session_cookie(self):
        """ Handle JSESSIONID cookie logic """
        # If JSESSIONID support is disabled in the settings, ignore cookie logic
        if not self.server.settings['jsessionid']:
            return

        cookie = self.cookies.get('JSESSIONID')

        if not cookie:
            cv = 'dummy'
        else:
            cv = cookie.value

        self.set_cookie('JSESSIONID', cv)

    def safe_finish(self):
        """ Finish session safely (do not raise if already finished by a dropped
        connection). """
        try:
            self.finish()
        except Exception:
            pass


class PreflightHandler(BaseHandler):
    """ CORS preflight handler """

    @asynchronous
    def options(self, *args, **kwargs):
        """ XHR cross-domain OPTIONS handler """
        self.enable_cache()
        self.handle_session_cookie()
        self.preflight()

        if self.verify_origin():
            allowed_methods = getattr(self, 'access_methods', 'OPTIONS, POST')
            self.set_header('Access-Control-Allow-Methods', allowed_methods)
            self.set_header('Allow', allowed_methods)

            self.set_status(204)
        else:
            # Set forbidden
            self.set_status(403)

        self.finish()

    def preflight(self):
        """ Handles request authentication """
        origin = self.request.headers.get('Origin', '*')

        # 'null' may be sent by the browser when the sockjs client is hosted
        # from a file:// url.
        # In such case, respond with '*' to 'null' origin, as per sockjs
        # protocol definition
        if origin == 'null':
            origin = '*'

        self.set_header('Access-Control-Allow-Origin', origin)

        headers = self.request.headers.get('Access-Control-Request-Headers')
        if headers:
            self.set_header('Access-Control-Allow-Headers', headers)

        self.set_header('Access-Control-Allow-Credentials', 'true')

    def verify_origin(self):
        """ Verify if request can be served """
        # TODO: Verify origin
        return True
