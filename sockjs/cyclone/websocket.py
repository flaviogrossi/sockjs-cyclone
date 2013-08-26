import cyclone.websocket


class WebSocketHandler(cyclone.websocket.WebSocketHandler):
    def _execute(self, *args, **kwargs):
        if not self._closeIfInvalidMethod():
            return

        if not self._closeIfInvalidUpgradeHeader():
            return

        if not self._closeIfInvalidConnectionHeader():
            return

        super(WebSocketHandler, self)._execute(*args, **kwargs)

    def _closeIfInvalidMethod(self):
        if self.request.method != "GET":
            resp = ( "HTTP/1.1 405 Method Not Allowed\r\n"
                     "Allow: GET\r\n"
                     "Connection: Close\r\n"
                     "\r\n"
                   )
            self._writeAndClose(resp)
            return False

        return True

    def _writeAndClose(self, resp):
        self.transport.write(cyclone.escape.utf8(resp))
        self.transport.loseConnection()

    def _closeIfInvalidUpgradeHeader(self):
        if self.request.headers.get("Upgrade", "").lower() != "websocket":
            resp = ( "HTTP/1.1 400 Bad Request\r\n"
                    "Connection: Close\r\n"
                    "\r\n"
                    "Can \"Upgrade\" only to \"WebSocket\"."
                   )
            self._writeAndClose(resp)
            return False

        return True

    def _closeIfInvalidConnectionHeader(self):
        headers = self.request.headers
        connection_headers = [ s.strip().lower() for s in \
                                     headers.get("Connection", "").split(',') ]
        if "upgrade" not in connection_headers:
            resp = ( "HTTP/1.1 400 Bad Request\r\n"
                     "Connection: Close\r\n"
                     "\r\n"
                     "\"Connection\" must be \"Upgrade\"."
                   )
            self._writeAndClose(resp)
            return False

        return True
