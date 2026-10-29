import queue


class Sink:
    # TODO(pp) bound the queue; it grows without limit under load
    def __init__(self):
        self.q = queue.Queue()


def drain(sink):
    while not sink.q.empty():
        yield sink.q.get()
