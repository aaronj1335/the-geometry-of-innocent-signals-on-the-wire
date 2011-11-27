#! /usr/bin/env python

import sys,os,SocketServer,signal,array
from SimpleHTTPServer import SimpleHTTPRequestHandler

import sig

class Server(SimpleHTTPRequestHandler):

    def do_POST(self):
        length = int(self.headers.getheader('content-length'))
        with open('out.pcm', 'w') as out:
            out.write(self.rfile.read(length))

        response_str = 'abc 123'

        self.send_response(200)
        self.send_header("Content-Length", str(len(response_str)))
        self.send_header("Content-type", self.guess_type('abc.txt'))
        self.end_headers()

        self.wfile.write(response_str)

def handle_int(sig_num, stack_frame):
    try:
        httpd.server_close()
    except Exception as e:
        pass
signal.signal(signal.SIGINT, handle_int)

if __name__ == '__main__':

    if len(sys.argv) > 1:
        os.chdir(sys.argv[1])

    httpd = SocketServer.TCPServer(('0.0.0.0', 8080), Server)
    try:
        print 'serving up the goods'
        httpd.serve_forever()
    except Exception as e:
        httpd.server_close()
