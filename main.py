import os
import http
import time
import socket
from threading import Thread
import http.client
from http.server import SimpleHTTPRequestHandler, HTTPServer
from typing import List

from Worker import *
from RenderTask import *
import CommunicationConstants as CConsts

workers: List[Worker] = []
tasks: List[RenderTask] = []

class ServerHTTPRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        print("Got request for " + self.path)
        if self.path == CConsts.WORKERMGMT:
            headers = self.headers

            if ("Action" in headers):
                if (("Host" and "Port") in headers):
                    self.send_response(200)
                    self.end_headers()  # necessary to send
                    workers.append(Worker(headers))
                    return
                else:
                    print(f"Missing or wrong arguments in \"Action\" header in \"{CConsts.WORKERMGMT}\" request")
                    self.send_error(500, "Missing or wrong arguments")
                    return
            else:
                print(f"Unknown \"{CConsts.WORKERMGMT}\" request: " + str(headers))
                self.send_error(500, f"Unknown \"{CConsts.WORKERMGMT}\" request")

        elif self.path == "blenderdata":
            if ("Task-ID" not in self.headers):
                self.send_error(http.client.BAD_REQUEST, "Missing \"Task-ID\" header")
                return

            task = next(task for task in tasks if task.TaskID == self.headers["Task-ID"])
            if not task:
                print(f"Unknown task: {self.headers["Task-ID"]}")
                self.send_error(http.client.BAD_REQUEST, f"Unknown \"Task-ID\": {self.headers["Task-ID"]}")
                return

            # TODO: look up, if it's a single file (.blend) or multiple files (.zip)
            filepath = f"{task.get_folder()}/blenderfiles/{task.get_filename()}"
            if not os.path.isfile(filepath):
                print(f"Could not find {task.get_filename()} in for task {task.TaskID}")
                self.send_error(http.client.INTERNAL_SERVER_ERROR, f"Coulnd't find a file associated with Task-ID {task.TaskID}")

            self.send_response(200)
            self.send_header("Content-type", "application/octet-stream")
            self.send_header("Content-Disposition", "attachment; filename='blenderdata.blend'")
            self.end_headers()  # necessary to send
            with open(filepath, "rb") as file:
                self.wfile.write(file.read())

        else:
            self.send_error(404, f"Unknown request: {self.path}")

    def do_PUT(self):
        print("Got request for " + self.path)
        # task from self.path ??
        missingFields = {"Content-Type", "Content-Length", "Task-ID", "Worker-ID", "Frame-Info"}.difference(set(self.headers))
        if len(missingFields) > 0:
            self.send_error(500, "Header fields missing: " + ", ".join(missingFields))
            return

        if not self.headers["Content-Type"] == "application/octet-stream":
            self.send_error(500, "Content-Type is no octet-stream")
            return

        if self.headers["Content-Length"] == "0":
            self.send_error(500, "Content-Length is 0. Not allowed")
            return

        if not is_int(self.headers["Content-Length"]):
            self.send_error(500, "Content-Length cannot be parsed to int")
            return

        #TODO (maybe): check worker id
        task = next(task for task in tasks if task.TaskID == self.headers["Task-ID"])
        if not task:
            print(f"Unknown task: {self.headers["Task-ID"]}")
            self.send_error(http.client.BAD_REQUEST, f"Unknown \"Task-ID\" header")
            return

        workingPath = f"{task.get_folder()}/renderoutput"
        os.makedirs(workingPath, exist_ok=True)
        try:
            with open(f"{workingPath}/{str(self.headers["Frame-Info"])}", "wb") as file:
                file.write(self.rfile.read(int(self.headers["Content-Length"])))

        except Exception as ex:
            print(ex)
            self.send_error(500, f"Error while writing received file")

        self.send_response(http.client.OK)
        self.end_headers()  # necessary to send

def is_int(string: str) -> bool:
    try:
        int(string)
        return True
    except:
        return False

def send_task_http(worker: Worker):
    global tasks
    task0 = RenderTask("0000_0000_0000_0000",
                       "localhost",
                       65431,
                       BlenderDataType.SingleFile,
                       RenderOutputType.PNG,
                       0,
                       52,
                       13)
    tasks.append(task0)

    task1 = RenderTask("0000_0000_0000_0001",
                       "localhost",
                       65431,
                       BlenderDataType.SingleFile,
                       RenderOutputType.FFMPEG,
                       0,
                       52,
                       13)
    tasks.append(task1)

    headers = task0.to_headers()
    MAX_RETRIES = 3
    TIMEOUT = 5  # timeout after x (here: 5) seconds
    retry_count = 0
    while retry_count < MAX_RETRIES:
        connection = None
        try:
            connection = http.client.HTTPConnection(worker.host, worker.port, timeout=TIMEOUT)
            connection.request("GET", CConsts.STARTTASK, headers=headers)
            response = connection.getresponse()

            # Check if response belongs to request??
            if response.status == 200:
                responseData = response.read()
                print("Task delivered successfully")
            else:
                print(f"Task delivery failed: {response.status} {response.reason}")
        except socket.timeout as e:   # did response timeout?
            retry_count += 1
            print(f"Socket timeout, retrying {retry_count}/{MAX_RETRIES}...")
            if retry_count >= MAX_RETRIES:
                print("Max retries reached, unable to get response.")
        except http.client.HTTPException as e:
            print("HTTP exception:", e)
            break
        except Exception as e:
            print("Other exception:", e)
            break
        finally:
            # Close the connection if it was opened
            if connection is not None:
                connection.close()
                
    # Start thread to listen to tasks

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
        time.sleep(0.01)  # reduce performance impact of while(True)-loop

def listen(host: str, port: int):
    server_address = (host, port)
    httpd = HTTPServer(server_address, ServerHTTPRequestHandler)
    print(f"Listener runs at {host}:{port}")
    httpd.serve_forever()

def main():
    listener = Thread(target=listen, args=("localhost", 65431))
    listener.start()

    time.sleep(1)
    input("\nPress enter to send test file")

    send_task_http(workers[0])

    loop()


main()