class Worker:
    host: str
    port: int

    def __init__(self, host, port):
        self.host = host
        self.port = port

    def __init__(self, dictionary):
        self.host = dictionary['host']
        self.port = dictionary['port']