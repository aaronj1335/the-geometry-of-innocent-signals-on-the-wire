#! /usr/bin/env python

import sys,os,SocketServer,signal,array
from SimpleHTTPServer import SimpleHTTPRequestHandler

import sig

class Server(SimpleHTTPRequestHandler):

    def do_POST(self):
        print '**************************************** in do_POST'
        # print dir(self)
        # print self.request
        length = int(self.headers.getheader('content-length'))
        # a = array.array('h')
        # a.fromstring(self.rfile.read(length))
        # d = sig.Decoder(signal=sig.Signal(raw_signal=a))
        with open('out.pcm', 'w') as out:
            out.write(self.rfile.read(length))
        self.send_response(200, 'abc')

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
