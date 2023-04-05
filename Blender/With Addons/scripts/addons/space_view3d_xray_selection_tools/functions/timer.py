import time


class Timer:
    ENABLED = False

    def __init__(self):
        if self.ENABLED:
            self.time_start = time.time()

    def add(self, label):
        if self.ENABLED:
            exec_time = time.time() - self.time_start
            print(f"{label}: {exec_time:.4f} sec")
            self.time_start = time.time()
