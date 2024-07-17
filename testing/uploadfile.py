import http.client
import pathlib
import json

address = "localhost"
port = 8000

username = "tobi"
password = "a"

connection = http.client.HTTPConnection(address, port)
body = "{\"username\":\"" + username + "\",\"password\":\"" + password + "\"}"
connection.request("POST", "/account/login/",
                   headers={"Content-Type": "application/json"},
                   body=body)

data = connection.getresponse().read().decode("utf-8")
print(data)
token = json.loads(data)["token"]

filepath = f"{pathlib.Path(__file__).parent.absolute()}/example.blend"
with open(filepath, "rb") as file:
    connection = http.client.HTTPConnection(address, port)
    connection.request("POST", "/api/taskscheduler/render-tasks/run_task/",
                       headers={"Content-Type": "application/octet-stream",
                                "Authorization": f"Token {token}"},
                       body=file.read())
    response = connection.getresponse()
    print(response.status)
    print(response.read())