from twisted.python import log

from sockjs.cyclone import websocket, session
from sockjs.cyclone.transports import base


class RawSession(session.BaseSession):
    """ Raw session without any sockjs protocol encoding/decoding.
        Simply works as a proxy between C{SockJSConnection} class and
        C{RawWebSocketTransport}. """
    def send_message(self, msg):
        self.handler.send_pack(msg)

    def on_message(self, msg):
        self.conn.on_message(msg)


class RawWebSocketTransport(websocket.WebSocketHandler, base.BaseTransportMixin):
    """ Raw Websocket transport """

    name = 'rawwebsocket'

    def initialize(self, server):
        self.server = server
        self.session = None

    def open(self):
        # Stats
        self.server.stats.on_conn_opened()

        # FIXME
        # Disable nagle if needed
        #if self.server.settings['disable_nagle']:
        #    self.stream.socket.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)

        # Create and attach to session
        self.session = RawSession(self.server.get_connection_class(), self.server)
        self.session.set_handler(self)
        self.session.verify_state()

    def _detach(self):
        if self.session is not None:
            self.session.remove_handler(self)
            self.session = None

    def on_message(self, message):
        # Ignore empty messages
        if not message or not self.session:
            return

        try:
            self.session.on_message(message)
        except Exception as e:
            log.mgs('RawWebSocketTransport: %r' % e)

            # Close running connection
            self._detach()
            self.abort_connection()

    def on_close(self):
        # Close session if websocket connection was closed
        if self.session is not None:
            # Stats
            self.server.stats.on_conn_closed()

            session = self.session
            self._detach()
            session.close()

    def connectionLost(self, reason):
        self.on_close()

    def send_pack(self, message):
        # Send message
        self.write_message(message)

    def session_closed(self):
        self.close()

    # Websocket overrides
    def allow_draft76(self):
        return True

