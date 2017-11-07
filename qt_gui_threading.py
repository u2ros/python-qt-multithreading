"""Multithreaded helper module for Qt based QApplications
"""
import time
from PyQt4 import uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *

#client-side thread interface
class ThreadClient(QObject):
    """Client side thread interface
    """
    sgnTick = pyqtSignal(dict)
    sgnError = pyqtSignal(dict)
    sgnFinished = pyqtSignal()

    def __init__(self, controller):
        """Constructor

        :param ThreadController controller: Instance of user defined ThreadController

        Instance of ThreadClient will fire sgnTick on every iteration of the work loop, sgnError on error
        and sgnFinished after receiving a stop flag and finishing the last loop iteration
        """
        QObject.__init__(self)
        self._controller = controller
        self._running = False

    @property
    def is_running(self):
        return self._running

    def start(self):
        """Starts the thread and connects all signals
        """
        self._thread = QThread()
        self._controller.moveToThread(self._thread)

        self._controller.sgnError.connect(self._on_error)
        self._controller.sgnTick.connect(self._on_tick, type = Qt.QueuedConnection)
        self._controller.sgnFinished.connect(self._thread_finished)

        self._thread.started.connect(self._controller.work)
        self._thread.start()

        self._running = not self._running

    def stop(self):
        """Sends a stop signal to ThreadController

        Note: Thread will not finish immediately, it will finish the current iteration first
        """
        self._controller.stop()

    def _on_tick(self, result):
        self.sgnTick.emit(result)

    def _thread_finished(self):
        self._thread.quit()
        self._thread.wait()
        self._thread = None
        self._running = not self._running
        self.sgnFinished.emit()

    def _on_error(self, errdict):
        self.sgnError.emit(errdict)

#thread-side controller object
class ThreadController(QObject):
    sgnTick = pyqtSignal(dict)
    sgnError = pyqtSignal(dict)
    sgnFinished = pyqtSignal()

    def __init__(self, interval, wait_chunk=0.05):
        """Constructor

        :param float interval: Pause duration between iterations of the loop in seconds
        :param float wait_period: Check period in seconds for thread stop signal, default 0.05 seconds
        """
        QObject.__init__(self, None)
        self._mutex = QMutex()
        self._interval = interval
        self._running = True
        self._wait_period = wait_chunk

    def stop(self):
        """Sets the running flag to False, thread will stop in at most wait_period time, then emit sgnFinished
        """
        self._mutex.lock()
        self._running = False
        self._mutex.unlock()

    @pyqtSlot()
    def work(self):
        """Performs the actual work.

        Before the work loop is started _prepare() is called and _cleanup() after the stop signal is received.
        Default implementations of _prepare() and _cleanup() do nothing.
        During the loop execution the _process() method is called in each iteration. This method must be overriden and it must return a result
        """
        try:
            self._prepare()
        except Exception as e:
            self.sgnError.emit({'error': e})

        while self._running:
            try:
                result = self._process()
                self.sgnTick.emit({'result': result})
            except Exception as e:
                self.sgnError.emit({'error': e})

            #wait out the interval period but check for stop signal all the time
            wait = 0.0
            while wait < self._interval:
                if not self._running:
                    break
                time.sleep(self._wait_period)
                wait += self._wait_period

        try:
            self._cleanup()
        except Exception as e:
            self.sgnError.emit({'error': e})

        self.sgnFinished.emit()

    def _prepare(self):
        pass

    def _process(self):
        raise NotImplementedError()

    def _cleanup(self):
        pass
