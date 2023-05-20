import json
import logging
import multiprocessing
import os
import pathlib


class Pipe:
    def __init__(self, path: pathlib.Path):
        self.path = path
        self.listeners = list()
        if not os.path.exists(self.path):
            os.mkfifo(self.path, mode=0o660)

    def add_listener(self, listener: callable):
        self.listeners.append(listener)

    def listen(self):
        # Open FIFO pipe file with line buffering
        # Opening a FIFO pipe will block until both a reader and a writer are available
        f = open(self.path, "r", buffering=1)
        logging.info(f"Listening on pipe {self.path}")

        read_buffer = ""
        while True:
            line = f.read()
            if len(line) == 0:
                continue
            read_buffer += line
            newline_index = read_buffer.find("\n")
            if newline_index == -1:
                continue
            json_str = read_buffer[:newline_index]
            read_buffer = read_buffer[newline_index + 1 :]
            try:
                o = json.loads(json_str)
            except json.JSONDecodeError as e:
                logging.error(f"Failed to decode JSON: {e} (json_str={json_str})")
                continue
            for listener in self.listeners:
                listener(o)
        f.close()

    def write(self, data: str):
        with open(self.path, "w") as f:
            logging.info(f"Writing to pipe {self.path}")
            data_str = json.dumps(data)
            f.write(data_str + "\n")
