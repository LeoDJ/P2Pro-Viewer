import threading
import sys

class PipeLogger:
    @staticmethod
    def _proxy_lines(pipe, handler):
        with pipe:
            for line in pipe:
                handler(line.decode(sys.stdout.encoding).rstrip())

    def __init__(self, pipe, handler):
        threading.Thread(target=self._proxy_lines, args=[pipe, handler]).start()