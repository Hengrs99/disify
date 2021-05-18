import time


class Timer:
    def start(self):
        self.__start_time = time.perf_counter()

    def elapsed_time(self):
        elapsed_time = time.perf_counter() - self.__start_time
        return elapsed_time