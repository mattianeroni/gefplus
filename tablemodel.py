from PyQt5.QtCore import Qt, QAbstractTableModel



class TableModel(QAbstractTableModel):

    """ An instace of this class represents an editable 
    table model used by the table view """

    def __init__(self, df):
        super(TableModel, self).__init__()
        self.df = df

    def rowCount(self, index):
        return self.df.shape[0]

    def columnCount(self, index):
        return self.df.shape[1]

    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable

    def data(self, index, role):
        if index.isValid():
            if role == Qt.DisplayRole or role == Qt.EditRole:
                value = self.df.iloc[index.row(), index.column()]
                return str(value)
            elif role == Qt.TextAlignmentRole:
                return Qt.AlignHCenter | Qt.AlignVCenter

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            # Set the value into the data frame.
            self.df.iloc[index.row(), index.column()] = value
            return True
        return False

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.df.columns.values[section]
        return super().headerData(section, orientation, role)