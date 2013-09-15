from twisted.python import log

from sockjs.cyclone import session
from sockjs.cyclone.transports import base
from sockjs.cyclone import websocket


class RawSession(session.BaseSession):
    """ Raw session without any sockjs protocol encoding/decoding.
        Simply works as a proxy between C{SockJSConnection} class and
        C{RawWebSocketTransport}. """
    def send_message(self, msg, stats=True):
        self.handler.send_pack(msg)

    def messageReceived(self, msg):
        self.conn.messageReceived(msg)


class RawWebSocketTransport(websocket.WebSocketHandler, base.BaseTransportMixin):
    """ Raw Websocket transport """

    name = 'rawwebsocket'

    def initialize(self, server):
        self.server = server
        self.session = None

    def connectionMade(self):
        # Stats
        self.server.stats.connectionOpened()

        # Disable nagle if required
        if self.server.settings['disable_nagle']:
            self.transport.setTcpNoDelay(True)

        # Create and attach to session
        session_args = ( self.server.get_connection_class(), self.server )
        self.session = self.server.create_session(
                                session_id=None, register=False,
                                session_factory=(RawSession, session_args, {}))
        self.session.set_handler(self)
        self.session.verify_state()

    def _detach(self):
        if self.session is not None:
            self.session.remove_handler(self)
            self.session = None

    def messageReceived(self, message):
        # Ignore empty messages
        if not message or not self.session:
            return

        try:
            self.session.messageReceived(message)
        except Exception as e:
            log.msg('RawWebSocketTransport.messageReceived: %r' % e)

            # Close running connection
            self._detach()
            self.transport.loseConnection()

    def connectionLost(self, reason):
        # Close session if websocket connection was closed
        if self.session is not None:
            # Stats
            self.server.stats.connectionClosed()

            session = self.session
            self._detach()
            session.close()

    def send_pack(self, message):
        # Send message
        self.sendMessage(message)

    def session_closed(self):
        self.transport.loseConnection()
        self._detach()
