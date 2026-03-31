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
    QStackedLayout,
    QScrollArea,  
    QGridLayout,  
    QFrame        
)


from src.logicModule import noteLogic


databaseName = "synapse.db"


class Page(Enum):
    HOME = 0
    NOTE = 1


# Window for notes and homepage
class MainWindow(QWidget): # type: ignore
    def __init__(self) -> None:
        super().__init__()
        # tracker varibles
        self.mainPageColumnMax:int = 3
        self.currentNoteId: int = -1

        # Setting main window size and background color
        self.setWindowTitle("Synapse")
        self.resize(1200, 1000)
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
        self.exitButton.setStyleSheet("border: None; text-align: left;")
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
        self.homeLayout:QVBoxLayout = QVBoxLayout()

        # Create Scroll Area
        self.scrollArea:QScrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setStyleSheet("border: none; background-color: transparent;")

        # Create Grid Container
        self.scrollContainer:QWidget = QWidget()
        self.scrollContainer.setStyleSheet("background-color: transparent;")
        
        # Create the Grid Layout
        self.gridLayout:QGridLayout = QGridLayout()
        self.scrollContainer.setLayout(self.gridLayout)
        
        # Put the container inside the scroll area
        self.scrollArea.setWidget(self.scrollContainer)

        # Add the scroll area to the home page
        self.homeLayout.addWidget(self.scrollArea)
        
        self.homePage.setLayout(self.homeLayout)

        # adding pages to stacked layout
        self.stackedLayout.addWidget(self.homePage)
        self.stackedLayout.addWidget(self.notePage)

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

    def adjustMainPageColumnMax(self)->None:
        oldMax: int = self.mainPageColumnMax
        self.mainPageColumnMax = int(self.width()/390)
        print(self.mainPageColumnMax)
        if oldMax != self.mainPageColumnMax:
            self.displayNotesOnHome()

    def resizeEvent(self, event)->None: # type: ignore
        # This method is called whenever the window is resized
        self.adjustTitleHeight()
        self.adjustMainPageColumnMax()
        # Call the base class implementation
        QWidget.resizeEvent(self, event)
        
        
    def goToMainScreen(self) -> None:
        # self.folder_input.clear()
        # self.editableContentText.clear()
        # Refresh the list in case we saved a new note
        self.displayNotesOnHome()
        self.stackedLayout.setCurrentIndex(Page.HOME.value)

    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater() # Deletes the widget
                else:
                    self.clearLayout(item.layout()) # Recursively clear nested layouts


    def displayNotesOnHome(self) -> None:
        """Fetches notes and builds custom rounded cards in a grid."""
        import sqlite3

        # Groups the cards closely together
        self.clearLayout(self.gridLayout)
        self.gridLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.gridLayout.setSpacing(30) # Pixel gap

        # Gets the notes from the database
        dbConnection:sqlite3.Connection = sqlite3.connect(databaseName)
        cursor:sqlite3.Cursor = dbConnection.cursor()
        cursor.execute("SELECT title, content, id FROM notes")
        allNotes:list = cursor.fetchall()

        # Grid positioning coordinates
        row = 0
        col = 0

        # Builds a card for each note
        for note in allNotes:
            noteTitle:str = note[0]
            noteContent:str = note[1]
            noteID:int = note[2]
            # print("title: ", noteTitle, " content: ", noteContent, "id: ", id)
            # Makes the card shape
            card:QFrame = QFrame()
            card.setFixedSize(350, 300) 
            card.setStyleSheet("""
                QFrame {
                    background-color: #90E0EF;
                    border-radius: 20px;
                }
                QFrame:hover {
                    background-color: #7AD5E8; 
                }
            """)
            
            # Make the card clickable
            card.mousePressEvent = lambda event, title=noteTitle: self.openNoteFromCard(noteID)
            print(noteID)
            
            # Setup the text inside the card
            cardLayout:QVBoxLayout = QVBoxLayout()
            cardLayout.setContentsMargins(20, 20, 20, 20)
            cardLayout.setAlignment(Qt.AlignTop) # Text alignment
            
            # Add the Bold Title
            titleLabel:QLabel = QLabel(noteTitle)
            titleLabel.setFont(QFont("Arial", 18, QFont.Bold))
            titleLabel.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
            titleLabel.setWordWrap(True) # long titles can wrap to a new line
            titleLabel.setStyleSheet("color: black; background-color: transparent;")
            
            # Add a little space between the title and the preview
            cardLayout.addSpacing(15)
            
            # Add the Preview Text 
            previewString:str = noteContent[:100] + "..." if len(noteContent) > 100 else noteContent
            previewLabel:QLabel = QLabel(previewString)
            previewLabel.setFont(QFont("Arial", 11))
            previewLabel.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
            previewLabel.setWordWrap(True)
            previewLabel.setStyleSheet("color: #333333; background-color: transparent;")
            
            # Put text in the card, and put the card in the grid
            cardLayout.addWidget(titleLabel)
            cardLayout.addWidget(previewLabel)
            card.setLayout(cardLayout)
            
            self.gridLayout.addWidget(card, row, col)
            
            # Move to the next column
            col += 1
            if col >= self.mainPageColumnMax:
                col = 0
                row += 1

        dbConnection.close()

    def openNoteFromCard(self, clickedId: int) -> None:
        """Gets the clicked note's content and switches to the editing page."""
        import sqlite3
        
        dbConnection:sqlite3.Connection = sqlite3.connect(databaseName)
        cursor:sqlite3.Cursor = dbConnection.cursor()
        print(clickedId)
        cursor.execute("SELECT content, title FROM notes WHERE id = ?", (clickedId,))
        result:tuple = cursor.fetchone()
        dbConnection.close()

        if result:
            noteContent:str = result[0]
            noteTitle:str = result[1]
            
            self.titleInput.setText(noteTitle)
            self.editableContentText.setText(noteContent)
            self.stackedLayout.setCurrentIndex(Page.NOTE.value)
            self.currentNoteId = clickedId

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


# 