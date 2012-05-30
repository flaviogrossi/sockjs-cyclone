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
        self.server.stats.on_conn_opened()

        # Disable nagle if required
        if self.server.settings['disable_nagle']:
           self.transport.setTcpNoDelay(True)

        # Handle session
        self.session = self.server.create_session(session_id, register=False)

        if not self.session.set_handler(self):
            self.close()
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
                self.session.on_messages(msg)
            else:
                self.session.on_messages((msg,))
        except Exception:
            log.msg('WebSocket')

            # Close session on exception
            #self.session.close()

            # Close running connection
            self.abort_connection()

    def connectionLost(self, reason):
        # Close session if websocket connection was closed
        if self.session is not None:
            # Stats
            self.server.stats.on_conn_closed()

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

    # Websocket overrides
    # TODO: no use in cyclone
    def allow_draft76(self):
        return True

    # TODO: no use in cyclone
    def auto_decode(self):
        return False

