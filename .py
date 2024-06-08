import sys
import os
import csv
from PyQt5.QtWidgets import *

class ProfileManager(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Profile Manager")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.create_widgets()
        self.show()

    def create_widgets(self):
        self.label1 = QLabel("Select CSV File 1:")
        self.comboBox1 = QComboBox()
        self.comboBox1.addItems(self.get_csv_files_in_directory('model'))

        self.label2 = QLabel("Select CSV File 2:")
        self.comboBox2 = QComboBox()
        self.comboBox2.addItems(self.get_csv_files_in_directory1('model/profiles'))
        
        self.comboBox1.currentIndexChanged.connect(self.updateComboBox2)

        self.label3 = QLabel("Enter Text:")
        self.text_field = QLineEdit()

        self.table = QTableWidget(self)
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Key", "Value"])

        self.add_button = QPushButton("Add to Profile", self)
        self.add_button.clicked.connect(self.add_to_profile)

        self.layout.addWidget(self.label1)
        self.layout.addWidget(self.comboBox1)
        self.layout.addWidget(self.label2)
        self.layout.addWidget(self.comboBox2)
        self.layout.addWidget(self.label3)
        self.layout.addWidget(self.text_field)
        self.layout.addWidget(self.add_button)
        self.layout.addWidget(self.table)

        # Load initial data into the table
        self.load_table_data()

    def updateComboBox2(self, index):
        self.comboBox2.clear()
        current_item_name = self.comboBox1.currentText()
        current_item_name = current_item_name.split(".")[0]
        csv_files = [file for file in os.listdir('model/profiles') if file.endswith(".csv") and file.startswith(current_item_name)]
        self.comboBox2.addItems(csv_files)


    def get_csv_files_in_directory(self, directory):
        csv_files = [file for file in os.listdir(directory) if file.endswith(".csv")]
        return csv_files
    
    def get_csv_files_in_directory1(self, directory):
        self.comboBox2.clear()
        current_item_name = self.comboBox1.currentText()
        current_item_name = current_item_name.split(".")[0]
        csv_files = [file for file in os.listdir(directory) if file.endswith(".csv") and file.startswith(current_item_name)]
        return csv_files


    def load_table_data(self):
        csv_file_path = os.path.join('model/applications/profile.csv')
        try:
            with open(csv_file_path, 'r') as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    self.add_row_to_table(row[0], row[1])
        except FileNotFoundError:
            # Handle file not found error
            pass

    def add_row_to_table(self, key, value):
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)
        self.table.setItem(row_position, 0, QTableWidgetItem(key))
        self.table.setItem(row_position, 1, QTableWidgetItem(value))

    def add_to_profile(self):
        key = self.text_field.text()
        value = self.comboBox2.currentText()
        
        if key and value:
            csv_file_path = os.path.join('model/applications/profile.csv')
            with open(csv_file_path, 'a', newline='') as file:
                csv_writer = csv.writer(file)
                csv_writer.writerow([key, value])

            # Update the table with the new data
            self.add_row_to_table(key, value)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ProfileManager()
    sys.exit(app.exec_())
