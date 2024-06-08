# button.py
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from process import process
import multiprocessing
from knn_classifier import kNNClassifier
import time
import os
import csv
import pyautogui as pg

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.label_path = ""
        self.keypoints_path = ""
        self.model_name = ""
        self.process_camera = None
        self.count = 0
        # self.camera_running = False  # Flag to track camera state
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateLabel)
        self.program()
        
        

    def program(self):
        layout = QVBoxLayout()

        # Create a tab widget
        tab_widget = QTabWidget(self)

        # Create and add home tab
        home_tab = QWidget()
        home_layout = QVBoxLayout(home_tab)

        # Add 'Turn On' button and radio buttons in a horizontal layout
        button_layout = QHBoxLayout()
        self.button = QPushButton("Turn On", self)
        self.button.clicked.connect(self.buttonClicked)
        self.button.setStyleSheet('background-color: green;'
                                  'color: white')
        button_font = self.button.font()
        button_font.setFamily('Montserrat')
        button_font.setBold(True)
        button_font.setPointSize(10)

        self.button.setFont(button_font) 
        self.radio1 = QRadioButton('On')
        self.radio2 = QRadioButton('Off')
        self.radio2.setChecked(True)
        button_layout.addWidget(self.button)
        button_layout.addWidget(self.radio1)
        button_layout.addWidget(self.radio2)
        button_layout.setAlignment(Qt.AlignTop)

        home_layout.addLayout(button_layout)

        # Add 'haha' label
        self.label1 = QLabel("haha", alignment = Qt.AlignCenter)
        home_layout.addWidget(self.label1)

        # Add 'Selected Gesture:' label
        selected_gesture_label = QLabel("Selected Gesture:", alignment = Qt.AlignCenter)
        home_layout.addWidget(selected_gesture_label)

        # Add a QComboBox to list all available gesture CSV files
        self.gesture_combo_box = QComboBox(home_tab)
        # self.populate_gesture_list()
        self.gesture_combo_box.currentIndexChanged.connect(self.handle_gesture_combo_box_selection)
        
        home_layout.addWidget(self.gesture_combo_box)

        tab_widget.addTab(home_tab, "Home")

        # Create and add gesture list tab
        gesture_list_tab = QWidget()
        gesture_list_layout = QVBoxLayout(gesture_list_tab)

        # Add a list widget to display the available gesture CSV files
        self.gesture_list_widget = QListWidget(gesture_list_tab)
        self.populate_gesture_list()
        gesture_list_layout.addWidget(self.gesture_list_widget)

        # Connect the item double-clicked signal to a handler
        self.gesture_list_widget.itemDoubleClicked.connect(self.handle_csv_double_click)

        tab_widget.addTab(gesture_list_tab, "Gesture List")

        layout.addWidget(tab_widget)

        self.setLayout(layout)
        self.show()

    def buttonClicked(self):
        button_text = self.button.text()
        newButton_text = 'Turn Off' if button_text == 'Turn On' else 'Turn On'
        self.button.setText(newButton_text)

        button_color = self.button.palette().button().color()
        newButton_color = QColor('red') if button_color == QColor('green') else QColor('green')
        self.button.setStyleSheet(f'background-color: {newButton_color.name()};'
                                  'color: white')
        self.radio1.setEnabled(not self.radio1.isEnabled())
        self.radio2.setEnabled(not self.radio2.isEnabled())
        x = 'off'
        if self.radio1.isChecked():
            x = 'on'
            
        if newButton_text == 'Turn Off':
            # if not self.camera_running:
                self.queue = multiprocessing.Queue()
                self.queueState = 1
                # print(self.label_path)
                self.process_camera = multiprocessing.Process(target=process.process, args=(self.queue, self.keypoints_path, self.label_path, self.model_name, 0))
                self.process_camera.start()
                # self.camera_running = True
        elif newButton_text == 'Turn On':
            # if self.camera_running:
                self.process_camera.terminate()
                self.process_camera.join()
                # self.camera_running = False
        
        self.timer.start(10)
        
    def updateLabel(self):
        if self.button.text() == 'Turn On':
            self.queue.close()
            self.queueState = 0
            self.queue.join_thread()
            self.timer.stop()
        else:
            # if self.queueState == 0:
            #      self.queue = multiprocessing.Queue()
            #      self.queueState = 1
            #      print("haha")
            if self.queueState == 1:
                try:
                     hand_sign = self.queue.get(timeout=1)
                     self.label1.setText(hand_sign)
                     print(hand_sign)
                except Exception:
                     self.label1.setText("None")
                # hand_sign = self.queue.get()
                # # #  self.label1.setText(str(self.count))
                # self.label1.setText(hand_sign)
                # # # self.count += 1
                # # print(self.queue.empty())
                # # hand_sign = self.queue.get()
                # print(hand_sign)
            else:
                 self.label1.setText("None")
                 print(self.queue.empty())
            # print(self.queue.empty())
            # hand_sign = self.queue.get()
            # print(hand_sign)

    def handle_csv_double_click(self, item):
        selected_csv_path = os.path.join('model', item.text())
        edit_dialog = EditCSVDialog(selected_csv_path, self)
        result = edit_dialog.exec_()
        if result == QDialog.Accepted:
            edit_dialog.save_csv_content()
            print(f"Changes saved for {selected_csv_path}")

        
    def populate_gesture_list(self):
        gesture_folder_path = 'model'  # Replace with the actual path
        gesture_files = [f for f in os.listdir(gesture_folder_path) if f.endswith('.csv')]
        self.gesture_combo_box.addItems(gesture_files)

        for gesture_file in gesture_files:
            item = QListWidgetItem(gesture_file)
            self.gesture_list_widget.addItem(item)

        # Connect the item clicked signal to a handler
        self.gesture_list_widget.itemClicked.connect(self.handle_gesture_selection)

    def handle_gesture_selection(self, item):
        selected_gesture = item.text()
        print(f"Selected Gesture: {selected_gesture}")

    def handle_gesture_combo_box_selection(self, index):
        self.selected_file_name = self.gesture_combo_box.itemText(index)
        self.label_path = os.path.join('model', f'{self.selected_file_name}')
        self.keypoints_path = os.path.join('model', 'keypoints', f'keypoints_{self.selected_file_name}')
        self.model_name = self.selected_file_name.split('.')[0] + '.sav'
        print(f"Selected Gesture from Combo Box: {self.label_path}")
        print(f"Selected Gesture points from Combo Box: {self.keypoints_path}")
        # Perform any additional actions based on the selected gesture file

    def get_current_selected_item(self):
        # Retrieve the current index
        current_index = self.gesture_combo_box.currentIndex()

        # Retrieve the text of the currently selected item
        current_selected_item = self.gesture_combo_box.itemText(current_index)

        # Print or use the currently selected item
        print(f"Currently selected item: {current_selected_item}")


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

if __name__ == '__main__':
    app = QApplication([])
    widget = MyWidget()
    app.exec_()
