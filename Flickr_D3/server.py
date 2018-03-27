import http.server
import socketserver
import sys

class ReuseAddrTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

def run_local_http_server(PORT=8000):
    Handler = http.server.SimpleHTTPRequestHandler

    with ReuseAddrTCPServer(("", PORT), Handler) as httpd:
        print("serving at port", PORT)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            httpd.shutdown()
            sys.exit()

if __name__ == '__main__':
	port = 8000
	if len(sys.argv) > 1:
		port = int(sys.argv[1])
	run_local_http_server(port)
