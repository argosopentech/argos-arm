import functools
import logging
import multiprocessing
import os
import pathlib
import time

import jsonipc
import xboxdrv

home_dir = pathlib.Path.home()
data_dir = pathlib.Path(
    os.getenv("XDG_DATA_HOME", default=str(home_dir / ".local" / "share"))
)
argos_arm_data_dir = data_dir / "argos-arm"
os.makedirs(argos_arm_data_dir, exist_ok=True)


def consumer(pipe):
    pipe.add_listener(lambda data: print(data))
    pipe.listen()


def xboxdrv_input_listener(pipe: jsonipc.Pipe, data):
    pipe.write(data)


def main():
    logging.basicConfig(level=logging.DEBUG)

    # Start xboxdrv
    controller_input_pipe = jsonipc.Pipe(argos_arm_data_dir / "controller.pipe")
    controller_callback = functools.partial(
        xboxdrv_input_listener, controller_input_pipe
    )
    controller_proc = multiprocessing.Process(
        target=xboxdrv.subscribe_to_inputs, args=(controller_callback,)
    )
    controller_proc.start()

    c = multiprocessing.Process(target=consumer, args=(controller_input_pipe,))
    c.start()

    controller_proc.join()
    c.join()


if __name__ == "__main__":
    main()
