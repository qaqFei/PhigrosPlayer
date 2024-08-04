import http.server

class PPRServerHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            datas = self.rfile.read(int(self.headers["Content-Length"])).decode("utf-8")
            print(datas)
            userUsingUploadInfoFileStream = open("./ppr-server-userUsingUploadInfo.txt", "a", encoding="utf-8")
            userUsingUploadInfoFileStream.write("\n")
            userUsingUploadInfoFileStream.write(datas)
            userUsingUploadInfoFileStream.write("\n")
            userUsingUploadInfoFileStream.close()
        except Exception as e:
            print(f"Error: {repr(e)}")
            try:
                userUsingUploadInfoFileStream.close()
            except Exception:
                pass
        self.send_response(200)
        self.end_headers()
    
    def do_POST(self):
        self.do_GET()
    

server = http.server.HTTPServer(("", 8000), PPRServerHandler)
server.serve_forever(0.05)