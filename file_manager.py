import time
import os

class Manager:
    def __init__(self, file):
        self.file = file

    def read_file(self):
        if self.file_exists():
            with open(self.file, "r") as f:
                content = f.readline()

        else:
            content = "Not Generated"
            time.sleep(1)
            self.read_file()

        return content

    def file_exists(self):
        try:
            f = open(self.file)
            f.close()
            return True

        except FileNotFoundError:
            return False

    def delete_file(self):
        os.remove(self.file)
