#  coding: utf-8 
import socketserver
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        self.reroute = False
        print ("\n\nGot a request of: %s" % self.data)
        self.path = self.create_path()
        self.check_path()
        # self.request.sendall(bytearray("OK",'utf-8'))
        
    def create_path(self):
        self.link = self.data.decode("utf-8").split(" ")
        if ("www" in self.link[1]):
            self.reroute = True
            path =  "." + self.link[1]
        else:
            path = './www' + self.link[1]
            
        print(path)
        return path
    
    def get_content_type(self):
        if "css" in self.link[1]:
            return "css\n"
        elif "html" in self.link[1]:
            return "html\n" 
        else:
            return "html\n"   # 404
    
    def send_content(self, error, isReroute, isDir):
        statusCode = "HTTP/1.1 "
        contentType = "Content-Type: text/"
        location = "Location: " 
        
        if self.reroute:
            error = "301\n"
            
        msg = statusCode + error + contentType + self.get_content_type()
        
        # print("404" not in error)
        print(msg)
        if "404" not in error and "405" not in error:
            if isReroute or self.reroute:
                msg += location + self.link[1]

            if isDir:
                print("here")
                contents = self.path + "/index.html"
                with open(contents, "r") as fileObj:
                    file = fileObj.read()
                msg += "\n" + file
            else:
                print("here")
                contents = self.path
                with open(contents, "r") as fileObj:
                    file = fileObj.read()
                msg += "\n" + file
            
        msg += "\r\n"
        print(msg)
        
        self.request.sendall(msg.encode('utf-8'))
        
    def check_path(self):
        if self.link[0] != "GET":           # only allow GET http commands
            self.send_content("405\n", False, False)
        elif ".." in self.link[1]:          # do not allow for /../... cases at all
            self.send_content("404\n", False, False)
            
        try:
            open(self.path)
            # print(os.path.exists(self.path))
        except Exception as e:
            # print(e)
            if os.path.exists(self.path):
                if os.path.isdir(self.path):
                    if not self.path.endswith("/"): 
                        self.path += "/"
                        self.reroute = True
                        self.send_content("301\n", True, True)      # if directory found, return 200
                        print("301 success")
                    else:
                        self.send_content("200\n", False, True)      # if directory found, return 200
                else:
                    self.reroute = False
                    print("success")    
                    self.send_content("200\n", False, False)      # if directory found, return 200
            else:                                                   # not a directory
                print("not found")
                self.reroute = False
                self.send_content("404\n", False, False)      # if directory not found, return 404
        else:
            if os.path.isdir(self.path):
                print("success")
                self.send_content("200\n", False, True)      # if directory found, return 200
            else:
                print("success")
                self.send_content("200\n", False, False)      # if directory found, return 200
            
if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    with socketserver.TCPServer((HOST, PORT), MyWebServer) as server:

        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        server.serve_forever()
