import logging
import multiprocessing

import xboxdrv


def main():
    logging.basicConfig(level=logging.DEBUG)
    proc = multiprocessing.Process(target=xboxdrv.f710)
    proc.start()
    proc.join()


if __name__ == "__main__":
    main()
