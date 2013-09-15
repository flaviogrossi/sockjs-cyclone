from cyclone.web import asynchronous

from sockjs.cyclone.transports import streamingbase


class XhrStreamingTransport(streamingbase.StreamingTransportBase):
    name = 'xhr_streaming'

    @asynchronous
    def post(self, session_id):
        # Handle cookie
        self.preflight()
        self.handle_session_cookie()
        self.set_header('Content-Type', 'application/javascript; charset=UTF-8')
        self.disable_cache()

        # Send prelude and flush any pending messages
        # prelude is needed to workaround an ie8 weirdness:
        # 'http://blogs.msdn.com/b/ieinternals/archive/2010/04/06/'
        #     'comet-streaming-in-internet-explorer-with-xmlhttprequest-'
        #     'and-xdomainrequest.aspx'
        self.write('h' * 2048 + '\n')
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
        self.write(message + '\n')
        self.flush()

        # Close connection based on amount of data transferred
        if self.should_finish(len(message) + 1):
            self._detach()
            self.safe_finish()
