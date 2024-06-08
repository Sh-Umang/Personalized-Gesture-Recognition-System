import sys
import os
import csv
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QLabel, QComboBox, QPushButton

class CSVViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CSV Viewer")
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
        self.comboBox2.addItems(self.get_csv_files_in_directory('model'))

        self.table = QTableWidget(self)
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["CSV 1", "CSV 2"])

        self.load_button = QPushButton("Load CSVs", self)
        self.load_button.clicked.connect(self.load_csvs)

        self.layout.addWidget(self.label1)
        self.layout.addWidget(self.comboBox1)
        self.layout.addWidget(self.label2)
        self.layout.addWidget(self.comboBox2)
        self.layout.addWidget(self.load_button)
        self.layout.addWidget(self.table)

    def get_csv_files_in_directory(self, directory):
        csv_files = [file for file in os.listdir(directory) if file.endswith(".csv")]
        return csv_files

    # def load_csvs(self):
    #     csv_file1 = os.path.join('model', self.comboBox1.currentText())
    #     csv_file2 = os.path.join('model', self.comboBox2.currentText())

    #     self.table.setRowCount(0)  # Clear existing rows

    #     with open(csv_file1, 'r') as file1, open(csv_file2, 'r') as file2:
    #         csv_reader1 = csv.reader(file1)
    #         csv_reader2 = csv.reader(file2)

    #         for row1, row2 in zip(csv_reader1, csv_reader2):
    #             # Add a new row to the table
    #             row_position = self.table.rowCount()
    #             self.table.insertRow(row_position)

    #             # Populate the cells with data from the CSV files
    #             self.table.setItem(row_position, 0, QTableWidgetItem(row1[0]))
    #             self.table.setItem(row_position, 1, QTableWidgetItem(row2[0]))

    def load_csvs(self):
        self.reset_table()
        csv_file1 = os.path.join('model', self.comboBox1.currentText())
        csv_file2 = os.path.join('model', self.comboBox2.currentText())

        with open(csv_file1, 'r') as file1, open(csv_file2, 'r') as file2:
            csv_reader1 = csv.reader(file1)
            csv_reader2 = csv.reader(file2)

            rows1 = list(csv_reader1)
            rows2 = list(csv_reader2)

            # Determine the maximum number of rows among the two CSV files
            # max_rows = max(len(rows1), len(rows2))
            # print(max_rows)
            # print(rows1)

            # self.table.setRowCount(max_rows)  # Set the table row count

            for row_position in range(len(rows1)):
                # Add a new row to the table
                self.table.insertRow(row_position)

                # Populate the cells with data from the CSV files
                if row_position < len(rows1):
                    self.table.setItem(row_position, 0, QTableWidgetItem(rows1[row_position][0]))
                    
                # else:
                #     self.table.setItem(row_position, 0, QTableWidgetItem(""))
                #     # print(rows1[row_position][0])
                    

                if row_position < len(rows2):
                    self.table.setItem(row_position, 1, QTableWidgetItem(rows2[row_position][0]))
                # else:
                #     self.table.setItem(row_position, 1, QTableWidgetItem(""))
                    # print(rows2[row_position][0])

    def reset_table(self):
        self.table.clearContents()  # Clear the contents of all items
        self.table.setRowCount(0)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CSVViewer()
    sys.exit(app.exec_())
