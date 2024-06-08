import sys
from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QSizePolicy

class ResponsiveTableApp(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setGeometry(100, 100, 700, 300)
        self.setWindowTitle('Responsive Table App')

        # Create a table widget
        table_widget = QTableWidget(self)
        table_widget.setRowCount(3)  # Set the number of rows
        table_widget.setColumnCount(3)  # Set the number of columns

        # Set table headers
        table_widget.setHorizontalHeaderLabels(['Column 1', 'Column 2', 'Column 3'])

        # Insert values into the table
        for row in range(3):
            for col in range(3):
                item = QTableWidgetItem(f'Row {row + 1}, Col {col + 1}')
                table_widget.setItem(row, col, item)

        # Set table to expand horizontally and vertically
        table_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Create a vertical layout
        layout = QVBoxLayout(self)
        layout.addWidget(table_widget)

        # Set layout
        self.setLayout(layout)

        self.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ResponsiveTableApp()
    sys.exit(app.exec_())
