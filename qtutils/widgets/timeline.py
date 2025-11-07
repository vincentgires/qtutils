from qtbinding import QtGui, QtWidgets, QtCore

max_range = 999999
current_frame_size_scale = 0.75
current_frame_tick_color = (0.5, 0.5, 0.5)
current_frame_tick_width = 2
current_frame_number_color = (0.5, 0.5, 0.5)
tick_frame_size_scale = 0.65
tick_frame_number_color = (0.5, 0.5, 0.5)
background_line_color = (0.5, 0.5, 0.5)
background_line_with = 1
tick_line_color = (0.5, 0.5, 0.5)
tick_line_with = 1
range_intervals_default_color = (0.7, 0.2, 1, 0.35)
range_intervals_font_scale = 0.75
range_intervals_font_gain_factor = 2


class StripItem(QtWidgets.QGraphicsRectItem):
    def __init__(self, *args):
        super().__init__(*args)


class TimelineView(QtWidgets.QGraphicsView):
    frame_changed = QtCore.Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QtWidgets.QGraphicsScene(self)
        self.setScene(self.scene)

        # Basic properties
        self.start = 1
        self.end = 100
        self.current = 1
        self.current_spin = None
        self.range_intervals: list[dict] = []
        # dict(frame_range: tuple[int], color: tuple[int], name: str)
        self.dragging = False
        self.zoom_factor = 1.0

        # View configuration
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        # Initialize the timeline
        self.update_timeline()

    def set_current_spin(self, spin_box):
        self.current_spin = spin_box
        self.current_spin.valueChanged.connect(self.on_current_changed)

    def on_current_changed(self):
        # Emit signal on frame changed
        self.frame_changed.emit(self.current)

    def resizeEvent(self, event):  # noqa: N802
        super().resizeEvent(event)
        self.update_timeline()

    def update_timeline(self):
        self.scene.clear()

        # Basic dimensions
        timeline_width = self.width() * self.zoom_factor
        timeline_height = 20
        timeline_y = 50

        # Draw the background line
        self.scene.addLine(
            0, timeline_y, timeline_width, timeline_y,
            QtGui.QPen(
                QtGui.QColor.fromRgbF(*background_line_color),
                background_line_with))

        # Draw the ticks
        num_ticks = 10
        tick_step = timeline_width / num_ticks
        for i in range(num_ticks + 1):
            tick_x = i * tick_step
            tick_value = int(
                self.start + (i / num_ticks) * (self.end - self.start))

            # Tick
            self.scene.addLine(
                tick_x, timeline_y - 5, tick_x, timeline_y + 5,
                QtGui.QPen(
                    QtGui.QColor.fromRgbF(*tick_line_color),
                    tick_line_with))

            # Label
            font = QtWidgets.QApplication.font()
            font.setPointSizeF(font.pointSize() * tick_frame_size_scale)
            text = self.scene.addText(str(tick_value), font)
            text.setDefaultTextColor(
                QtGui.QColor.fromRgbF(*tick_frame_number_color))
            text.setPos(tick_x - 10, timeline_y + 8)

        # Draw the range intervals
        for data in self.range_intervals:
            color = data['color']
            name = data['name']
            frame_range = data['frame_range']
            start, end = frame_range
            color = color or range_intervals_default_color
            start_x = (
                (start - self.start) / (self.end - self.start)
            ) * timeline_width
            end_x = (
                (end - self.start) / (self.end - self.start)
            ) * timeline_width
            if start_x >= end_x:  # Ensure the range is valid
                continue
            range_rect = StripItem(
                start_x,
                timeline_y - timeline_height / 2,
                end_x - start_x,
                timeline_height)
            range_rect.setBrush(QtGui.QBrush(QtGui.QColor.fromRgbF(*color)))
            range_rect.setPen(QtGui.QPen(QtCore.Qt.NoPen))
            self.scene.addItem(range_rect)

            # Add the text for the current position
            font = QtWidgets.QApplication.font()
            font.setPointSizeF(font.pointSize() * range_intervals_font_scale)
            darkened_color = tuple(
                c * range_intervals_font_gain_factor
                for i, c in enumerate(color) if i < 3)  # Only take rgb
            text = self.scene.addText(name, font)
            text.setDefaultTextColor(QtGui.QColor.fromRgbF(*darkened_color))
            text.setPos(start_x, timeline_y - 15)

        # Draw the current position line
        current_x = (
            (self.current - self.start) / (self.end - self.start)
        ) * timeline_width
        if 0 <= current_x <= timeline_width:
            self.scene.addLine(
                current_x, timeline_y - 15, current_x, timeline_y + 15,
                QtGui.QPen(
                    QtGui.QColor.fromRgbF(*current_frame_tick_color),
                    current_frame_tick_width))

            # Add the text for the current position
            font = QtWidgets.QApplication.font()
            font.setPointSizeF(font.pointSize() * current_frame_size_scale)
            current_text = self.scene.addText(str(self.current), font)
            current_text.setDefaultTextColor(
                QtGui.QColor.fromRgbF(*current_frame_number_color))
            current_text.setPos(current_x - 15, timeline_y - 30)

        # Adjust the scene to show the entire timeline
        self.scene.setSceneRect(0, 0, timeline_width, 100)

    def set_values(self, start, end, current):
        self.start = start
        self.end = end
        self.current = current
        self.update_timeline()

    def wheelEvent(self, event):  # noqa: N802
        # Zoom with the mouse wheel
        factor = 1.2 if event.angleDelta().y() > 0 else 1 / 1.2
        new_zoom = self.zoom_factor * factor
        if 0.1 <= new_zoom <= 5:
            self.zoom_factor = new_zoom
            self.update_timeline()

        # Re-center on the current frame after zoom
        current_x = (
            (self.current - self.start) / (self.end - self.start)
        ) * (self.width() * self.zoom_factor)
        self.centerOn(current_x, 50)

    def mousePressEvent(self, event):  # noqa: N802
        if event.button() == QtCore.Qt.LeftButton:
            self.dragging = True
            self.set_current_from_pos(event.pos())

    def mouseMoveEvent(self, event):  # noqa: N802
        if self.dragging:
            self.set_current_from_pos(event.pos())

    def mouseReleaseEvent(self, event):  # noqa: N802
        if event.button() == QtCore.Qt.LeftButton:
            self.dragging = False

    def set_current_from_pos(self, pos):
        scene_pos = self.mapToScene(pos)
        timeline_width = self.width() * self.zoom_factor

        if 0 <= scene_pos.x() <= timeline_width:
            proportion = scene_pos.x() / timeline_width
            self.current = int(
                self.start + proportion * (self.end - self.start))
            self.current = max(self.start, min(self.current, self.end))

            if self.current_spin:
                if self.current_spin.value() != self.current:
                    self.current_spin.setValue(self.current)

            self.update_timeline()


class TimelineWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Timeline')

        # Timeline
        self.timeline = TimelineView(self)

        # Main controls
        self.start_spin = QtWidgets.QSpinBox()
        self.start_spin.setRange(0, max_range)
        self.start_spin.setValue(self.timeline.start)
        self.start_spin.valueChanged.connect(self.update_timeline)

        self.end_spin = QtWidgets.QSpinBox()
        self.end_spin.setRange(1, max_range)
        self.end_spin.setValue(self.timeline.end)
        self.end_spin.valueChanged.connect(self.update_timeline)

        self.current_spin = QtWidgets.QSpinBox()
        self.current_spin.setRange(0, max_range)
        self.current_spin.setValue(self.timeline.current)
        self.current_spin.valueChanged.connect(self.update_current)

        # Connect the spinbox to the timeline
        self.timeline.set_current_spin(self.current_spin)

        # Layout
        self.main_layout = QtWidgets.QVBoxLayout()

        # Base controls
        self.controls_layout = QtWidgets.QHBoxLayout()
        self.controls_layout.addWidget(self.start_spin)
        self.controls_layout.addWidget(self.current_spin)
        self.controls_layout.addWidget(self.end_spin)
        self.main_layout.addLayout(self.controls_layout)

        # Timeline
        self.main_layout.addWidget(self.timeline)

        # Main layout
        self.setLayout(self.main_layout)

        # Initialize the timeline
        self.update_timeline()

    def add_range(
            self,
            interval: tuple[int, int],
            color: tuple[float] | None = None,
            name: str | None = None):
        start, end = interval
        # Check if the range is valid
        if start < end:
            self.timeline.range_intervals.append(
                dict(frame_range=(start, end), color=color, name=name))
            self.update_timeline()

    def clear_ranges(self):
        self.timeline.range_intervals = []
        self.update_timeline()

    def update_timeline(self):
        start = self.start_spin.value()
        end = self.end_spin.value()

        # Validate the values
        if end <= start:
            end = start + 1
            self.end_spin.setValue(end)

        # Update the current spinbox range
        self.current_spin.setRange(start, end)

        # Update the timeline
        current = self.current_spin.value()
        self.timeline.set_values(start, end, current)

    def update_current(self):
        current = self.current_spin.value()
        self.timeline.set_values(
            self.timeline.start, self.timeline.end, current)

    def set_frame_range(
            self, start: int, end: int, current: int | None = None):
        self.start_spin.setValue(start)
        self.end_spin.setValue(end)
        if current is not None:
            self.current_spin.setValue(current)


if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    timeline = TimelineWidget()
    timeline.set_frame_range(1, 300, 30)
    timeline.add_range((10, 30), name='name1')
    timeline.add_range((25, 45), (0.1, 0.9, 0.5, 0.35), name='name2')
    timeline.add_range((75, 90), (0.5, 0.1, 0.1, 0.35))
    # timeline.clear_ranges()
    timeline.show()
    sys.exit(app.exec_())
