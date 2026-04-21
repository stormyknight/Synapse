# Synapse
# guiModule
# mainScreen.py

from __future__ import annotations
from enum import Enum

from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QLineEdit,
    QWidget,
    QStackedLayout)


from src.logicModule import noteLogic


databaseName = "synapse.db"

class Page(Enum):
    HOME = 0
    NOTE = 1 
    SETTINGS = 2

# Window for notes and homepage
class MainWindow(QWidget): # type: ignore
    def __init__(self) -> None:
        super().__init__()

        # Setting main window size and background color
        self.setWindowTitle("Synapse")
        self.resize(1400, 1200)
        self.setMinimumSize(500,400)
        self.setStyleSheet("background-color: #A5F3FF;")

        # Create Stacked Widget for holding multple pages
        self.stackedLayout: QStackedLayout = QStackedLayout()

        # Create note page
        self.notePage:QWidget = QWidget()

        # Title row and setting title font for note page
        self.titleInput: QTextEdit = QTextEdit()
        titleFont: QFont = QFont("Arial", 26)
        self.titleInput.setStyleSheet("border: None;")

        # Disable Scroll bars for note page title
        self.titleInput.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.titleInput.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Start as one line tall
        self.titleInput.setFixedHeight(75)
        # Expand when text changes
        self.titleInput.textChanged.connect(self.adjustTitleHeight)
        self.titleInput.setFont(titleFont)
        
            # Creating exit button to return to main screen
        self.exitButton = QPushButton("← Back to Main")
        self.exitButton.setStyleSheet("border: None; text-align: left; color: black;")
        exitFont: QFont = QFont("Arial", 13)
        self.exitButton.setFont(exitFont)
        self.exitButton.clicked.connect(self.goToMainScreen)


        # Creating the content textedit and setting font and removing border for note page
        self.editableContentText = QTextEdit()
        self.editableContentText.setStyleSheet("border: None;")
        contentFont: QFont = QFont("Arial", 13)
        self.editableContentText.setFont(contentFont)

        self.folder_input = QLineEdit()
        self.folder_input.setStyleSheet("border: None")
        folderFont: QFont = QFont("Arial", 40)
        self.folder_input.setFont(folderFont)

        # Save + status row for note page
        self.saveButton = QPushButton("")
        self.saveButton.setIcon(QIcon("saveIcon.png"))
        self.saveButton.setIconSize(QSize(40,40))
        self.saveButton.setStyleSheet("border: none;")
        self.saveButton.clicked.connect(self.onSaveNoteClicked)

        self.statusLabel = QLabel("")
        statusRowLayout = QHBoxLayout()
        statusRowLayout.addWidget(self.saveButton)
        statusRowLayout.addStretch(1)
        statusRowLayout.addWidget(self.statusLabel)

        # Creating a vertical box layout to format note elements for note page
        noteWindowElementLayout: QVBoxLayout = QVBoxLayout()
        noteWindowElementLayout.addLayout(statusRowLayout)
        noteWindowElementLayout.addWidget(self.titleInput)
        noteWindowElementLayout.addWidget(self.editableContentText)
        noteWindowElementLayout.addWidget(self.exitButton)

        self.notePage.setLayout(noteWindowElementLayout)

        # Create Home Page
        self.homePage:QWidget = QWidget()
        
        
        # NEW: Add settings button to home page
        self.settingsButton = QPushButton("⚙Settings")
        self.settingsButton.setStyleSheet("border: None; text-align: right; color: black;")
        settingsButtonFont: QFont = QFont("Arial", 13)
        self.settingsButton.setFont(settingsButtonFont)
        self.settingsButton.clicked.connect(self.goToSettingsPage)

        homePageLayout: QVBoxLayout = QVBoxLayout()
        homeTopBar: QHBoxLayout = QHBoxLayout()
        homeTopBar.addStretch(1)
        homeTopBar.addWidget(self.settingsButton)
        homePageLayout.addLayout(homeTopBar)
        homePageLayout.addStretch(1)
        self.homePage.setLayout(homePageLayout)



        # adding pages to stacked layout
        self.stackedLayout.addWidget(self.homePage)
        self.stackedLayout.addWidget(self.notePage)

        # NEW: Create Settings Page
        self.settingsPage: QWidget = QWidget()

        # Settings page back button
        self.settingsBackButton = QPushButton("← Back to Main")
        self.settingsBackButton.setStyleSheet("border: None; text-align: left; color: black;")        
        settingsBackFont: QFont = QFont("Arial", 13)
        self.settingsBackButton.setFont(settingsBackFont)
        self.settingsBackButton.clicked.connect(self.goToMainScreen)

        # Settings page title label
        self.settingsTitleLabel = QLabel("Settings")
        settingsTitleFont: QFont = QFont("Arial", 26)
        self.settingsTitleLabel.setFont(settingsTitleFont)
        self.settingsTitleLabel.setStyleSheet("border: None;")

        # Settings page layout (empty — no settings added yet)
        settingsPageLayout: QVBoxLayout = QVBoxLayout()
        settingsPageLayout.addWidget(self.settingsBackButton)
        settingsPageLayout.addWidget(self.settingsTitleLabel)
        settingsPageLayout.addStretch(1)

        self.settingsPage.setLayout(settingsPageLayout)

        # Add settings page to stacked layout
        self.stackedLayout.addWidget(self.settingsPage)

        
        # adding stacked layout to mainScreen
        self.setLayout(self.stackedLayout)

        # Setting to note page. For now manually change page Index
        self.stackedLayout.setCurrentIndex(Page.NOTE.value)

    # Adjusts height of title to so title will wrap as size changes
    def adjustTitleHeight(self)->None:
        if self.titleInput.document() is not None:
            docHeight: float = self.titleInput.document().size().height()
            newHeight: int = int(docHeight + 10)  # padding
            self.titleInput.setFixedHeight(newHeight)

    def resizeEvent(self, event)->None: # type: ignore
        # This method is called whenever the window is resized
        self.adjustTitleHeight()
        # Call the base class implementation
        QWidget.resizeEvent(self, event)
        
        
    def goToMainScreen(self) -> None:
        # self.folder_input.clear()
        # self.editableContentText.clear()
        
        self.stackedLayout.setCurrentIndex(Page.HOME.value)
        
        # NEW: Navigate to settings page
    def goToSettingsPage(self) -> None:
        self.stackedLayout.setCurrentIndex(Page.SETTINGS.value)


    # This method calls the logic for saving on note and updates the GUI accordingly
    def onSaveNoteClicked(self) -> None:
        saveResult: dict[str, str] | str =noteLogic.onNoteSaveClicked(self.titleInput.toPlainText().strip(), self.editableContentText.toPlainText().strip(), databaseName)
        if type(saveResult) is not str and type(saveResult) is dict: # pylint: disable=unidiomatic-typecheck
            QMessageBox.critical(
                self,
                saveResult["title"],
                saveResult["msg"],
            )
            self.statusLabel.setText("Save failed")
        else:
            self.statusLabel.setText(saveResult)


def runApp() -> int:
    """Create and run the PyQt application."""
    app: QApplication = QApplication([])
    window: MainWindow = MainWindow()
    window.show()
    return int(app.exec())


if __name__ == "__main__":
    raise SystemExit(runApp())


# python3 -m src.guiModule.mainScreen 2>&1