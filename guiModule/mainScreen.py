# Synapse
# guiModule
# notesScreen.py
from PyQt5.QtWidgets import QApplication, QWidget, QTextEdit, QVBoxLayout
from PyQt5.QtGui import QFont


# Window for notes and homepage
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Setting main window size and background color
        self.setWindowTitle("Synapse")
        self.resize(1400, 1200)
        self.setStyleSheet("background-color: #A5F3FF;")

        # Creating the content textedit and setting font and removing border
        self.editableContentText = QTextEdit()
        self.editableContentText.setStyleSheet("border: None")
        contentFont: QFont = QFont("Arial", 13)
        self.editableContentText.setFont(contentFont)

        # Creating a vertical box layout to format elements
        windowElementLayout: QVBoxLayout = QVBoxLayout(self)

        # Adding the textedit into the layout
        windowElementLayout.addWidget(self.editableContentText)

        self.setLayout(windowElementLayout)


# creating PyQT5 App, adding window, and showing window
app: QApplication = QApplication([])
window: MainWindow = MainWindow()
window.show()

app.exec()
