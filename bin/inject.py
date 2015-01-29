# Usage: mitmdump -s "iframe_injector.py url"
# (this script works best with --anticache)
from bs4 import BeautifulSoup
from libmproxy.protocol.http import decoded


def start(context, argv):
    if len(argv) != 2:
        raise ValueError('Usage: -s "inject.py url"')
    context.surl = argv[1]

def response(context, flow):
    if flow.request.host in context.surl:
        return
    with decoded(flow.response):  # Remove content encoding (gzip, ...)
        html = BeautifulSoup(flow.response.content)
        if html.body:
            script = html.new_tag("script", src=context.surl)
            html.body.insert(0, script)
            flow.response.content = str(html)
            context.log("script tag inserted.")
