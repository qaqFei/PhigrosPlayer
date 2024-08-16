from queue import Queue
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread
from time import sleep
import json

_jsCodes: Queue[str] = Queue()
resultMap = {}
_codeId = -1

def _rid():
    global _codeId
    _codeId += 1
    return _codeId

def addJsCode(code: str):
    _jsCodes.put((code, False, _rid()))

def runJsCode(code: str):
    data = (code, True, _rid())
    _jsCodes.put(data)
    while data[-1] not in resultMap:
        sleep(1 / 240)
    return resultMap.pop(data[-1])

class _Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        global _codeId
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "*")
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
        self.end_headers()
        
        if "getJs" in self.path:
            if not _jsCodes.empty():
                code, getresult, rid = _jsCodes.get()
                self.wfile.write(json.dumps({
                    "code": 0,
                    "data": code,
                    "getresult": getresult,
                    "rid": rid
                }).encode())
            else:
                self.wfile.write(b'{"code": -1}')
    
    def do_POST(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "*")
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
        self.end_headers()
        if "putResult" in self.path:
            result = json.loads(self.rfile.read(int(self.headers["Content-Length"])).decode())
            resultMap.update({
                result["rid"]: result.get("data", None)
            })
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "*")
        self.send_header("Access-Control-Allow-Headers", "Authorization, Content-Type")
        self.end_headers()
    
    def log_request(self, *args, **kwargs) -> None: ...


def _run():
    httpd = HTTPServer(("localhost", 21632), _Handler)
    httpd.serve_forever(poll_interval=0.0)

def run():
    Thread(target=_run, daemon=True).start()