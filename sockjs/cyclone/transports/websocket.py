#import socket

from twisted.python import log

from sockjs.cyclone import proto
from sockjs.cyclone.transports import base
from sockjs.cyclone import websocket


class WebSocketTransport(websocket.WebSocketHandler, base.BaseTransportMixin):
    """ Websocket transport """
    name = 'websocket'

    def initialize(self, server):
        self.server = server
        self.session = None

    def connectionMade(self, session_id):
        # Stats
        self.server.stats.connectionOpened()

        # Disable nagle if required
        if self.server.settings['disable_nagle']:
           self.transport.setTcpNoDelay(True)

        # Handle session
        self.session = self.server.create_session(session_id, register=False)

        if not self.session.set_handler(self):
            self.transport.loseConnection()
            return

        self.session.verify_state()

        if self.session:
            self.session.flush()

    def _detach(self):
        if self.session is not None:
            self.session.remove_handler(self)
            self.session = None

    def messageReceived(self, message):
        # Ignore empty messages
        if not message or not self.session:
            return

        try:
            msg = proto.json_decode(message)

            if isinstance(msg, list):
                self.session.messagesReceived(msg)
            else:
                self.session.messagesReceived((msg,))
        except Exception as e:
            log.msg('WebSocketTransport.messageReceived: %r' % e)

            # Close running connection
            self.transport.loseConnection()

    def connectionLost(self, reason):
        # Close session if websocket connection was closed
        if self.session is not None:
            # Stats
            self.server.stats.connectionClosed()

            # Detach before closing session
            session = self.session
            self._detach()
            session.close()

    def send_pack(self, message):
        self.sendMessage(message)

    def session_closed(self):
        # If session was closed by the application, terminate websocket
        # connection as well.
        self.transport.loseConnection()
        self._detach()

    # TODO: no use in cyclone
    def auto_decode(self):
        return False
