import socket
import pickle

from http.server import SimpleHTTPRequestHandler, HTTPServer

class CustomHTTPRequestHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        print("Got request for " + self.path)
        if self.path == '/data/thefile':
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
    httpd = HTTPServer(server_address, CustomHTTPRequestHandler)
    print(f'Server läuft an {host}:{port}')
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

if __name__ == '__main__':
    send_task('localhost', 65432)
    run_http_server('localhost', 65432)
    #run_http_server('0.0.0.0', 65432)
