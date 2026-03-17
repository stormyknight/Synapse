# Synapse
# guiModule
# mainScreen.py
from PyQt5.QtWidgets import QApplication, QWidget, QTextEdit, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtGui import QFont


# Window for notes and homepage
class MainWindow(QWidget): # type: ignore
    def __init__(self)->None:
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

        self.folder_input = QLineEdit()
        self.folder_input.setStyleSheet("border: None")
        folderFont: QFont = QFont("Arial", 40)
        self.folder_input.setFont(folderFont)

        # Creating a vertical box layout to format elements
        windowElementLayout: QVBoxLayout = QVBoxLayout(self)

        windowElementLayout.addWidget(QLabel("Folder Name:"))
        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("Enter folder name...")
        windowElementLayout.addWidget(self.folder_input)

        # Creating exit button to return to main screen
        self.exitButton = QPushButton("← Back to Main")
        self.exitButton.setStyleSheet("border: None; text-align: left;")
        exitFont: QFont = QFont("Arial", 13)
        self.exitButton.setFont(exitFont)
        self.exitButton.clicked.connect(self.goToMainScreen)
        windowElementLayout.addWidget(self.exitButton)

        windowElementLayout.addWidget(self.editableContentText)

        self.setLayout(windowElementLayout)

    def goToMainScreen(self) -> None:
        self.folder_input.clear()
        self.editableContentText.clear()


# creating PyQT5 App, adding window, and showing window
app: QApplication = QApplication([])
window: MainWindow = MainWindow()
window.show()

app.exec()

# to run: python3 -u "/Users/jessekemmer/Downloads/codes/Synapse/src/guiModule/mainScreen.py"
