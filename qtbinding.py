import os
import importlib

qt_binding = os.environ.get('QT_BINDING', 'PySide2')
shiboken_modules = {
    'PySide2': 'shiboken2',
    'PySide6': 'shiboken6'}


def import_module(name):
    return importlib.import_module(f'{qt_binding}.{name}')


QtWidgets = import_module('QtWidgets')
QtCore = import_module('QtCore')
QtGui = import_module('QtGui')
if qt_binding.startswith('PySide'):
    shiboken = importlib.import_module(shiboken_modules[qt_binding])

# Compatibility with older version
if qt_binding == 'PySide2':
    QtGui.QAction = QtWidgets.QAction
    QtWidgets.QApplication.exec = QtWidgets.QApplication.exec_

    class QRegularExpression:
        def __init__(self, pattern=''):
            self._regexp = QtCore.QRegExp(pattern)

        def match(self, text):
            index = self._regexp.indexIn(text)
            return QRegularExpressionMatch(self._regexp, index)

        def __getattr__(self, name):
            return getattr(self._regexp, name)

    class QRegularExpressionMatch:
        def __init__(self, regexp, index):
            self._regexp = regexp
            self._index = index

        def hasMatch(self):
            return self._index != -1

        def captured(self, group=0):
            return self._regexp.cap(group)

        def capturedStart(self, group=0):
            return self._regexp.pos(group)

        def capturedLength(self, group=0):
            text = self._regexp.cap(group)
            return len(text) if text else 0

        def __getattr__(self, name):
            return getattr(self._regexp, name)

    def setFilterRegularExpression(self, regex):
        if isinstance(regex, QtCore.QRegularExpression):
            self.setFilterRegExp(regex.pattern())
        else:
            self.setFilterRegExp(regex)

    QtCore.QRegularExpression = QRegularExpression
    QtCore.QRegularExpressionMatch = QRegularExpressionMatch
    QtCore.QSortFilterProxyModel.setFilterRegularExpression = setFilterRegularExpression

    for cls in [
            # QtWidgets.QMenu: don't override it because it crashes
            QtWidgets.QDialog,
            QtWidgets.QMessageBox,
            QtWidgets.QFileDialog,
            QtGui.QDrag]:
        cls.exec = cls.exec_
