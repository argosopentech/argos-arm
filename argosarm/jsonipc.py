import json
import multiprocessing
import os
import pathlib


class Pipe:
    # Opening a FIFO pipe will block until both a reader and a writer are available
    def __init__(self, path: pathlib.Path):
        self.lock = multiprocessing.Lock()
        self.path = path
        self.listeners = list()
        os.mkfifo(self.path, mode=0o660)

    def add_listener(self, listener: callable):
        with self.lock:
            self.listeners.append(listener)

    def listen(self):
        # Open FIFO pipe file with line buffering
        f = open(self.path, "r", buffering=1)

        while True:
            with self.lock:
                line = f.read()
                if len(line) == 0:
                    continue
                o = json.loads(line)
                for listener in self.listeners:
                    listener(o)

        f.close()

    def write(self, data: str):
        with open(self.path, "w") as f:
            data_str = json.dumps(data)
            f.write(data_str + "\n")
