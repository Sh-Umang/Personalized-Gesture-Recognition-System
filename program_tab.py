import sys
from PyQt5.QtWidgets import *
import sqlite3

from db_sqlite3 import db_connector
class ProgramTab(QMainWindow):
    def __init__(self):
        super().__init__()
        self.selected_cell = ""

        self.setWindowTitle("File Browser and Database")

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.add_button = QPushButton("Add Programs", self)
        self.add_button.clicked.connect(self.browse_files)
        self.layout.addWidget(self.add_button)

        self.delete_button = QPushButton('Delete Program')
        self.delete_button.setStyleSheet(f"background-color: 'darkRed';"
                                  "color: white")
        self.delete_button.clicked.connect(self.deleteProgram)
        self.layout.addWidget(self.delete_button)

        self.tableWidget = QTableWidget(self)
        self.tableWidget.setColumnCount(1)
        self.tableWidget.setHorizontalHeaderLabels(["Program Name"])
        self.tableWidget.setColumnWidth(0, 280)
        self.layout.addWidget(self.tableWidget)
        self.updateTable()
        self.tableWidget.cellClicked.connect(self.updateGestureNameField)


    def browse_files(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        files = file_dialog.getOpenFileNames()[0]
        self.selected_files = files
        print("Selected Files:", files)
        self.add_to_database()

    def add_to_database(self):
        if self.selected_files:
            db_connector.connect()
            query = "Insert into AppPath (path, prog_name) values (?, ?)"
            for file_path in self.selected_files:
                program_name = file_path.split("/")[-1].split(".")[0]
                db_connector.connect()
                parameters = (file_path, program_name)
                searchResult = db_connector.execute("select * from AppPath where path = ? or prog_name = ?", parameters)
                if searchResult:
                    QMessageBox.warning(self, "Program Already Exists", "Program Already Exists on list")
                    db_connector.close()
                    print("Files not added to the database.")
                else:
                    db_connector.execute(query, (file_path, program_name))
                    db_connector.close()
                    QMessageBox.information(self, "Program added", "Program added to list")
                    print("Files added to the database.")
                    self.updateTable()
            self.selected_files=[]
        else:
            print("No files selected.")

    def updateTable(self):
        # self.reset()
        db_connector.connect()
        query = "select prog_name from AppPath"
        result = db_connector.execute(query)
        db_connector.close()

        self.tableWidget.clearContents()
        self.tableWidget.setRowCount(0)
        
        if len(result):
            self.tableWidget.setRowCount(len(result))


            for row, row_item in enumerate(result):
                col1_item = QTableWidgetItem(str(row_item[0]))
                self.tableWidget.setItem(row, 0, col1_item)
    
    def deleteProgram(self):
        if self.selected_cell:
            db_connector.connect()
            reply = QMessageBox.question(self, 'Yes/No Dialog', f'Do you want to remove {self.selected_cell} program from the list?', QMessageBox.Yes | QMessageBox.No)

            # Process the user's choice
            if reply == QMessageBox.Yes:
                #deleting from database
                query = "delete from AppPath where prog_name = ?"
                db_connector.execute(query, (self.selected_cell,))
                QMessageBox.information(self, "Program Removed", f"{self.selected_cell} removed successfully from the list")
                self.updateTable()

                self.reset()
            else:
                print('User clicked No')
            db_connector.close()
        elif not self.selected_cell:
            QMessageBox.warning(self, "No Program Selected", "Select a program to remove from the list")
        else:
            pass
    
    def updateGestureNameField(self):
        self.selected_cell = self.tableWidget.selectedItems()[0].text()

    def reset(self):
        #clear the selected Gesture name after updating
        self.selected_cell = ""
        

# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     main_window = ProgramTab()
#     main_window.show()
#     sys.exit(app.exec_())
