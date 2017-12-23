import http.server
import socketserver
import webbrowser
import sys

class ReuseAddrTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

def run_local_http_server(PORT=8000):
    Handler = http.server.SimpleHTTPRequestHandler

    with ReuseAddrTCPServer(("", PORT), Handler) as httpd:
        print("serving at port", PORT)
        webbrowser.open('http://localhost:{}/index.html'.format(PORT))
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            httpd.shutdown()
            sys.exit()