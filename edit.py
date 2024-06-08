import sys
import os
import csv
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QListWidget, QPushButton, QTextEdit, QLabel, QFileDialog

class CSVEditor(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('CSV Editor')

        # Widgets
        self.list_widget = QListWidget(self)
        self.edit_button = QPushButton('Edit Selected CSV', self)
        self.result_label = QLabel(self)
        self.csv_editor = QTextEdit(self)

        # Layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.list_widget)
        layout.addWidget(self.edit_button)
        layout.addWidget(self.result_label)
        layout.addWidget(self.csv_editor)

        # Signals
        self.list_widget.itemClicked.connect(self.load_csv_contents)
        self.edit_button.clicked.connect(self.save_csv_contents)

        # Initialize the list of CSV files
        self.populate_csv_list()

    def populate_csv_list(self):
        folder_path = 'model'  # Change this to your desired location
        csv_files = [file for file in os.listdir(folder_path) if file.endswith('.csv')]
        self.list_widget.addItems(csv_files)

    def load_csv_contents(self, item):
        selected_csv = item.text()
        file_path = os.path.join('model', selected_csv)  # Change this to your desired location
        with open(file_path, 'r') as csv_file:
            csv_contents = csv_file.read()
            self.csv_editor.setPlainText(csv_contents)

    def save_csv_contents(self):
        selected_item = self.list_widget.currentItem()
        if selected_item:
            selected_csv = selected_item.text()
            file_path = os.path.join('model', selected_csv)  # Change this to your desired location
            new_contents = self.csv_editor.toPlainText()

            with open(file_path, 'w') as csv_file:
                csv_file.write(new_contents)

            self.result_label.setText(f'Saved changes to {selected_csv}')
        else:
            self.result_label.setText('No CSV file selected')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    editor = CSVEditor()
    editor.setGeometry(100, 100, 800, 600)
    editor.show()
    sys.exit(app.exec_())
