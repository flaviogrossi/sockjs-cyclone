====
CORS
====

References:
https://developer.mozilla.org/en/http_access_control

Cross-site HTTP requests initiated from within scripts have been subject to
well-known restrictions, for well-understood security reasons.  For example HTTP
Requests made using the XMLHttpRequest object were subject to the same-origin
policy.  In particular, this meant that a web application using XMLHttpRequest
could only make HTTP requests to the domain it was loaded from, and not to other
domains.

CORS provides a way for web servers to support cross-site access controls.

CORS is used to enable cross-site HTTP requests for e.g. invocations of the
XMLHttpRequest API in a cross-site manner

The Cross-Origin Resource Sharing standard works by adding new HTTP headers that
allow servers to describe the set of origins that are permitted to read that
information using a web browser.  Additionally, for HTTP request methods that
can cause side-effects on user data (in particular, for HTTP methods other than
GET, or for POST usage with certain MIME types), the specification mandates that
browsers "preflight" the request, soliciting supported methods from the server
with an HTTP OPTIONS request header, and then, upon "approval" from the server,
sending the actual request with the actual HTTP request method.  Servers can
also notify clients whether "credentials" (including Cookies and HTTP
Authentication data) should be sent with requests.


Simple requests:
the browser sends a GET request to domain bar.other for a resources loaded from
the domain foo.example. It needs to include an "Origin: http://foo.example"
header:
    GET /resources/public-data/ HTTP/1.1  
    Host: bar.other  
    User-Agent: Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; en-US; rv:1.9.1b3pre) Gecko/20081130 Minefield/3.1b3pre  
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8  
    Accept-Language: en-us,en;q=0.5  
    Accept-Encoding: gzip,deflate  
    Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.7  
    Connection: keep-alive  
    Referer: http://foo.example/examples/access-control/simpleXSInvocation.html  
    Origin: http://foo.example

the web server at bar.other then must respond with an
"Access-Control-Allow-Origin: \*" header to allow the request:
    HTTP/1.1 200 OK  
    Date: Mon, 01 Dec 2008 00:23:53 GMT  
    Server: Apache/2.0.61   
    Access-Control-Allow-Origin: *  
    Keep-Alive: timeout=2, max=100  
    Connection: Keep-Alive  
    Transfer-Encoding: chunked  
    Content-Type: application/xml  
      
    [XML Data]

if the web server wants to restrict the domain which can send the request, the
header should be "Access-Control-Allow-Origin: http://foo.example"


Preflight requests
------------------

Unlike simple requests (discussed above), "preflighted" requests first send an
HTTP OPTIONS request header to the resource on the other domain, in order to
determine whether the actual request is safe to send.

Preflight is needed if the request:
* uses methods other than GET or POST with a Content-Type other than
  text/plain, application/x-www-form-urlencoded or multipart/form-data;
* sets custom headers in the request.

A Preflight request is made before the actual request. The browser sends an
OPTION request to bar.other with the Origin header and the method to check,
using the headers "Access-Control-Request-Method: POST" and
"Access-Control-Request-Headers: X-PINGOTHER":
    OPTIONS /resources/post-here/ HTTP/1.1  
    Host: bar.other  
    User-Agent: Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; en-US; rv:1.9.1b3pre) Gecko/20081130 Minefield/3.1b3pre  
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8  
    Accept-Language: en-us,en;q=0.5  
    Accept-Encoding: gzip,deflate  
    Accept-Charset: ISO-8859-1,utf-8;q=0.7,*;q=0.7  
    Connection: keep-alive  
    Origin: http://foo.example  
    Access-Control-Request-Method: POST  
    Access-Control-Request-Headers: X-PINGOTHER

the server at bar.other respon with the allowed origin, methods and headers:
    HTTP/1.1 200 OK  
    Date: Mon, 01 Dec 2008 01:15:39 GMT  
    Server: Apache/2.0.61 (Unix)  
    Access-Control-Allow-Origin: http://foo.example  
    Access-Control-Allow-Methods: POST, GET, OPTIONS  
    Access-Control-Allow-Headers: X-PINGOTHER  
    Access-Control-Max-Age: 1728000  
    Vary: Accept-Encoding  
    Content-Encoding: gzip  
    Content-Length: 0  
    Keep-Alive: timeout=2, max=100  
    Connection: Keep-Alive  
    Content-Type: text/plain

After this preflight, the request flows as above.

