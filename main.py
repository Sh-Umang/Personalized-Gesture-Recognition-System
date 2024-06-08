# button.py
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import qdarkstyle

from home_tab import HomeTab
from feature_tab import FeatureTab
from profile_tab import ProfileTab
from gesture_tab import GestureTab
from program_tab import ProgramTab
from knn_classifier import kNNClassifier

class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gesture for Automation")
        self.resize(370, 700)
        self.program()

    def program(self):
        layout = QVBoxLayout()

        tab_widget = QTabWidget(self)

        #home tab
        self.home_tab = HomeTab()
        tab_widget.addTab(self.home_tab, "Home")

        #feature tab
        self.feature_tab = FeatureTab()
        tab_widget.addTab(self.feature_tab, "Features")

        #profiles tab
        self.profile_tab = ProfileTab()
        tab_widget.addTab(self.profile_tab, "Profiles")

        self.model_tab = GestureTab()
        tab_widget.addTab(self.model_tab, "Gestures")

        self.program_tab = ProgramTab()
        tab_widget.addTab(self.program_tab, "Programs")

        tab_widget.currentChanged.connect(self.on_tab_changed)
        layout.addWidget(tab_widget)
        self.setLayout(layout)
        self.show()
    
    def on_tab_changed(self):
        self.model_tab.populateComboBox()
        self.profile_tab.populateComboBox(1) #1 means combobox1 which eventually populates combobox2 as well
        self.home_tab.populate_gesture_list("")
        self.home_tab.populate_profile_list()
        self.feature_tab.populate_list()


if __name__ == '__main__':
    app = QApplication([])
    style = '''
            QPushButton {
                background-color: green;
                color: white;
                border: 1px solid #555;
                border-radius: 5px;
                padding: 5px 10px;
                font-family: 'Montserrat';
                font-size: 14px;
                font-weight: bold;  /* Make the button text bold */
            }
            QRadioButton {
                font-weight: bold;
            }
            QLabel, QComboBox {
                font-family: 'Montserrat';
                font-size: 14px;  /* Adjust the font size as needed */
                font-weight: bold;  /* Make the label and combo box text bold */
            }
        '''
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5() + style)

    ################### Other Styles ######################

    # QApplication.setStyle(QStyleFactory.create("Fusion"))
    # QApplication.setStyle(QStyleFactory.create("windowsvista"))
    # QApplication.setStyle(QStyleFactory.create("Windows"))
    
    widget = MyWidget()
    app.exec_()
