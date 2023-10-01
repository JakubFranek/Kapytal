from PyQt6.QtCore import QModelIndex, QModelRoleDataSpan, QSortFilterProxyModel


class MultiDataProxyModel(QSortFilterProxyModel):
    def multiData(
        self, index: QModelIndex, roleDataSpan: QModelRoleDataSpan  # noqa: N803
    ) -> None:
        self.sourceModel().multiData(self.mapToSource(index), roleDataSpan)
