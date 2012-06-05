class SockJSConnection(object):
    def __init__(self, session):
        """ Connection constructor.

        @param session: Associated session
        """
        self.session = session

    # Public API
    def connectionMade(self, request):
        """Default connectionMade() handler.

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
        """ Default on_close handler. """
        pass

    def sendMessage(self, message):
        """ Send message to the client.

        @param message: Message to send.
        """
        if not self.is_closed:
            self.session.send_message(message)

    def broadcast(self, clients, message):
        """Broadcast message to the one or more clients.
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
        """Check if connection was closed"""
        return self.session.is_closed

