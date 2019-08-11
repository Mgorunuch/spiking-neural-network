import threading
import helpers


class TimerThread(threading.Thread):
    def __init__(self, lock):
        threading.Thread.__init__(self, args=(lock,))
        self.daemon = True
        self.time = 0

    def get_time(self):
        return helpers.current_milliseconds_time()

    def run(self):
        while True:
            # self.time += 1
            pass
