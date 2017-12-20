import http.server
import socketserver
import webbrowser

def run_local_http_server(PORT=8000):
	Handler = http.server.SimpleHTTPRequestHandler

	with socketserver.TCPServer(("", PORT), Handler) as httpd:
	    print("serving at port", PORT)
	    webbrowser.open('http://localhost:{}/index.html'.format(PORT))
	    httpd.serve_forever()