from cyclone.web import asynchronous

from sockjs.cyclone.transports import streamingbase


class EventSourceTransport(streamingbase.StreamingTransportBase):
    name = 'eventsource'

    @asynchronous
    def get(self, session_id):
        # Start response
        self.preflight()
        self.handle_session_cookie()
        self.disable_cache()

        self.set_header('Content-Type', 'text/event-stream; charset=UTF-8')
        self.write('\r\n')
        self.flush()

        if not self._attach_session(session_id):
            self.finish()
            return

        if self.session:
            self.session.flush()

    def connectionLost(self, reason):
        self.session.delayed_close()
        self._detach()

    def send_pack(self, message):
        msg = 'data: %s\r\n\r\n' % message

        self.write(msg)
        self.flush()

        # Close connection based on amount of data transferred
        if self.should_finish(len(msg)):
            self._detach()
            self.safe_finish()
