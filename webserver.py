import cgi

from http.server import BaseHTTPRequestHandler, HTTPServer

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Restaurant, Base, MenuItem


#Create session and connect to DB
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind = engine)
session = DBSession()


class WebServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += "<h1> Make a new restaurant</h1>"
                output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/new'>"
                output += "<input name='newrestaurantname' type='text' placeholder='New Restaurant Name'>"
                output += "<input type='submit' value='Create'>"
                output += "</body></html>"
                self.wfile.write(output.encode())
                return

            if self.path.endswith('/edit'):
                restaurantIDPath = self.path.split('/')[2]
                myRestaurantQuery = session.query(Restaurant).filter_by(id = restaurantIDPath).one()
                if myRestaurantQuery != []:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = ""
                    output = '<html><body>'
                    output += '<h1>'
                    output += str(myRestaurantQuery.name)
                    output += '</h1>'
                    output += '<form method="POST" enctype="multipart/form-data"\
                         action="/restaurants/%s/edit">' %restaurantIDPath
                    output += '<input name="newrestaurantname" type="text" placeholder=%s >' %(myRestaurantQuery.name)
                    output += '<input type="submit" value="Rename">'
                    output += '</form>'
                    output += '</body></html>'
                    self.wfile.write(output.encode())
                    return

            if self.path.endswith("/restaurants"):
                restaurants = session.query(Restaurant).all()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<a href = '/restaurants/new' > Make new restaurant here </a></br></br>"
                output += "<html><body>"
                for restaurant in restaurants:
                    output += str(restaurant.name)
                    output += "</br>"
                    output += "<a href = '/restaurants/%s/edit' > Edit </a>" % restaurant.id
                    output += "</br>"
                    output += "<a href = '/restaurants/%s/delete' > Delete </a>" % restaurant.id
                    output += "</br>"
                output += "</body></html>"
                self.wfile.write(output.encode())
                return

            if self.path.endswith('/delete'):
                restaurantIDPath = self.path.split('/')[2]
                myRestaurantQuery = session.query(Restaurant).filter_by(id = restaurantIDPath).one()
                if myRestaurantQuery != []:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    output = ""
                    output = '<html><body>'
                    output += '<h1>Are you sure you want to delete {}?</h1>'.format(str(myRestaurantQuery.name))
                    output += '<form method="POST" enctype="multipart/form-data"\
                         action="/restaurants/%s/delete">' %restaurantIDPath  
                    output += '<input type="submit" value="Delete"></form>'
                    self.wfile.write(bytes(output,'utf-8'))
                    return

            if self.path.endswith("/hello"):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                output = ""
                output += "<html><body>Hello!</body></html>"
                output += '<form method="POST" enctype="multipart/form-data" action="/restaurants/%s/delete">'%restaurantIDPath
                output += '<input type="submit" value="Delete"></form>'
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

        if self.path.endswith('/delete'):
            restaurantIDPath = self.path.split('/')[2]
            myRestaurantQuery = session.query(Restaurant).filter_by(id = restaurantIDPath).one()
            if myRestaurantQuery != []:
                session.delete(myRestaurantQuery)
                session.commit()
                self.send_response(301)
                self.send_header('Content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()
        
        if self.path.endswith('/edit'):
            ctype, pdict = cgi.parse_header(self.headers.get('Content-type'))
            pdict['boundary'] = bytes(pdict['boundary'], 'utf-8')
            content_len = int(self.headers.get("Content-length"))
            pdict['CONTENT-LENGTH'] = content_len
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('newrestaurantname')
                restaurantIDPath = self.path.split('/')[2]
                myRestaurantQuery = session.query(Restaurant).filter_by(id = restaurantIDPath).one()
                if myRestaurantQuery != []:
                    myRestaurantQuery.name = messagecontent[0]
                    session.add(myRestaurantQuery)
                    session.commit()
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()


        if self.path.endswith("/restaurants/new"):
            ctype, pdict = cgi.parse_header(self.headers.get('Content-type'))
            pdict['boundary'] = bytes(pdict['boundary'], 'utf-8')
            content_len = int(self.headers.get("Content-length"))
            pdict['CONTENT-LENGTH'] = content_len
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('newrestaurantname')
                
            #Create new restaurant class
            newRestaurant = Restaurant(name = messagecontent[0])
            session.add(newRestaurant)
            session.commit()

            self.send_response(301)
            self.send_header('Content-type', 'text/html')
            self.send_header('Location', '/restaurants')
            self.end_headers()

            # self.send_response(200)
            # self.send_header('Content-type', 'text/html')
            # self.end_headers()
            # ctype, pdict = cgi.parse_header(self.headers.get('Content-type'))
            # pdict['boundary'] = bytes(pdict['boundary'], "utf-8")
            # content_len = int(self.headers.get('Content-length'))
            # pdict['CONTENT-LENGTH'] = content_len
            # if ctype == 'multipart/form-data':
            #     fields = cgi.parse_multipart(self.rfile, pdict)
            #     messagecontent = fields.get('message')
            #     output = ''
            #     output += '<html><body>'
            #     output += '<h2> Okay, how about this: </h2>'
            #     output += '<h1> %s </h1>' % messagecontent[0]
            #     output += '<form method="POST" enctype="multipart/form-data" action="/hello">\
            #             <h2> What would you like me to say?</h2><input name="message" type="text" />\
            #             <input type="submit" value="Submit" /></form>'
            #     output += '</body></html>'
            #     self.wfile.write(bytes(output,'utf-8'))
            #     print(output)


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
