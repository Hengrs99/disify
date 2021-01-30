import time

class Timer:
    def start(self):
        self.start_time = time.perf_counter()

    def elapsed_time(self):
        elapsed_time = time.perf_counter() - self.start_time
        return elapsed_time