import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QPushButton, QHBoxLayout, QLineEdit, QLabel, QDialog, QVBoxLayout, QFormLayout
import pyodbc

class EditDialog(QDialog):
    def __init__(self, column_names, parent=None):
        super(EditDialog, self).__init__(parent)

        self.column_names = column_names
        self.line_edits = []

        layout = QFormLayout()

        for column_name in self.column_names:
            line_edit = QLineEdit()
            self.line_edits.append(line_edit)
            layout.addRow(QLabel(column_name), line_edit)

        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Replace these placeholders with your actual values
        server = 'DESKTOP-95HCNL6\SQLEXPRESS'
        database = 'PracticeDB'
        connection_string = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'

        # Establish a connection
        self.connection = pyodbc.connect(connection_string)

        # Create a cursor for executing SQL queries
        self.cursor = self.connection.cursor()

        # Example query
        self.cursor.execute('SELECT * FROM Departments')
        self.rows = self.cursor.fetchall()

        # Get column names
        self.column_names = [column[0] for column in self.cursor.description]

        # Close the cursor and connection (for now, we'll open them as needed)
        self.cursor.close()
        self.connection.close()

        # Create a PyQt5 table widget
        self.table_widget = QTableWidget()
        self.setup_table(self.rows, self.column_names)

        # Create buttons
        self.add_button = QPushButton('Add')
        self.update_button = QPushButton('Update')
        self.delete_button = QPushButton('Delete')

        # Connect buttons to functions
        self.add_button.clicked.connect(self.add_record)
        self.update_button.clicked.connect(self.update_record)
        self.delete_button.clicked.connect(self.delete_record)

        # Set up the main window
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        # Layout for buttons
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.delete_button)

        # Main layout
        layout = QVBoxLayout(self.central_widget)
        layout.addWidget(self.table_widget)
        layout.addLayout(button_layout)

    def setup_table(self, rows, column_names):
        # Set the number of rows and columns
        self.table_widget.setRowCount(len(rows))
        self.table_widget.setColumnCount(len(column_names))

        # Set column names as table header
        self.table_widget.setHorizontalHeaderLabels(column_names)

        # Populate the table with data
        for i, row in enumerate(rows):
            for j, value in enumerate(row):
                item = QTableWidgetItem(str(value))
                self.table_widget.setItem(i, j, item)

    def add_record(self):
        # Implement the logic to add a record
        pass

    def update_record(self):
        # Implement the logic to update a record
        pass

    def delete_record(self):
        # Implement the logic to delete a record
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
