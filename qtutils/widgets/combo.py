from PySide2 import QtWidgets, QtCore, QtGui


class CheckComboBox(QtWidgets.QComboBox):
    """Editable ComboBox widget where each item can be added or removed with a
    checkbox"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._model = CheckComboItemModel(self)
        self.setModel(self._model)
        self.setEditable(True)


class CheckComboItemModel(QtGui.QStandardItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._parent = parent

    def flags(self, index):
        return (QtCore.Qt.ItemIsEnabled |
                QtCore.Qt.ItemIsUserCheckable |
                QtCore.Qt.ItemIsEditable)

    def data(self, index, role):
        value = super(CheckComboItemModel, self).data(index, role)
        row = index.row()
        text = self._parent.lineEdit().text()
        items = text.split(',')
        if role == QtCore.Qt.CheckStateRole:
            current_text = self._parent.itemText(row)
            if current_text in items:
                return QtCore.Qt.Checked
            else:
                return QtCore.Qt.Unchecked
        return value

    def setData(self, index, value, role):
        data = index.data()
        text = self._parent.lineEdit().text()
        items = text.split(',') if text else []
        items.remove(data) if data in items else items.append(data)
        result_string = ','.join(items)
        self._parent.setEditText(result_string)
        return True
