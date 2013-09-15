class BaseTransportMixin(object):
    """Base transport.

    Implements few methods that session expects to see in each transport.
    """

    name = 'override_me_please'

    def get_conn_info(self):
        from sockjs.cyclone.conn import ConnectionInfo

        """ Return C{ConnectionInfo} object from current transport """
        return ConnectionInfo(self.request.remote_ip,
                              self.request.cookies,
                              self.request.arguments,
                              self.request.headers,
                              self.request.path)

    def session_closed(self):
        """ Called by the session, when it gets closed """
        pass


class MultiplexTransport(BaseTransportMixin):
    name = 'multiplex'

    def __init__(self, conn_info):
        self.conn_info = conn_info

    def get_conn_info(self):
        return self.conn_info
