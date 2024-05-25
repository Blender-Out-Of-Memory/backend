import http
import time
from threading import Thread
import http.client
from http.server import SimpleHTTPRequestHandler, HTTPServer
from typing import List

from Worker import *
import CommunicationConstants as CConsts

workers: List[Worker] = []

class ServerHTTPRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        print("Got request for " + self.path)
        if self.path == CConsts.WORKERMGMT:
            headers = self.headers

            if ("Action" in headers):
                if (("Host" and "Port") in headers):
                    self.send_response(200)
                    self.end_headers() # necessary to send
                    workers.append(Worker(headers))
                    return
                else:
                    print(f"Missing or wrong arguments in \"Action\" header in \"{CConsts.WORKERMGMT}\" request")
                    self.send_error(500, "Missing or wrong arguments")
                    return
            else:
                print(f"Unknown \"{CConsts.WORKERMGMT}\" request: " + str(headers))
                self.send_error(500, f"Unknown \"{CConsts.WORKERMGMT}\" request")

        elif self.path == '/data/thefile':
            self.send_response(200)
            self.send_header('Content-type', 'application/octet-stream')
            self.send_header('Content-Disposition', 'attachment; filename="example.txt"')
            self.end_headers()
            with open('pain.blend', 'rb') as file:
                self.wfile.write(file.read())
        else:
            self.send_error(404, 'File Not Found')

def send_task_http(worker: Worker):
    connection = http.client.HTTPConnection(worker.host, worker.port)
    data = {'task-id': '0000_0000_0000_0000', 'file': '/data/thefile', 'start_frame': 0, 'end_frame': 50}
    connection.request('GET', CConsts.STARTTASK, headers=data)
    response = connection.getresponse() #TODO:Add timeout and retry

    #Check if response belongs to request??
    if response.status == 200:
        responseData = response.read()
        print("Task delivered sucessfully")
    else:
        print(f'Task delivery failed: {response.status} {response.reason}')

    connection.close()
    #Start thread to listen to tasks

    return

def loop():
    print("Entered loop")
    stop = False
    while not stop:
        inp = input("Enter command> ")
        if (inp.lower() == ("q" or "quit")):
            stop = True
        else:
            print("Unknown command")

        inp = ""

def listen(host: str, port: int):
    server_address = (host, port)
    httpd = HTTPServer(server_address, ServerHTTPRequestHandler)
    print(f'Listener runs at {host}:{port}')
    httpd.serve_forever()

def main():
    listener = Thread(target=listen, args=('localhost', 65431))
    listener.start()

    time.sleep(1)
    input("\nPress enter to send test file")

    send_task_http(workers[0])

    loop()


main()