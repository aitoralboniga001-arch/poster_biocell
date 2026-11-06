"""A local static server that caches like GitHub Pages (Cache-Control: max-age=600), so the browser shares one decoded
copy of each image between the loader / pre-decoder and the poster. The old no-store dev server made every
new Image() fetch and decode its own copy, which hid what the site really does once deployed.
usage: python pages_server.py <port> <root>"""
import functools, http.server, sys


class H(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'max-age=600')
        super().end_headers()

    def log_message(self, *a):  # quiet: hundreds of image requests per load
        pass


class S(http.server.ThreadingHTTPServer):
    request_queue_size = 128     # the default backlog of 5 refuses connections under the loader's parallel fetches
    daemon_threads = True


S(('127.0.0.1', int(sys.argv[1])), functools.partial(H, directory=sys.argv[2])).serve_forever()
