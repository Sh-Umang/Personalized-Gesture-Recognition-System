from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt

import multiprocessing

import os
import sys
import csv


from process_new import process
from train_model import train

# from feature_window1 import ModelCreatorWindow
from gesture_list_tab import EditCSVDialog
from knn_classifier import kNNClassifier
from db_sqlite3 import db_connector


class FeatureTab(QWidget):
    def __init__(self):
        super().__init__()

        self.selected_model_name = ""
        # self.csv_location = csv_location
        self.label_path = ""
        self.keypoints_path = ""
        self.modelsav_path = ""
        self.gesture_adder = None
        self.camOn = False
        self.init_ui()
        

    def init_ui(self):
        # Create a layout for the 'feature' tab
        layout = QVBoxLayout()
        model_name_label = QLabel("Available Models To Train:")
        model_name_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(model_name_label)

        # Create a QListWidget to display the CSV files
        self.model_list = QListWidget(self)
        # for csv_file in csv_files:
        #     item = QListWidgetItem(csv_file)
        #     self.model_list.addItem(item)

        # Get and update QListWidget with a list of all CSV files in the specified location
        # self.get_csv_files()


        self.model_list.itemSelectionChanged.connect(self.update_feature_button_state)
        # self.model_list.itemDoubleClicked.connect(self.handle_csv_double_click)
        

        # Add the QListWidget to the layout
        layout.addWidget(self.model_list)

        # Add a button to add a new CSV file
        self.add_button = QPushButton('Add New Model', self)
        self.delete_button = QPushButton('Delete Model')
        self.delete_button.setStyleSheet(f"background-color: 'darkRed';"
                                  "color: white")
        # self.add_button.clicked.connect(self.add_csv_file)
        self.add_button.clicked.connect(self.add_model)
        self.delete_button.clicked.connect(self.delete_model)
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.delete_button)
        layout.addLayout(button_layout)

        self.feature_button = QPushButton('Add Features', self)
        
        layout.addWidget(self.feature_button)


        
        self.feature_button.clicked.connect(self.feature)

        self.train_button = QPushButton('Train')
        
        layout.addWidget(self.train_button)

        
        self.train_button.clicked.connect(self.trainModel)
        self.populate_list()

        # Set the layout for the 'feature' tab
        self.setLayout(layout)
        

    def populate_list(self):
        self.feature_button.setEnabled(False)
        self.train_button.setEnabled(False)
        self.model_list.clear()
        db_connector.connect()
        query = "select model_name from Model"
        result = db_connector.execute(query)
        for model_name in result:
            item = QListWidgetItem(model_name[0])
            self.model_list.addItem(item)

    def update_feature_button_state(self): #also updates the label and keypoints path
        if not self.camOn: #runs only when cam is off
            selected_items = self.model_list.selectedItems()

            if selected_items:
                # Extract the name of the currently selected file
                self.selected_model_name = selected_items[0].text()
                print(self.selected_model_name)

                self.update_keypoints_modelsav_path()
                self.create_keypoints_modelsav_directory()
                # os.makedirs(f'model/keypoints', exist_ok=True)
                # # Update the keypoints_path
                # self.keypoints_path = os.path.join('model', 'keypoints', f'{self.selected_model_name}_keypoints.csv')
                # # If no keypoints csv file, this creates the file
                # if not os.path.exists(self.keypoints_path):
                #     with open(self.keypoints_path, 'w'):
                #         pass
                
                # self.label_path = os.path.join(self.csv_location, self.selected_model_name)

                # print(f"Label path: {self.label_path}")
                print(f"Keypoints path: {self.keypoints_path}")

            self.feature_button.setEnabled(bool(self.model_list.selectedItems()))
            self.train_button.setEnabled(bool(self.model_list.selectedItems()))
            self.train_button.setStyleSheet(f"background-color: 'darkCyan';"
                                  "color: white")
            self.feature_button.setStyleSheet(f"background-color: 'darkBlue';"
                                  "color: white")
        db_connector.close()

    def add_model(self):
        keypoints_path = 'model/keypoints'
        model_name, ok = QInputDialog.getText(self, 'Add a new model', 'Enter the model\'s name:')
        if ok and model_name:
            model_name = model_name.upper()
            db_connector.connect()
            result = db_connector.execute(f"select * from Model where model_name = ?", (model_name,))
            if len(result) == 0:
                query = "insert into Model (model_name) values (?)"
                db_connector.execute(query, (model_name,))
                QMessageBox.information(self, 'Model Created', f'Successfully created a {model_name} model')
                os.makedirs(keypoints_path, exist_ok=True)
                new_keypoints_csv_path = os.path.join(keypoints_path, model_name + '_keypoints.csv')
                with open(new_keypoints_csv_path, 'w'):
                    pass
                self.populate_list()

            else:
                QMessageBox.warning(self, 'Duplicate Model Name',f'{model_name} model already exists')
            db_connector.close()

    def delete_model(self):
        if  self.selected_model_name:
            db_connector.connect()
            # model_id = self.getModelID(self.selected_model_name)
            reply = QMessageBox.question(self, 'Yes/No Dialog', f'Do you want to delete {self.selected_model_name} model?', QMessageBox.Yes | QMessageBox.No)

            # Process the user's choice
            if reply == QMessageBox.Yes:
                #delete keypoints.csv file
                self.delete_keypoints()
                #delete model.sav file
                self.delete_model_sav()

                #deleting from database
                query = "delete from Model where model_name = ?"
                db_connector.execute(query, (self.selected_model_name,))
                QMessageBox.information(self, "Model Deleted", f"{self.selected_model_name} model deleted successfully")
                self.populate_list()

                self.reset()
            else:
                print('User clicked No')
            db_connector.close()
        elif not self.selected_model_name:
            QMessageBox.warning(self, "No Model Selected", "Select a model to delete")
        else:
            pass

    def getModelID(self, model_name):
        try:
            db_connector.connect()
            query = "select model_id from Model where model_name = ?"
            result = db_connector.execute(query, (model_name,))
            return int(result[0][0])
        except:
            pass

    def reset(self):

        #clear the selected Gesture name after updating
        self.selected_model_name = ""

    def delete_keypoints(self):
        if os.path.exists(self.keypoints_path): # updated from update_feature_button_state()
            os.remove(self.keypoints_path)
        else:
            pass

    def delete_model_sav(self):
        if os.path.exists(self.modelsav_path):
            os.remove(self.modelsav_path)

    def create_keypoints_modelsav_directory(self):
        os.makedirs(f'model/keypoints', exist_ok=True)
        # If no keypoints csv file, this creates the file
        if not os.path.exists(self.keypoints_path):
            with open(self.keypoints_path, 'w'):
                pass
        os.makedirs(f'model/models', exist_ok=True)

    def update_keypoints_modelsav_path(self):
        self.keypoints_path = os.path.join('model', 'keypoints', f'{self.selected_model_name}_keypoints.csv')
        self.modelsav_path = os.path.join('model', 'models', f'{self.selected_model_name}.sav')

    
    def feature(self):
        self.camOn = True #doing this for the feature button state update
        self.add_button.setEnabled(False)
        self.feature_button.setEnabled(False)
        self.train_button.setEnabled(False)
        self.queue = multiprocessing.Queue()
        # self.process_camera = multiprocessing.Process(target=process.process, args=(self.queue, self.keypoints_path, self.label_path, "", 1, True))
        # self.process_camera.start()

        #creating a dummy gesture for its gesture_id
        model_id = self.getModelID(self.selected_model_name)
        db_connector.connect()
        db_connector.execute("insert into gesture (model_id, gesture_name) values (?, ?)",(model_id, ""))
        result = db_connector.execute("select gesture_id from  gesture where gesture_name = ''")
        db_connector.close()
        gesture_id = result[0][0]

        process.process(self.queue, self.keypoints_path, gesture_id, "", 1, self.camOn, "")
        self.camOn = False
        keypoints_collected = self.queue.get()
        self.queue.close()
        self.queue.join_thread()
        if keypoints_collected:
            # Create the GestureAdder window if it doesn't exist
            if not self.gesture_adder:
                self.gesture_adder = GestureAdder(model_id, self.keypoints_path, keypoints_collected)

            print(keypoints_collected)
            # Show the GestureAdder window
            self.gesture_adder.show()
        else:
            db_connector.connect()
            db_connector.execute("delete from gesture where gesture_name = ''")
            db_connector.close()
        self.add_button.setEnabled(True)
        self.feature_button.setEnabled(True)
        self.train_button.setEnabled(True)
            



    def trainModel(self):
        try:
            train_model = train(7, self.selected_model_name)
        except:
            QMessageBox.warning(self, "Training Failed", "Add more features to the model to continue")


class GestureAdder(QWidget):
    def __init__(self, model_id, keypoints_path, keypoints):
        super().__init__()

        # Set the path to the CSV file
        # self.csv_file_path = label_path
        self.model_id = model_id
        self.csv_keypoints_file_path = keypoints_path
        self.keypoints = keypoints
        self.count = 0

        # Initialize the user interface
        self.init_ui()

    def init_ui(self):
        # Create a vertical layout
        layout = QVBoxLayout()

        # Create a textbox
        self.textbox = QLineEdit(self)
        layout.addWidget(self.textbox)

        # Create an "Add" button
        add_button = QPushButton('Add', self)
        add_button.clicked.connect(self.add_text)
        layout.addWidget(add_button)

        # Create a "Cancel" button
        cancel_button = QPushButton('Cancel', self)
        cancel_button.clicked.connect(self.closeWindow)
        layout.addWidget(cancel_button)

        # Set the layout for the main window
        self.setLayout(layout)

    def add_text(self):
        # Get the text from the textbox
        entered_text = self.textbox.text()
        entered_text = entered_text.lower()

        # Check if the textbox is empty
        if not entered_text:
            QMessageBox.warning(self, 'Empty Field', 'The text field cannot be empty.')
            return

        #checking for duplicate gesture name
        db_connector.connect()
        result = db_connector.execute("select * from gesture where model_id = ? and gesture_name = ?", (self.model_id, entered_text))
        if len(result):
            QMessageBox.warning(self, "Gesture Exists", "Gesture Name already exists")
            db_connector.close()
            return
        else:
            db_connector.execute("update gesture set gesture_name = ? where gesture_name = ''", (entered_text,))
            QMessageBox.information(self, 'Gesture Added', f'{entered_text} added to the gesture list')
            db_connector.close()
        # # Append the entered text to the CSV file
        # with open(self.csv_file_path, 'a', newline='') as csv_file:
        #     csv_writer = csv.writer(csv_file)
        #     csv_writer.writerow([entered_text])

        # QMessageBox.information(self, 'Gesture Added', f'{entered_text} added to the gesture list')
        self.textbox.clear()
        super(GestureAdder, self).close()
        # Clear the textbox after adding the text
        # self.textbox.clear()
        

    def closeWindow(self):
        try:
            self.count += 1
            # Read all entries from the CSV file
            with open(self.csv_keypoints_file_path, 'r', newline='') as csv_file:
                csv_reader = csv.reader(csv_file)
                entries = list(csv_reader)

            # Ensure that there are enough entries to remove
            if len(entries) >= self.keypoints:
                # Remove the last 'keypoints' number of entries
                entries = entries[:-self.keypoints]

                # Write the updated entries back to the CSV file
                with open(self.csv_keypoints_file_path, 'w', newline='') as csv_file:
                    csv_writer = csv.writer(csv_file)
                    csv_writer.writerows(entries)

                db_connector.connect()
                db_connector.execute("delete from gesture where gesture_name = ''")
                db_connector.close()

                # QMessageBox.information(self, 'Entries Removed', f'Last {self.keypoints} entries removed.')
                # print(f"{self.count} at if")
                # self.close()
            # else:
            #     # QMessageBox.warning(self, 'Not Enough Entries', 'There are not enough entries to remove.')
            #     print(f"{self.count} at else")
            #     # print("not enough points")
            super(GestureAdder, self).close()
        except Exception as e:
            QMessageBox.warning(self, 'Error', f'An error occurred: {str(e)}')



        


# class MainWindow(QTabWidget):
#     def __init__(self, csv_location):
#         super().__init__()

#         self.addTab(FeatureTab(csv_location), 'feature')

#         # Set window properties
#         self.setWindowTitle('featureing App')
#         self.setGeometry(300, 300, 400, 200)

# if __name__ == '__main__':
#     csv_location = 'model'  # Replace with the actual path to your CSV files
#     app = QApplication(sys.argv)
#     window = MainWindow(csv_location)
#     window.show()
#     sys.exit(app.exec_())