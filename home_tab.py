# home_tab.py
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import subprocess

import pyautogui as pg

import multiprocessing
import os
# import csv
# import ctypes

from keybinding import keybinding
from keypoint_classifier_labels import keypoint_classifier_labels
from process_new import process
from db_sqlite3 import db_connector

class HomeTab(QWidget):
    def __init__(self):
        super().__init__()
        self.keypoints_path = ""
        self.model_name = ""
        self.timer = QTimer()
        self.timer.timeout.connect(self.updateLabel)
        self.setup_ui()

    def setup_ui(self):

        #############Defining Layouts###############

        master_layout = QVBoxLayout()

        button_layout = QHBoxLayout()

        camOpt_layout = QVBoxLayout()

        gestureLbl_layout = QVBoxLayout()

        selectedMdl_layout = QVBoxLayout()

        selectedPfl_layout = QVBoxLayout()

        #########button_layout Widgets####################

        self.button = QPushButton("Turn On")
        self.button.setStyleSheet('background-color: green;''color: white;')
        # self.button.setFont(button_font)
        self.button.setFixedSize(150, 40)
        #Setting button click event
        self.button.clicked.connect(self.buttonClicked)
        #Adding button to layout
        button_layout.addWidget(self.button)
        button_layout.setAlignment(Qt.AlignCenter)

        ###########camOpt_layout Widgets###################

        self.label_CamShow = QLabel("Camera Option", alignment=Qt.AlignCenter)
        self.radio1 = QRadioButton('Show')
        self.radio2 = QRadioButton('Hide')
        self.radio1.setStyleSheet('font-weight: normal;')
        self.radio2.setStyleSheet('font-weight: normal;')
        self.radio2.setChecked(True)
        #Adding Widgets to layout
        radio_layout = QHBoxLayout()
        radio_layout.addWidget(self.radio1)
        radio_layout.addWidget(self.radio2)
        #Adding Widgets to layout
        camOpt_layout.addWidget(self.label_CamShow)
        camOpt_layout.addLayout(radio_layout)
        camOpt_layout.setAlignment(Qt.AlignCenter)



        #############gestureLbl_layout Widgets##################

        self.label_GestureDetected = QLabel("Detected Gesture: ", alignment = Qt.AlignCenter)
        self.label_Gesture = QLabel("None", alignment=Qt.AlignCenter)
        self.label_Gesture.setStyleSheet('font-weight: normal;')
        #Adding Widgets to layout
        gestureLbl_layout.addWidget(self.label_GestureDetected)
        gestureLbl_layout.addWidget(self.label_Gesture)

        ############selectedMdl_layout Widgets##################

        self.label_SelectedModel = QLabel("Selected Model", alignment=Qt.AlignCenter)
        self.gesture_combo_box = QComboBox(self)
        self.label_SelectedProfile = QLabel("Selected Profile", alignment=Qt.AlignCenter)
        self.profile_combo_box = QComboBox(self)

        #populating combobox with values
        self.populate_gesture_list("")
        
        #Setting default selected value of combobox
        self.gesture_combo_box.setCurrentIndex(0)
        self.populate_profile_list()
        self.gesture_combo_box.currentIndexChanged.connect(self.populate_profile_list)
        #Adding Widgets to layout
        selectedMdl_layout.addWidget(self.label_SelectedModel)
        selectedMdl_layout.addWidget(self.gesture_combo_box)
        selectedPfl_layout.addWidget(self.label_SelectedProfile)
        selectedPfl_layout.addWidget(self.profile_combo_box)


        master_layout.addLayout(gestureLbl_layout)
        master_layout.addLayout(selectedMdl_layout)
        master_layout.addLayout(selectedPfl_layout)
        master_layout.addLayout(camOpt_layout)
        master_layout.addLayout(button_layout)
        self.setLayout(master_layout)

        # self.application_profiles = self.read_csv_as_dict('model/applications/profile.csv')

        # Adjust spacing and margins
        button_layout.setSpacing(20)
        camOpt_layout.setSpacing(20)
        gestureLbl_layout.setSpacing(20)
        selectedMdl_layout.setSpacing(20)
        selectedPfl_layout.setSpacing(20)

        # Add margins to layout containers
        button_layout.setContentsMargins(20, 20, 20, 20)
        camOpt_layout.setContentsMargins(20, 20, 20, 20)
        gestureLbl_layout.setContentsMargins(20, 20, 20, 20)
        selectedMdl_layout.setContentsMargins(20, 20, 20, 20)
        selectedPfl_layout.setContentsMargins(20, 20, 20, 20)
        master_layout.setContentsMargins(20, 20, 20, 20)


    def buttonClicked(self):
        if self.gesture_combo_box.currentText() and self.profile_combo_box.currentText():
            button_text = self.button.text()
            newButton_text = 'Turn Off' if button_text == 'Turn On' else 'Turn On'
            self.button.setText(newButton_text)

            button_color = self.button.palette().button().color()
            newButton_color = QColor('red') if button_color == QColor('green') else QColor('green')
            self.button.setStyleSheet(f'background-color: {newButton_color.name()};'
                                    'color: white')
            self.radio1.setEnabled(not self.radio1.isEnabled())
            self.radio2.setEnabled(not self.radio2.isEnabled())
            cam_show = False
            if self.radio1.isChecked():
                cam_show = True

            self.handle_gesture_combo_box_selection(self.gesture_combo_box.currentIndex())

            if newButton_text == 'Turn Off':
                
                    self.queue = multiprocessing.Queue()
                    # self.queueState = 1
                    profile_id = self.profile_id()
                    self.process_camera = multiprocessing.Process(target=process.process, args=(self.queue, self.keypoints_path, self.label_path, self.model_name, 0, cam_show, profile_id))
                    self.process_camera.start()
                    
            elif newButton_text == 'Turn On':
                
                    self.process_camera.terminate()
                    self.process_camera.join()
                    
            
            self.timer.start(10)
        else:
             QMessageBox.warning(self, 'Cannot Start', 'No model or profile selected')
        
    def updateLabel(self):
        if self.button.text() == 'Turn On':
            self.queue.close()
            # self.queueState = 0
            self.queue.join_thread()
            self.timer.stop()
        else:
            # if self.queueState == 1:
                try:
                     hand_sign = self.queue.get(timeout=1.5)
                     profile_id = self.profile_id()
                    #  self.keybinding(hand_sign)
                    #  keybinding_text = keybinding.keybinding(hand_sign, profile_id)
                    #  self.gesture = self.keypoint_classifier_labels(hand_sign)
                     
                     self.gesture = keypoint_classifier_labels.keypoint_classifier_labels(hand_sign)
                     

                     print(hand_sign, "hand_sign from update_label")
                    
                     self.label_Gesture.setText(self.gesture)
                    #  print("haha")
                    #  application_name = self.get_active_window_title()
                    #  profile_name = self.application_profiles[application_name]
                
                     print(self.label_Gesture.text())
                    
                except Exception:
                     self.label_Gesture.setText("None")
                     print(self.label_Gesture.text())
                    

    def keypoint_classifier_labels(self, hand_sign_id):
        db_connector.connect()
        query = "select gesture_name from Gesture where gesture_id = ?"

        parameter = (int(hand_sign_id),)
        result = db_connector.execute(query, parameter)
        db_connector.close()
        return result[0][0]

    
    def keybinding(self, hand_sign_id):
        gesture_id = int(hand_sign_id)
        print(gesture_id, "gesture id from home_tab")
        profile_id = self.profile_id()

        print(profile_id, "profileid1 from hometab")
        db_connector.connect()
        result = db_connector.execute("select key_string from KeyboardBind where gesture_id = ? and profile_id = ?", (gesture_id, profile_id))
        print(result, "result from hometab")
        print(profile_id, "profileid2 from hometab")
        if len(result):
            action = result[0][0]
            action = action.strip().split(" ")
            print(action, "action from home_tab")
            if (action[0] == "open"):
                parameter = '%' + action[1] + '%'
                query = "select path from AppPath where prog_name like ?"
                db_connector.connect()
                result = db_connector.execute(query, (parameter,))
                if result:
                    subprocess.call(result[0][0])
                else:
                     pass
                db_connector.close()
            else:
                pg.hotkey(action)
        else:
            print("query returned empty")
                 
    def populate_gesture_list(self, index):
        self.gesture_combo_box.clear()
        print("Connecting")
        db_connector.connect()
        query = "select model_name from Model"
        result = db_connector.execute(query)
        db_connector.close()
        for row in result:
            print(row)
            model_path = "model\models\\" + str(row[0]) + ".sav"
            print(model_path, "model_path from home_tab")
            if os.path.exists(model_path):
                self.gesture_combo_box.addItem(str(row[0]))

    def populate_profile_list(self):
        self.profile_combo_box.clear()
        db_connector.connect()
        query = "select profile_name from Profile where model_id in (select model_id from Model where model_name = ?)"
        parameter = (self.gesture_combo_box.currentText(),)
        result = db_connector.execute(query, parameter)
        db_connector.close()
        for row in result:
            self.profile_combo_box.addItem(str(row[0]))

    def profile_id(self):
        db_connector.connect()
        query = "select profile_id from Profile where profile_name = ?"
        parameter = (self.profile_combo_box.currentText(),)
        result = db_connector.execute(query, parameter)
        db_connector.close()
        return result[0][0]

        

    def handle_gesture_selection(self, item):
        selected_gesture = item.text()
        print(f"Selected Gesture: {selected_gesture}")

    def handle_gesture_combo_box_selection(self, index):
        self.selected_file_name = self.gesture_combo_box.itemText(index)
        self.label_path = os.path.join('model', 'labels', f'{self.selected_file_name}.csv')
        self.keypoints_path = os.path.join('model', 'keypoints', f'keypoints_{self.selected_file_name}.csv')
        self.model_name = 'model/models/' + self.selected_file_name + '.sav'
        print(f"Selected Gesture from Combo Box: {self.label_path}")
        print(f"Selected Gesture points from Combo Box: {self.keypoints_path}")
        

    def get_current_selected_item(self):
        # Retrieve the current index
        current_index = self.gesture_combo_box.currentIndex()

        # Retrieve the text of the currently selected item
        current_selected_item = self.gesture_combo_box.itemText(current_index)

        # Print or use the currently selected item
        print(f"Currently selected item: {current_selected_item}")


    
    ########FEATURE TO BE ADDED#############
    # def get_active_window_title(self):
    #     GetForegroundWindow = ctypes.windll.user32.GetForegroundWindow
    #     GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
    #     GetWindowText = ctypes.windll.user32.GetWindowTextW

    #     hwnd = GetForegroundWindow()
    #     length = GetWindowTextLength(hwnd)
    #     buff = ctypes.create_unicode_buffer(length + 1)
    #     GetWindowText(hwnd, buff, length + 1)
    #     return buff.value
        
    # def read_csv_as_dict(self,file_path):
    #     result_dict = {}
    #     with open(file_path, 'r') as csvfile:
    #         csv_reader = csv.reader(csvfile)
    #         for row in csv_reader:
    #             key = row[0]  # Assuming the first column contains keys
    #             value = row[1]  # Assuming the second column contains values
    #             result_dict[key] = value
    #     return result_dict