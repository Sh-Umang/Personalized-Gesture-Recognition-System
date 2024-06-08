import sys
import os
import csv

from PyQt5.QtWidgets import *

from db_sqlite3 import db_connector

class ProfileTab(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CSV Viewer")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)
        self.selected_key = ""

        self.create_widgets()
        self.show()

    def create_widgets(self):
        master_layout = QVBoxLayout()
        self.label1 = QLabel("Select Model:")
        self.comboBox1 = QComboBox()
        # self.comboBox1.addItems(self.get_csv_files_in_directory('model'))

        self.label2 = QLabel("Select Profile:")
        self.comboBox2 = QComboBox()
        # self.comboBox2.addItems(self.get_csv_files_in_directory1('model/profiles'))
        self.populateComboBox(1)
        self.comboBox1.currentIndexChanged.connect(self.updateComboBox2)
        
        # self.comboBox1.currentIndexChanged.connect(self.updateComboBox2)

        self.table = QTableWidget(self)
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Gesture", "Key Bindings"])
        self.table.cellClicked.connect(self.updateKeyField)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.comboBox2.currentIndexChanged.connect(self.updateTable)

        self.key_label = QLabel("Key Combination:")
        self.key_field = QLineEdit()
        self.set_button = QPushButton("Set", self)
        self.set_button.setStyleSheet(f"background-color: 'darkBlue';"
                                  "color: white")
        self.set_button.clicked.connect(self.setKey)

        # self.save_button = QPushButton("Save", self)
        # self.save_button.clicked.connect(self.save_csv)

        self.add_button = QPushButton("Add New Profile", self)
        self.add_button.clicked.connect(self.add_profile)

        self.make_table_readonly()

        self.layout.addWidget(self.label1)
        self.layout.addWidget(self.comboBox1)
        self.layout.addWidget(self.label2)
        self.layout.addWidget(self.comboBox2)
        self.layout.addWidget(self.add_button)
        self.layout.addWidget(self.key_label)
        self.layout.addWidget(self.key_field)
        self.layout.addWidget(self.set_button)
        self.layout.addWidget(self.table)
        # self.layout.addWidget(self.save_button)

    def populateComboBox(self, x):
        if x == 1: #for comboBox1
            self.comboBox1.clear()
            db_connector.connect()
            results = db_connector.execute("select model_name from model")
            if len(results):
                for val in results:
                    self.comboBox1.addItem(val[0])
                self.populateComboBox(2)
            db_connector.close()

        if x == 2: #for comboBox2
            self.comboBox2.clear()
            model_name = self.comboBox1.currentText()
            model_id = self.getModelID(model_name)
            db_connector.connect()
            results = db_connector.execute("select profile_name from profile where model_id = ?", (model_id,))
            if len(results):
                for val in results:
                    self.comboBox2.addItem(val[0])
            db_connector.close()
        
    def updateComboBox2(self, _):
        self.populateComboBox(2)

    def add_profile(self):
        if self.comboBox1.currentText():
            model_id = self.getModelID(self.comboBox1.currentText())
            profile_name, ok = QInputDialog.getText(self, 'Add a new model', 'Enter the profile\'s name:')
            if ok and profile_name:
                profile_name = profile_name.lower()
                db_connector.connect()
                result = db_connector.execute(f"select * from profile where model_id = ? and profile_name = ?", (model_id, profile_name))
                if len(result) == 0:
                    query = "insert into Profile (model_id, profile_name) values (?, ?)"
                    db_connector.execute(query, (model_id, profile_name))
                    QMessageBox.information(self, 'Profile Created', f'Successfully created a {profile_name} profile')
            
                    self.populateComboBox(2) # 2 for comboBox2

                else:
                    QMessageBox.warning(self, 'Duplicate Profile',f'{profile_name} profile already exists')
                db_connector.close()


    def getModelID(self, model_name):
        try:
            db_connector.connect()
            query = "select model_id from Model where model_name = ?"
            result = db_connector.execute(query, (model_name,))
            return int(result[0][0])
        except:
            pass

    def getProfileID(self, profile_name):
        try:
            db_connector.connect()
            query = "select profile_id from Profile where profile_name = ?"
            result = db_connector.execute(query, (profile_name,))
            return str(result[0][0])
        except:
            pass

    def updateTable(self, index):
        self.reset()
        model_id = self.getModelID(self.comboBox1.currentText())
        db_connector.connect()
        query = "select gesture_name from Gesture where model_id = ?"
        # query = "select gesture_name from gesture where model_id = ?"
        result = db_connector.execute(query, (model_id,))
        db_connector.close()

        self.table.clearContents()
        self.table.setRowCount(0)
        
        if len(result):
            self.table.setRowCount(len(result))

            for row, row_item in enumerate(result):
                item1 = QTableWidgetItem(str(row_item[0]))
                self.table.setItem(row, 0, item1)
                db_connector.connect()
                query = "select key_string from keyboardbind where profile_id in (select profile_id from profile where profile_name = ?) and gesture_id in (select gesture_id from gesture where gesture_name = ? and model_id = ?)"
                result = db_connector.execute(query, (self.comboBox2.currentText(), row_item[0], model_id))
                if len(result):
                    item2 = QTableWidgetItem(str(result[0][0]))
                    self.table.setItem(row, 1, item2)
                db_connector.close()    

    def updateKeyField(self):
        self.key_field.clear()
        try: #because self.selected_key = selected_items[1].text() throws error out of index exception when selected_items[1] 
            selected_items = self.table.selectedItems()
            if selected_items:
                self.selected_key = selected_items[1].text()  
                self.key_field.setText(self.selected_key)
        except:
            pass
        # print(selected_items[0].text())

    def setKey(self):
        if self.comboBox1.currentText() and self.comboBox2.currentText():
            key_string = self.key_field.text().lower()
            #get id of gesture selected from table that corresponds to the model
            gesture_name = self.table.selectedItems()[0].text()
            model_id = self.getModelID(self.comboBox1.currentText())
            db_connector.connect()
            result = db_connector.execute("select gesture_id from gesture where gesture_name = ? and model_id = ?", (gesture_name, model_id))
            gesture_id = result[0][0]
            profile_id = self.getProfileID(self.comboBox2.currentText())
            result = db_connector.execute("select * from KeyboardBind where key_string = ? and profile_id = ?", (key_string, profile_id))
            if len(result):
                QMessageBox.warning(self, "Duplicate Key Combination", "Key combination already exists")
            else:
                result = db_connector.execute("select * from KeyboardBind where profile_id = ? and gesture_id = ?", (profile_id, gesture_id))
                if len(result):
                    db_connector.execute("update KeyboardBind set key_string = ? where profile_id = ? and gesture_id = ?", (key_string, profile_id, gesture_id))
                else:
                    db_connector.execute("insert into KeyboardBind (profile_id, gesture_id, key_string) values (?, ?, ?)", (profile_id, gesture_id, key_string))
                self.updateTable("")
                self.reset()
            db_connector.close()
        
        else:
            QMessageBox.warning(self, "No model or profile selected", "Select both model and profile")
    
    def reset(self):
        #clear the field after updating
        self.key_field.clear()

        #clear the selected Gesture name after updating
        self.selected_key = ""

    def make_table_readonly(self):
        # Set the edit triggers to NoEditTriggers
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Set the selection behavior to select entire rows
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)


    # def updateComboBox2(self, index):
    #     self.comboBox2.clear()
    #     current_item_name = self.comboBox1.currentText()
    #     current_item_name = current_item_name.split(".")[0]
    #     csv_files = [file for file in os.listdir('model/profiles') if file.endswith(".csv") and file.startswith(current_item_name)]
    #     self.comboBox2.addItems(csv_files)


    # def get_csv_files_in_directory(self, directory):
    #     csv_files = [file for file in os.listdir(directory) if file.endswith(".csv")]
    #     return csv_files
    
    # def get_csv_files_in_directory1(self, directory):
    #     self.comboBox2.clear()
    #     current_item_name = self.comboBox1.currentText()
    #     current_item_name = current_item_name.split(".")[0]
    #     csv_files = [file for file in os.listdir(directory) if file.endswith(".csv") and file.startswith(current_item_name)]
    #     return csv_files

    def load_csvs(self):
        self.reset_table()
        csv_file1 = os.path.join('model', self.comboBox1.currentText())
        csv_file2 = os.path.join('model/profiles', self.comboBox2.currentText())
        try:
            with open(csv_file1, 'r') as file1, open(csv_file2, 'r') as file2:
                csv_reader1 = csv.reader(file1)
                csv_reader2 = csv.reader(file2)

                rows1 = list(csv_reader1)
                rows2 = list(csv_reader2)

                for row_position in range(len(rows1)):
                    self.table.insertRow(row_position)

                    if row_position < len(rows1):
                        self.table.setItem(row_position, 0, QTableWidgetItem(rows1[row_position][0]))

                    if row_position < len(rows2):
                        self.table.setItem(row_position, 1, QTableWidgetItem(rows2[row_position][0]))
        except:
            QMessageBox.warning(self, 'Select a profile', f'No profile selected ')

    def reset_table(self):
        self.table.clearContents()
        self.table.setRowCount(0)

    def save_csv(self):
        csv_file2 = os.path.join('model/profiles', self.comboBox2.currentText())
        try:
            with open(csv_file2, 'w', newline='') as file2:
                csv_writer2 = csv.writer(file2)

                for row_position in range(self.table.rowCount()):
                    item = self.table.item(row_position, 1)
                    if item is not None:
                        csv_writer2.writerow([item.text()])
                    else:
                        csv_writer2.writerow([""])
                QMessageBox.information(self, 'Profile Saved', f'{self.comboBox2.currentText()} Saved ')
        except:
            QMessageBox.warning(self, 'Select a profile', f'No profile selected ')

    # def add_csv(self):
    #     current_item_name = self.comboBox1.currentText()
    #     current_item_name = current_item_name.split(".")[0] + '_'
    #     new_csv_name, ok = QInputDialog.getText(self, 'Add CSV File', 'Enter the new CSV file name:')
    #     if ok and new_csv_name:
    #         new_csv_path = os.path.join('model/profiles', current_item_name + new_csv_name + '.csv')
    #         with open(new_csv_path, 'w', newline=''):
    #             pass
    #         # Update the combo box items
    #         self.comboBox2.clear()
    #         self.comboBox2.addItems(self.get_csv_files_in_directory1('model/profiles'))
                    
    # def add_csv(self):
    #     current_item_name = self.comboBox1.currentText()
    #     current_item_name = current_item_name.split(".")[0] + '_'
    #     new_csv_name, ok = QInputDialog.getText(self, 'Add CSV File', 'Enter the new CSV file name:')
    #     if ok and new_csv_name:
    #         new_csv_path = os.path.join('model/profiles', current_item_name + new_csv_name + '.csv')

    #         # Check if the file already exists
    #         if os.path.exists(new_csv_path):
    #             QMessageBox.warning(self, 'File Already Exists', f'The file already exists.')
    #         else:
    #             with open(new_csv_path, 'w', newline=''):
    #                 pass
    #             # Update the combo box items
    #             self.comboBox2.clear()
    #             self.comboBox2.addItems(self.get_csv_files_in_directory1('model/profiles'))

class NonEditableDelegate(QItemDelegate):
    def createEditor(self, parent, option, index):
        if index.column() == 0:
            return None
        return super().createEditor(parent, option, index)

# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     window = CSVViewer()
#     delegate = NonEditableDelegate()
#     window.table.setItemDelegateForColumn(0, delegate)
#     sys.exit(app.exec_())
