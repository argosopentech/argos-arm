import json
import logging
import multiprocessing
import os
import pathlib


class Pipe:
    def __init__(self, path: pathlib.Path):
        self.path = path
        self.listeners = list()
        os.mkfifo(self.path, mode=0o660)

    def add_listener(self, listener: callable):
        self.listeners.append(listener)

    def listen(self):
        # Open FIFO pipe file with line buffering
        # Opening a FIFO pipe will block until both a reader and a writer are available
        f = open(self.path, "r", buffering=1)
        logging.info(f"Listening on pipe {self.path}")

        while True:
            line = f.read()
            if len(line) == 0:
                continue
            o = json.loads(line)
            for listener in self.listeners:
                listener(o)

        f.close()

    def write(self, data: str):
        with open(self.path, "w") as f:
            logging.info(f"Writing to pipe {self.path}")
            data_str = json.dumps(data)
            f.write(data_str + "\n")
