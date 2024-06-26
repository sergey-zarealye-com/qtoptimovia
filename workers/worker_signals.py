from PyQt5.QtCore import QObject, pyqtSignal


class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    progress
        float indicating % progress

    '''
    finished = pyqtSignal(int, object)
    error = pyqtSignal(tuple)
    result = pyqtSignal(int, object)
    partial_result = pyqtSignal(int, object)
    progress = pyqtSignal(int, float)
    metadata_result = pyqtSignal(int, object)