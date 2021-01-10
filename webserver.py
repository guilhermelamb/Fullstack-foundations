from http.server import BaseHTTPRequestHandler, HTTPServer
import cgi


class WebServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:

            if self.path.endswith("/hello"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>Hello!</body></html>"
                output += '<form method="POST" enctype="multipart/form-data" action="/hello">\
                        <h2> What would you like me to say?</h2><input name="message" type="text" />\
                        <input type="submit" value="Submit" /></form>'
                output += "</body></html>"
                self.wfile.write(output.encode())
                print(output)
                return
            if self.path.endswith("/oi"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>Oi!</body></html>"
                output += '<form method="POST" enctype="multipart/form-data" action="/hello">\
                        <h2> What would you like me to say?</h2><input name="message" type="text" />\
                        <input type="submit" value="Submit" /></form>'
                output += "</body></html>"
                self.wfile.write(output.encode())
                print(output)
                return
        except IOError:
            self.send_error(404, "File not found: %s" %self.path)
    


    def do_POST(self):
        try:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            ctype, pdict = cgi.parse_header(self.headers.get('Content-type'))
            pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
            content_len = int(self.headers.get('Content-length'))
            pdict['CONTENT-LENGTH'] = content_len
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('message')
                output = ''
                output += '<html><body>'
                output += '<h2> Okay, how about this: </h2>'
                output += '<h1> %s </h1>' % messagecontent[0]
                output += '<form method="POST" enctype="multipart/form-data" action="/hello">\
                        <h2> What would you like me to say?</h2><input name="message" type="text" />\
                        <input type="submit" value="Submit" /></form>'
                output += '</body></html>'
                self.wfile.write(bytes(output,'utf-8'))
                print(output)
        except:
            pass

def main():
    try:
        port = 8080
        server = HTTPServer(('', port), WebServerHandler)
        print("Web server running on port %s" % port)
        server.serve_forever()
    except KeyboardInterrupt:
        print("^C entered, stop running server...")
        server.socket.close()

if __name__ == '__main__':
    main()
