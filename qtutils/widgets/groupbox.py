from qtbinding import QtWidgets


class CollapsibleBox(QtWidgets.QGroupBox):
    def __init__(self, horizontal: bool = False):
        super().__init__()
        self.setCheckable(True)

        # Layout
        self.layout = (
            QtWidgets.QHBoxLayout() if horizontal else QtWidgets.QVBoxLayout())
        frame = QtWidgets.QFrame()
        widget_layout = QtWidgets.QVBoxLayout()
        widget_layout.addWidget(frame)
        frame.setLayout(self.layout)
        self.setLayout(widget_layout)

        # Connection
        self.toggled.connect(lambda x: frame.show() if x else frame.hide())
