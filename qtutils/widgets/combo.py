from qtbinding import QtWidgets, QtCore, QtGui


class CheckComboBox(QtWidgets.QComboBox):
    """Editable ComboBox widget

    Each item can be added or removed with a checkbox.
    """

    def __init__(self, parent=None, separator=','):
        super().__init__(parent)
        model = CheckComboItemModel(self)
        model.set_separator(separator)
        self.setModel(model)
        self.setEditable(True)


class CheckComboItemModel(QtGui.QStandardItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._parent = parent

    def set_separator(self, separator):
        self.separator = separator

    def flags(self, index):
        return (QtCore.Qt.ItemIsEnabled |
                QtCore.Qt.ItemIsUserCheckable |
                QtCore.Qt.ItemIsEditable)

    def data(self, index, role):
        value = super(CheckComboItemModel, self).data(index, role)
        row = index.row()
        text = self._parent.lineEdit().text()
        items = text.split(self.separator)
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
        items = text.split(self.separator) if text else []
        items.remove(data) if data in items else items.append(data)
        result_string = self.separator.join(items)
        self._parent.setEditText(result_string)
        return True
