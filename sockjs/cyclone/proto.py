import simplejson

json_encode = lambda data: simplejson.dumps(data, separators=(',', ':'))
json_decode = lambda data: simplejson.loads(data)
JSONDecodeError = ValueError

# Protocol handlers
CONNECT = 'o'
DISCONNECT = 'c'
MESSAGE = 'm'
HEARTBEAT = 'h'


# Various protocol helpers
def disconnect(code, reason):
    """Return SockJS packet with code and close reason

    @param code: Closing code
    @param reason: Closing reason
    """
    return 'c[%d,"%s"]' % (code, reason)
