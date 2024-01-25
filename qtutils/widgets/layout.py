from PySide2.QtWidgets import QWidget, QFormLayout, QLabel


def get_widgets_from_form_layout(
        layout: QFormLayout,
        field_only: bool = False,
        filter_labels: list[str] | None = None,
        flatten: bool = False) -> list[QWidget] | list[tuple[QLabel, QWidget]]:
    result = []
    for i in range(layout.rowCount()):
        label_item = layout.itemAt(i, QFormLayout.LabelRole)
        label_widget = label_item.widget()
        if filter_labels is not None:
            if label_widget.text() not in filter_labels:
                continue
        field_item = layout.itemAt(i, QFormLayout.FieldRole)
        field_widget = field_item.widget()
        if field_only:
            result.append(field_widget)
        else:
            if flatten:
                result.extend([label_widget, field_widget])
            else:
                result.append((label_widget, field_widget))
    return result
