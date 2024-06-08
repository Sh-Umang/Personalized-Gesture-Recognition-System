import sys
import csv
import os

from PyQt5.QtWidgets import *

from db_sqlite3 import db_connector

class GestureTab(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_gesture_name = ""
        # Initialize the UI components
        self.init_ui()

    def init_ui(self):
        # Create a combo box
        self.comboBox = QComboBox(self)
        self.populateComboBox()
        self.comboBox.currentIndexChanged.connect(self.updateTable)

        self.gestureName_label = QLabel("Gesture Name:")
        self.gestureName_field = QLineEdit()
        self.update_button = QPushButton("Update")
        self.delete_button = QPushButton("Delete")
        self.delete_button.setStyleSheet(f"background-color: 'darkRed';"
                                  "color: white")
        self.update_button.clicked.connect(self.changeGestureName)
        self.delete_button.clicked.connect(self.deleteGesture)

        # Create a table with 3 columns
        self.tableWidget = QTableWidget(self)
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setHorizontalHeaderLabels(["Sno.", "Gesture Name"])
        self.tableWidget.cellClicked.connect(self.updateGestureNameField)

        # # Add some dummy data to the table
        # self.add_dummy_data()

        # Make table readonly and enable row selection
        self.make_table_readonly()

        # Create a layout and add the combo box and table to it
        layout = QVBoxLayout(self)
        layout.addWidget(self.comboBox)
        layout.addWidget(self.gestureName_label)
        layout.addWidget(self.gestureName_field)
        layout.addWidget(self.update_button)
        layout.addWidget(self.delete_button)
        layout.addWidget(self.tableWidget)

        # Set the layout for the widget
        self.setLayout(layout)

        #Populate Table
        self.updateTable(None)
        # print(self.getModelID(self.comboBox.currentText()))

        # Set the main window properties
        self.setWindowTitle('Combo Box and Table Example')
        self.setGeometry(100, 100, 600, 400)

    def populateComboBox(self):
        self.comboBox.clear()
        db_connector.connect()
        query = "select model_name from Model"
        result = db_connector.execute(query)
        if len(result):
            for row in result:
                self.comboBox.addItem(row[0])
        db_connector.close()

    def updateTable(self, index):
        self.reset()

        model_name = self.comboBox.currentText()
        db_connector.connect()
        query = "select gesture_name from Gesture where model_id in (select model_id from Model where model_name = ?)"
        result = db_connector.execute(query, (model_name,))
        db_connector.close()

        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)
        
        if len(result):
            self.tableWidget.setRowCount(len(result))


            for row, row_item in enumerate(result):
                col1_item = QTableWidgetItem(str(row+1))
                col2_item = QTableWidgetItem(str(row_item[0]))
                self.tableWidget.setItem(row, 0, col1_item)
                self.tableWidget.setItem(row, 1, col2_item)

    def updateGestureNameField(self):
        selected_items = self.tableWidget.selectedItems()
        if selected_items:
            self.selected_gesture_name = selected_items[1].text()  
            self.gestureName_field.setText(self.selected_gesture_name)

    def changeGestureName(self):
        db_connector.connect()
        model_id = self.getModelID(self.comboBox.currentText())
        query = "select * from Gesture where gesture_name = ? and model_id = ?"
        result = db_connector.execute(query, (self.gestureName_field.text(),))
        if not self.selected_gesture_name:
            QMessageBox.warning(self, "No gesture selected", "Select gesture from the table to update")
        elif len(result):
            QMessageBox.warning(self, "Duplicate Gesture", "Gesture Already Exists")
        elif not self.gestureName_field.text().strip():
            QMessageBox.warning(self, "Empty Gesture Name", "Gesture Name Invalid")
        else:
            query = "update Gesture set gesture_name = ? where gesture_name = ? and model_id = ?"
            db_connector.execute(query, (self.gestureName_field.text(), self.selected_gesture_name, model_id) )
            
            #update table with new value
            self.updateTable("")
            QMessageBox.information(self, "Gesture Updated", "Successfully updated the gesture")
        
        self.reset()    

        db_connector.close()

    def deleteGesture(self):
        if self.comboBox.currentText() and self.selected_gesture_name:
            db_connector.connect()
            model_id = self.getModelID(self.comboBox.currentText())
            reply = QMessageBox.question(self, 'Yes/No Dialog', f'Do you want to delete {self.selected_gesture_name} gesture from {self.comboBox.currentText()} model?', QMessageBox.Yes | QMessageBox.No)

            # Process the user's choice
            if reply == QMessageBox.Yes:
                #before deleting from database, extract id from database and delete from csv
                print("selected gesture name", self.selected_gesture_name)
                gesture_id = self.getGestureID(self.selected_gesture_name, model_id)
                keypoints_csv_path = f"model/keypoints/{self.comboBox.currentText()}_keypoints.csv"
                self.updateKeypoints(keypoints_csv_path, gesture_id)

                #deleting from database
                query = "delete from Gesture where gesture_name = ? and model_id = ?"
                db_connector.execute(query, (self.selected_gesture_name, model_id))
                QMessageBox.information(self, "Gesture Deleted", f"{self.selected_gesture_name} gesture deleted successfully")
                self.updateTable("")

                self.reset()
            else:
                print('User clicked No')
            db_connector.close()
        elif not self.selected_gesture_name:
            QMessageBox.warning(self, "No Gesture Selected", "Select a gesture to delete")
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

    def getGestureID(self, gesture_name, model_id):
        try:
            db_connector.connect()
            query = "select gesture_id from Gesture where gesture_name = ? and model_id = ?"
            result = db_connector.execute(query, (gesture_name, model_id))
            return int(result[0][0])
        except:
            pass

    def reset(self):
        #clear the field after updating
        self.gestureName_field.clear()

        #clear the selected Gesture name after updating
        self.selected_gesture_name = ""
        
    def updateKeypoints(self, input_file, id):
        # print("updateKeypoints", id)
        output_file = input_file  # Use the same name for output file
        if os.path.getsize(input_file) != 0: #checks if file size is 0 or not
            with open(input_file, 'r', newline='') as input_csv:
                reader = csv.reader(input_csv)

                # Filter rows based on the condition (first value equals 1)
                filtered_rows = [row for row in reader if row and row[0] != str(id)]

            with open(output_file, 'w', newline='') as output_csv:
                writer = csv.writer(output_csv)

                # Write the filtered rows
                writer.writerows(filtered_rows)

            

    # def add_dummy_data(self):
    #     # Add dummy data to the table
    #     data = [
    #         ["Data 11", "Data 12", "Data 13"],
    #         ["Data 21", "Data 22", "Data 23"],
    #         ["Data 31", "Data 32", "Data 33"]
    #     ]

    #     # Set the number of rows in the table
    #     self.tableWidget.setRowCount(len(data))

    #     # Populate the table with dummy data
    #     for row, row_data in enumerate(data):
    #         for col, col_data in enumerate(row_data):
    #             item = QTableWidgetItem(str(col_data))
    #             self.tableWidget.setItem(row, col, item)

    def make_table_readonly(self):
        # Set the edit triggers to NoEditTriggers
        self.tableWidget.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # Set the selection behavior to select entire rows
        self.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)


# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     window = GestureTab()
#     window.show()
#     sys.exit(app.exec_())
