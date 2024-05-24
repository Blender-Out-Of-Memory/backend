import ast
import http
import socket
import pickle
import time
from threading import Thread
import http.client
from http.server import SimpleHTTPRequestHandler, HTTPServer
from typing import List

import Worker
import CommunicationConstants as CConsts

workers: List[Worker] = []

class ServerHTTPRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        print("Got request for " + self.path)
        if self.path == CConsts.WORKERMGMT:
            headers = self.headers
            #try:
            #    headers = self.headers
            #except Exception as ex: # Can try fail at all ??
            #    print(f"Failed to read \"{CConsts.WORKERMGMT}\" request header")
            #    print("Exception: " + str(ex))
            #    self.send_error(500, f"Failed to read \"{CConsts.WORKERMGMT}\" request header")
            #    return

            if ("Action" in headers):
                if (("Host" and "Port") in headers):
                    self.send_response(200)
                    self.end_headers() # necessary to send
                    workers.append(Worker.Worker(headers))
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

def run_http_server(host, port):
    server_address = (host, port)
    httpd = HTTPServer(server_address, ServerHTTPRequestHandler)
    print(f'HTTP server runs at {host}:{port}')
    httpd.serve_forever()

def send_task(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f'Server läuft und wartet auf Verbindungen an {host}:{port}...')

    connection, client_address = server_socket.accept()
    try:
        print(f'Verbindung von {client_address} akzeptiert.')

        # Beispielobjekt zum Versenden
        data = {'task-id': '0000_0000_0000_0000', 'file': '/data/thefile', 'start_frame': 0, 'end_frame': 50}
        
        # Objekt serialisieren
        serialized_data = pickle.dumps(data)
        
        # Serialisierte Daten senden
        connection.sendall(serialized_data)
        print('Daten gesendet.')
    finally:
        connection.close()
        server_socket.close()

def send_task_http(worker: Worker.Worker):
    conn = http.client.HTTPConnection(worker.host, worker.port)
    data = {'task-id': '0000_0000_0000_0000', 'file': '/data/thefile', 'start_frame': 0, 'end_frame': 50}
    conn.request('GET', CConsts.STARTTASK, headers=data)
    response = conn.getresponse()

    #Check if response belongs to request??
    if response.status == 200:
        responseData = response.read()
        print("Task delivered sucessfully")
    else:
        print(f'Task delivery failed: {response.status} {response.reason}')

    conn.close()
    #Start thread to listen to tasks

    return

def listen(host: str, port: int):
    server_address = (host, port)
    httpd = HTTPServer(server_address, ServerHTTPRequestHandler)
    print(f'Listener runs at {host}:{port}')
    httpd.serve_forever()

def main():

    listener = Thread(target=listen, args=('localhost', 65431))
    listener.start()
    #send_task('localhost', 65432)

    #run_http_server('localhost', 65432)

    time.sleep(1)
    input("\nPress enter to send test file")

    send_task_http(workers[0])


main()