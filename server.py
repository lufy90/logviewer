from http.server import HTTPServer, SimpleHTTPRequestHandler
import sys
import json
import os

from MySQLdb import _mysql

FILE_DIR="./log/"

def read_log(file, end=sys.maxsize, pagesize=sys.maxsize):
    end = int(end)
    pagesize=int(pagesize)
    with open(file,'r') as f:
        total = sum(1 for line in f)
        end = total
        start = end - pagesize if end - pagesize > 0 else 0
        f.seek(0)
        for i, line in enumerate(f):
            j = i+1
            if start<=j and j<end:
                # yield "{0:<8} {1}".format(j,line)
                yield {"no":j, "content":line, "total":total}

class LogHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        print("self.path:", self.path)
        path = self.path
        query_url = ""
        try:
            path, query_url = self.path.split("?")
        except:
            pass
        print("path:", path)
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            f = open("./index.html", "rb")
            self.wfile.write(f.read())
            f.close()
        elif self.path == "/files":
            contents = os.listdir(FILE_DIR)
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(contents).encode('utf-8'))
        elif path == "/contents":
            query_params = [i.split("=") for i in query_url.split("&")]
            print("query_params0:", query_params)
            query_params = {i[0]:i[1] for i in query_params}
            query_params["file"] = os.path.join(FILE_DIR, query_params["file"])
            print("query_params:", query_params)
            contents = list(read_log(**query_params))
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(contents).encode('utf-8'))

        else:
            self.send_response(500)

class LogServer(HTTPServer):
    def __init__(self, server_address, RequestHandlerClass=SimpleHTTPRequestHandler):
        HTTPServer.__init__(self, server_address, RequestHandlerClass)


if __name__ == "__main__":
    server = LogServer(("0.0.0.0",10000), LogHandler)
    server.serve_forever()

