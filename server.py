#! /usr/bin/env python

import sys,os,SocketServer,signal,array
from SimpleHTTPServer import SimpleHTTPRequestHandler

import sig

def num(data_str):
    a = array.array('h')
    a.fromstring(data_str)
    s = sig.Signal(raw_signal=a)
    d = sig.Decoder(signal=s)
    bits = ''.join(str(b[0]) for b in d.bits())
    cc = ''.join(n for n in sig.cc_num(bits))
    return cc

class Server(SimpleHTTPRequestHandler):

    def do_POST(self):
        length = int(self.headers.getheader('content-length'))
        data_str = self.rfile.read(length)

        # with open('out.pcm', 'w') as out:
        #     out.write(data_str)

        try:
            response_str = num(data_str)
            print 'decoded swipe:',response_str
        except Exception as e:
            print 'ERROR: exception while decoding swipe:'
            print e.message
            try:
                response_str = num(''.join(n for n in reversed(data_str)))
                print 'reversed swipe:',response_str
            except Exception as e:
                print 'ERROR: exception while decoding REVERSED swipe:'
                print e.message
                response_str = 'ERROR: could not decode swipe'

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
