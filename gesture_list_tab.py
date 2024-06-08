# gesture_list_tab.py
from PyQt5.QtWidgets import *

import csv
import os

# class GestureListTab(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.setup_ui()

#     def setup_ui(self):
#         layout = QVBoxLayout()

#         self.gesture_list_widget = QListWidget(self)
#         # ... (copy the list widget setup code from MyWidget class)
#         self.populate_gesture_list()
#         # ... (copy the list widget setup code from MyWidget class)
#         layout.addWidget(self.gesture_list_widget)

#         self.gesture_list_widget.itemDoubleClicked.connect(self.handle_csv_double_click)

#         self.setLayout(layout)


#     def handle_csv_double_click(self, item):
#         selected_csv_path = os.path.join('model', item.text())
#         edit_dialog = EditCSVDialog(selected_csv_path, self)
#         result = edit_dialog.exec_()
#         if result == QDialog.Accepted:
#             edit_dialog.save_csv_content()
#             print(f"Changes saved for {selected_csv_path}")

        
#     def populate_gesture_list(self):
#         gesture_folder_path = 'model'  # Replace with the actual path
#         gesture_files = [f for f in os.listdir(gesture_folder_path) if f.endswith('.csv')]

#         for gesture_file in gesture_files:
#             item = QListWidgetItem(gesture_file)
#             self.gesture_list_widget.addItem(item)

#         # Connect the item clicked signal to a handler
#         self.gesture_list_widget.itemClicked.connect(self.handle_gesture_selection)

#     def handle_gesture_selection(self, item):
#         selected_gesture = item.text()
#         print(f"Selected Gesture: {selected_gesture}")


class EditCSVDialog(QDialog):
    def __init__(self, csv_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit CSV Content")
        self.layout = QVBoxLayout(self)

        self.text_edit = QTextEdit(self)
        self.layout.addWidget(self.text_edit)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel, self)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

        self.csv_path = csv_path
        self.load_csv_content()

    def load_csv_content(self):
        try:
            with open(self.csv_path, 'r') as file:
                reader = csv.reader(file)
                first_row = next(reader)
                csv_content = '\n'.join(','.join(row) for row in reader)
                self.text_edit.setPlainText(','.join(first_row) + '\n' + csv_content)
        except Exception as e:
            print(f"Error loading CSV content: {e}")

    def save_csv_content(self):
        try:
            new_content = self.text_edit.toPlainText()
            rows = [row.split(',') for row in new_content.split('\n')]
            with open(self.csv_path, 'w', newline='') as file:
                writer = csv.writer(file)
                for row in rows:
                    writer.writerow(row)
        except Exception as e:
            print(f"Error saving CSV content: {e}")