import http.server

class PPRServerHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            datas = self.rfile.read(int(self.headers["Content-Length"])).decode("utf-8")
            print(datas)
            userUsingUploadInfoFileStream.write("\n")
            userUsingUploadInfoFileStream.write(datas)
            userUsingUploadInfoFileStream.write("\n")
        except Exception as e:
            print(f"Error: {repr(e)}")
        self.send_response(200)
        self.end_headers()
    
    def do_POST(self):
        self.do_GET()
    
userUsingUploadInfoFileStream = open("./ppr-server-userUsingUploadInfo.txt", "a", encoding="utf-8")
server = http.server.HTTPServer(("", 8000), PPRServerHandler)
server.serve_forever(0.05)