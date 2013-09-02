from twisted.internet import task, reactor

from sockjs.cyclone import transports 
from sockjs.cyclone import session
from sockjs.cyclone import sessioncontainer
from sockjs.cyclone import proto
from sockjs.cyclone import static
from sockjs.cyclone import stats


DEFAULT_SETTINGS = {
    # Sessions check interval in seconds
    'session_check_interval': 1,
    # Session expiration in seconds
    'disconnect_delay': 5,
    # Heartbeat time in seconds. Do not change this value unless
    # you absolutely sure that new value will work.
    'heartbeat_delay': 25,
    # Enabled protocols
    'disabled_transports': [],
    # SockJS location
    'sockjs_url': 'http://cdn.sockjs.org/sockjs-0.3.min.js',
    # Max response body size
    'response_limit': 128 * 1024,
    # Enable or disable JSESSIONID cookie handling
    'jsessionid': True,
    # Should sockjs-cyclone flush messages immediately or queue then and
    # flush on next reactor cycle
    'immediate_flush': True,
    # Enable or disable Nagle for persistent transports
    'disable_nagle': True,
    # Enable IP checks for polling transports. If enabled, all subsequent
    # polling calls should be from the same IP address.
    'verify_ip': True
    }

GLOBAL_HANDLERS = [
    ('xhr_send', transports.XhrSendHandler),
    ('jsonp_send', transports.JSONPSendHandler)
]

TRANSPORTS = {
    'websocket': transports.WebSocketTransport,
    'xhr': transports.XhrPollingTransport,
    'xhr_streaming': transports.XhrStreamingTransport,
    'jsonp': transports.JSONPTransport,
    'eventsource': transports.EventSourceTransport,
    'htmlfile': transports.HtmlFileTransport
}

STATIC_HANDLERS = {
    '/chunking_test': static.ChunkingTestHandler,
    '/info': static.InfoHandler,
    '/iframe[0-9-.a-z_]*.html': static.IFrameHandler,
    '/websocket': transports.RawWebSocketTransport,
    '/?': static.GreetingsHandler
}



class SockJSRouter(object):
    def __init__(self, connection, prefix='', user_settings=dict()):
        self._connection = connection

        self.settings = DEFAULT_SETTINGS.copy()
        if user_settings:
            self.settings.update(user_settings)

        disabled_transports = self.settings['disabled_transports']
        self.websockets_enabled = 'websocket' not in disabled_transports

        self.cookie_needed = self.settings['jsessionid']

        self._initialize_sessions()

        self._initialize_stats()

        self._initialize_urls(prefix)

    def _initialize_urls(self, prefix):
        base = prefix + r'/[^/.]+/(?P<session_id>[^/.]+)'

        kwargs = dict(server=self)

        self._transport_urls = []
        for handler in GLOBAL_HANDLERS:
            url = '%s/%s$' % (base, handler[0])
            reqhandler = handler[1]
            self._transport_urls.append( (url, reqhandler, kwargs) )

        for name, transport in TRANSPORTS.iteritems():
            if name in self.settings['disabled_transports']:
                continue

            # Only version 1 is supported
            url = r'%s/%s$' % (base, name)
            self._transport_urls.append((url, transport, kwargs))

        # Generate static URLs
        for name, handler in STATIC_HANDLERS.iteritems():
            url = '%s%s' % (prefix, name)
            self._transport_urls.append((url, handler, kwargs))

    def _initialize_sessions(self):
        self._sessions = sessioncontainer.SessionContainer()

        check_interval = self.settings['session_check_interval']

        self._sessions_cleanup = task.LoopingCall(self._sessions.expire)
        self._sessions_cleanup.start(check_interval)

        reactor.addSystemEventTrigger('before', 'shutdown',
                                      self._sessions_cleanup.stop)

    def _initialize_stats(self):
        self.stats = stats.StatsCollector()

    def get_connection_class(self):
        """ Return associated connection class """
        return self._connection

    @property
    def urls(self):
        return self._transport_urls

    def apply_routes(self, routes):
        """ Feed list of the URLs to the routes list. Returns list """
        routes.extend(self._transport_urls)
        return routes

    def create_session(self, session_id, register=True, session_factory=None):
        """ Creates new session object and returns it.

        @param session_id: Session id. If not provided, will generate a
                           new session id.

        @param register: Should be the session registered in a storage.
                         Websockets don't need it.

        @param session_factory: Use the given (class, args, kwargs) tuple to
                                create the session. Class should derive from
                                `BaseSession`. Normally not needed.

        """
        if session_factory is not None:
            # use custom class to create session
            sess_factory, sess_args, sess_kwargs = session_factory
            s = sess_factory(*sess_args, **sess_kwargs)
        else:
            # use default session and arguments if not using a custom session
            # factory
            s = session.Session(self._connection, self, session_id,
                                self.settings.get('disconnect_delay'))

        if register:
            self._sessions.add(s)

        return s

    def get_session(self, session_id):
        """ Get session by session id

        @param session_id: Session id
        """
        return self._sessions.get(session_id)

    # Broadcast helper
    def broadcast(self, clients, msg):
        """ Optimized C{broadcast} implementation. Depending on type of the
        session, will json-encode message once and will call either
        C{send_message} or C{send_jsonifed}.

        @param clients: Clients iterable

        @param msg: Message to send
        """
        json_msg = None

        count = 0

        for c in clients:
            sess = c.session
            if not sess.is_closed:
                if sess.send_expects_json:
                    if json_msg is None:
                        json_msg = proto.json_encode(msg)
                    sess.send_jsonified(json_msg, stats=False)
                else:
                    sess.send_message(msg, stats=False)

                count += 1

        self.stats.packSent(count)
