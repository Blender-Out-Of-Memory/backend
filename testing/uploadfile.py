import http.client
import pathlib

address = "localhost"
port = 8000

filepath = f"{pathlib.Path(__file__).parent.absolute()}/example.blend"
with open(filepath, "rb") as file:
    connection = http.client.HTTPConnection(address, port)
    connection.request("POST", "/api/taskscheduler/render-tasks/run_task/", body=file.read())
    response = connection.getresponse()
    print(response.status)
    print(response.msg)