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
