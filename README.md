# python-qt-multithreading
Helper module for Qt 4 multi threading api

Example usage:

```python
import sys, random

import sip
try:
    apis = ["QDate", "QDateTime", "QString", "QTextStream", "QTime", "QUrl", "QVariant"]
    for api in apis:
        sip.setapi(api, 2)
except ValueError:
    # API has already been set so we can't set it again.
    pass

from PyQt4.QtGui import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt4.QtCore import QSize

from qt_gui_threading.core import ThreadClient, ThreadController

class LetterThreadController(ThreadController):
    def __init__(self, interval):
        ThreadController.__init__(self, interval)
        self._letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G']

    #override _process method
    def _process(self):
        return self._letters[random.randint(0, len(self._letters))]

class NumberThreadController(ThreadController):
    def __init__(self, interval):
        ThreadController.__init__(self, interval)

    def _process(self):
        return '{:d}'.format(random.randint(0, 99999))

class MyGUI(QWidget):
    def __init__(self):
        QWidget.__init__(self, None)

        #setup widgets...
        layout = QVBoxLayout()

        self.lblOne = QLabel(self)
        self.lblOne.setText('press start')
        self.lblTwo = QLabel(self)
        self.lblTwo.setText('press start')

        self.btnStart = QPushButton(self)
        self.btnStart.setText('Start')
        self.btnStart.clicked.connect(self._start)

        self.btnStop = QPushButton(self)
        self.btnStop.setText('Stop')
        self.btnStop.setEnabled(False)
        self.btnStop.clicked.connect(self._stop)

        layout.addWidget(self.lblOne)
        layout.addWidget(self.lblTwo)
        layout.addWidget(self.btnStart)
        layout.addWidget(self.btnStop)
        layout.insertStretch(-1, 1)

        #define thread controllers
        self._tc1 = None
        self._tc2 = None

        self.setLayout(layout)

    def _start(self):
        self._tc1 = ThreadClient(LetterThreadController(0.5))
        self._tc1.sgnTick.connect(self._onTc1Change)
        self._tc1.sgnFinished.connect(self._on_finished)
        self._tc1.start()
        self._tc2 = ThreadClient(NumberThreadController(1.0))
        self._tc2.sgnTick.connect(self._onTc2Change)
        self._tc2.sgnFinished.connect(self._on_finished)
        self._tc2.start()

        self.btnStart.setEnabled(False)
        self.btnStop.setEnabled(True)

    def _stop(self):
        if self._tc1:
            self._tc1.stop()
        if self._tc2:
            self._tc2.stop( )

    def _on_finished(self):
        #only enable start button when both threads have stopped...
        stopped = True
        if self._tc1.is_running or self._tc2.is_running:
            stopped = False

        if stopped:
            self.btnStart.setEnabled(True)
            self.btnStop.setEnabled(False)

    def _onTc1Change(self, data):
        self.lblOne.setText(data['result'])

    def _onTc2Change(self, data):
        self.lblTwo.setText(data['result'])

if __name__ == '__main__':
    app = QApplication(sys.argv)

    gui = MyGUI()
    gui.resize(QSize(500, 100))
    gui.show()

    app.exec_()
    sys.exit()
```
