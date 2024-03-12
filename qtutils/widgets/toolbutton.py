from functools import partial
from PySide2 import QtCore, QtWidgets


class PresetSelect(QtWidgets.QToolButton):
    selected = QtCore.Signal(str)

    def __init__(self, parent, items, icons=None):
        super().__init__(parent=parent)
        self.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        actions = [QtWidgets.QAction(p, parent) for p in items]
        menu = QtWidgets.QMenu(parent)
        menu.addActions(actions)
        self.setMenu(menu)
        for action, name in zip(actions, items):
            action.triggered.connect(partial(self.selected.emit, name))
        if icons is not None:
            for action, icon in zip(actions, icons):
                action.setIcon(icon)
