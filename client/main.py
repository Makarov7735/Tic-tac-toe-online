from http.server import HTTPServer, SimpleHTTPRequestHandler
import ssl


def run_server():
    httpd = HTTPServer(('localhost', 443), SimpleHTTPRequestHandler)

    httpd.socket = ssl.wrap_socket (httpd.socket, 
            keyfile='localhost-key.pem', 
            certfile='localhost.pem', server_side=True)

    httpd.serve_forever()


if __name__ == '__main__':
    try:
        run_server()
    except KeyboardInterrupt:
        exit()