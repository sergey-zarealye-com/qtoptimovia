from models.files import FilesModel
import time


class ImportProcessor(object):
    def __init__(self):
        pass

    def main(self, progress_callback, id):
        print('ID', id)
        for n in range(0, 5):
            time.sleep(1)
            progress_callback.emit(n * 100 / 4.)

        return "Done."