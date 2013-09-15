from twisted.python import log

from sockjs.cyclone.transports import base
from sockjs.cyclone.session import MultiplexChannelSession


class ConnectionInfo(object):
    """ Connection information object.

    Will be passed to the C{connectionMade} handler of your connection class.

    Has few properties:

    @cvar ip: Caller IP address

    @cvar cookies: Collection of cookies

    @cvar arguments: Collection of the query string arguments

    @cvar headers: a selection of the request's headers

    @cvar path: uri's path of the request
    """

    _exposed_headers = set( ('origin', 'referer', 'x-client-ip',
                             'x-forwarded-for', 'x-cluster-client-ip')
                          )

    def __init__(self, ip, cookies, arguments, headers, path):
        self.ip = ip
        self.cookies = cookies
        self.arguments = arguments
        self.path = path
        self._expose_headers(headers)

    def _expose_headers(self, headers):
        self.headers = {}
        for header_name, header_value in headers.iteritems():
            if header_name.lower() in self._exposed_headers:
                self.headers[header_name] = header_value

    def get_header(self, name):
        """ Return a single header by name
        """
        return self.headers.get(name)

    def get_argument(self, name):
        """ Return single argument by name """
        val = self.arguments.get(name)
        if val:
            return val[0]
        return None

    def get_cookie(self, name):
        """ Return single cookie by its name """
        return self.cookies.get(name)


class SockJSConnection(object):
    def __init__(self, session):
        """ Connection constructor.

        @param session: Associated session
        """
        self.session = session

    # Public API
    def connectionMade(self, request):
        """ Default connectionMade() handler.

        Override when you need to do some initialization or request validation.
        If you return False, connection will be rejected.

        You can also throw cyclone HTTPError to close connection.

        @param request: C{ConnectionInfo} object which contains caller IP
                        address, query string parameters and cookies associated
                        with this request (if any).
        @type request: C{ConnectionInfo}
        """
        pass

    def messageReceived(self, message):
        """ Default messageReceived handler. Must be overridden in your
        application """
        raise NotImplementedError()

    def connectionLost(self):
        """ Default connectionLost handler. """
        pass

    def sendMessage(self, message):
        """ Send message to the client.

        @param message: Message to send.
        """
        if not self.is_closed:
            self.session.send_message(message)

    def broadcast(self, clients, message):
        """ Broadcast message to the one or more clients.
        Use this method if you want to send same message to lots of clients, as
        it contains several optimizations and will work fast than just having
        loop in your code.

        @param clients: Clients iterable
        @param message: Message to send
        """
        self.session.broadcast(clients, message)

    def close(self):
        self.session.close()

    @property
    def is_closed(self):
        """ Check if connection was closed """
        return self.session.is_closed


class MultiplexConnection(SockJSConnection):
    channels = {}

    def _messageSplit(self, message):
        parts = message.split(',', 2)
        if len(parts) == 3:
            return parts[0], parts[1], parts[2]
        elif len(parts) == 2:
            return parts[0], parts[1], None
        else:
            raise ValueError

    def connectionMade(self, info):
        self.endpoints = dict()
        self.handler = base.MultiplexTransport(self.session.conn_info)
    
    def messageReceived(self, message):
        try:
            msgtype, topic, payload = self._messageSplit(message)
        except ValueError:
            log.msg('invalid message received <%s>' % message)
            return

        if topic not in self.channels:
            return

        if topic in self.endpoints:
            session = self.endpoints[topic]

            if msgtype == 'uns':
                del self.endpoints[topic]
                session._close()
            elif msgtype == 'msg':
                if payload:
                    session.messageReceived(payload)
        else:
            if msgtype == 'sub':

                session_args = (self.channels[topic], self.session.server,
                                self, topic)
                session = self.session.server.create_session(
                                     session_id=None, register=False,
                                     session_factory=(MultiplexChannelSession,
                                                      session_args, {}))
                session.set_handler(self.handler)
                session.verify_state()

                self.endpoints[topic] = session

    def connectionLost(self):
        for name, session in self.endpoints.iteritems():
            session._close()

    @classmethod
    def create(cls, **connections):
        channels = dict(channels=connections)
        conn = type(cls.__name__, (cls,), channels) 
        return conn
