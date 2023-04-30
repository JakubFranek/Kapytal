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
