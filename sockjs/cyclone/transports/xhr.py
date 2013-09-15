from twisted.python import log

from cyclone.web import asynchronous

from sockjs.cyclone import proto
from sockjs.cyclone.transports import pollingbase


class XhrPollingTransport(pollingbase.PollingTransportBase):
    """ xhr-polling transport implementation """
    name = 'xhr'

    @asynchronous
    def post(self, session_id):
        # Start response
        self.preflight()
        self.handle_session_cookie()
        self.disable_cache()

        if not self._attach_session(session_id):
            return

        # Might get already detached because connection was closed in
        # connectionMade
        if not self.session:
            return

        if self.session.send_queue.is_empty():
            self.session.start_heartbeat()
        else:
            self.session.flush()

    def connectionLost(self, reason):
        self.session.delayed_close()

    def send_pack(self, message):
        self.set_header('Content-Type', 'application/javascript; charset=UTF-8')
        self.set_header('Content-Length', len(message) + 1)
        self.write(message + '\n')

        self._detach()

        self.safe_finish()


class XhrSendHandler(pollingbase.PollingTransportBase):
    def post(self, session_id):
        self.preflight()
        self.handle_session_cookie()
        self.disable_cache()

        session = self._get_session(session_id)

        if session is None:
            self.set_status(404)
            return

        #data = self.request.body.decode('utf-8')
        data = self.request.body
        if not data:
            self.write("Payload expected.")
            self.set_status(500)
            return

        try:
            messages = proto.json_decode(data)
        except:
            # TODO: Proper error handling
            self.write("Broken JSON encoding.")
            self.set_status(500)
            return

        try:
            session.messagesReceived(messages)
        except Exception:
            log.msg('XHR incoming')
            session.close()

            self.set_status(500)
            return

        self.set_status(204)
        self.set_header('Content-Type', 'text/plain; charset=UTF-8')
