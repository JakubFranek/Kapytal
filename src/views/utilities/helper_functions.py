from PyQt6.QtWidgets import QTableView


def calculate_table_width(table: QTableView) -> int:
    return table.horizontalHeader().length() + table.verticalHeader().width()
