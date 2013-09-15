import urllib

from cyclone.web import asynchronous

from twisted.python import log

from sockjs.cyclone import proto
from sockjs.cyclone.transports import pollingbase


class JSONPTransport(pollingbase.PollingTransportBase):
    name = 'jsonp'

    @asynchronous
    def get(self, session_id):                                                  
        # Start response                                                        
        self.handle_session_cookie()                                            
        self.disable_cache()                                                    
                                                                                
        # Grab callback parameter                                               
        self.callback = self.get_argument('c', None)                            
        if not self.callback:                                                   
            self.write('"callback" parameter required')                         
            self.set_status(500)                                                
            self.finish()                                                       
            return                                                              

        # Get or create session without starting heartbeat
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
        # TODO: Just escape
        msg = '%s(%s);\r\n' % (self.callback, proto.json_encode(message))

        self.set_header('Content-Type',
                        'application/javascript; charset=UTF-8')
        self.set_header('Content-Length', len(msg))

        # FIXME
        self.set_header('Etag', 'dummy')

        self.write(msg)

        self._detach()

        self.safe_finish()


class JSONPSendHandler(pollingbase.PollingTransportBase):
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

        ctype = self.request.headers.get('Content-Type', '').lower()
        if ctype == 'application/x-www-form-urlencoded':
            if not data.startswith('d='):
                log.msg('jsonp_send: Invalid payload.')

                self.write("Payload expected.")
                self.set_status(500)
                return

            data = urllib.unquote_plus(data[2:])

        if not data:
            log.msg('jsonp_send: Payload expected.')

            self.write("Payload expected.")
            self.set_status(500)
            return

        try:
            messages = proto.json_decode(data)
        except:
            # TODO: Proper error handling
            log.msg('jsonp_send: Invalid json encoding')

            self.write("Broken JSON encoding.")
            self.set_status(500)
            return

        try:
            session.messagesReceived(messages)
        except Exception:
            log.msg('jsonp_send: messagesReceived() failed')

            session.close()

            self.write('Message handler failed.')
            self.set_status(500)
            return

        self.write('ok')
        self.set_header('Content-Type', 'text/plain; charset=UTF-8')
        self.set_status(200)
