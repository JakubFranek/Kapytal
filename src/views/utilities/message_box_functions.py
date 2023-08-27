from PyQt6.QtWidgets import QMessageBox, QWidget


def ask_yes_no_question(
    parent: QWidget, question: str, title: str, *, warning: bool = False
) -> bool:
    if not warning:
        answer = QMessageBox.question(
            parent,
            title,
            question,
            buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            defaultButton=QMessageBox.StandardButton.No,
        )
    else:
        answer = QMessageBox.warning(
            parent,
            title,
            question,
            buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            defaultButton=QMessageBox.StandardButton.No,
        )
    return answer == QMessageBox.StandardButton.Yes


def ask_yes_no_cancel_question(
    parent: QWidget, question: str, title: str, *, warning: bool = False
) -> bool | None:
    if not warning:
        answer = QMessageBox.question(
            parent,
            title,
            question,
            buttons=QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No
            | QMessageBox.StandardButton.Cancel,
            defaultButton=QMessageBox.StandardButton.Cancel,
        )
    else:
        answer = QMessageBox.warning(
            parent,
            title,
            question,
            buttons=QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No
            | QMessageBox.StandardButton.Cancel,
            defaultButton=QMessageBox.StandardButton.Cancel,
        )
    return (
        True
        if answer == QMessageBox.StandardButton.Yes
        else False
        if answer == QMessageBox.StandardButton.No
        else None
    )
