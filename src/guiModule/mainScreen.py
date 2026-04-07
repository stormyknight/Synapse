# Synapse
# guiModule
# mainScreen.py

from __future__ import annotations
from enum import Enum

from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import QSize, Qt, QPoint
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
    QFrame,
    QLayout,
    QMenu
)

from src.logicModule import noteLogic

databaseName = "synapse.db"


class Page(Enum):
    HOME = 0
    NOTE = 1


class MainWindow(QWidget):  # type: ignore
    def __init__(self) -> None:
        super().__init__()
        # tracker varibles
        self.mainPageColumnMax:int = 3

        self.setWindowTitle("Synapse")
        self.resize(1200, 1000)
        self.setMinimumSize(500,400)
        self.setStyleSheet("background-color: #A5F3FF;")

        # Track whether user is editing an existing note or creating a new one
        self.currentNoteId: int | None = None

        # Create Stacked Widget for holding multiple pages
        self.stackedLayout: QStackedLayout = QStackedLayout()

        # ---------------- NOTE PAGE ----------------
        self.notePage: QWidget = QWidget()

        # Title input
        self.titleInput: QTextEdit = QTextEdit()
        titleFont: QFont = QFont("Arial", 26)
        self.titleInput.setStyleSheet("border: None;")
        self.titleInput.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.titleInput.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.titleInput.setFixedHeight(75)
        self.titleInput.textChanged.connect(self.adjustTitleHeight)
        self.titleInput.setFont(titleFont)

            # Creating exit button to return to main screen
        self.exitButton = QPushButton()
        self.exitButton.setStyleSheet("border: None; text-align: left;")
        self.exitButton.setIcon(QIcon("backIcon.png"))
        self.exitButton.clicked.connect(self.goToMainScreen)

        # Creating the content textedit and setting font and removing border for note page
        self.editableContentText = QTextEdit()
        self.editableContentText.setStyleSheet("border: None;")
        contentFont: QFont = QFont("Arial", 13)
        self.editableContentText.setFont(contentFont)

        self.folderInput = QLineEdit()
        self.folderInput.setStyleSheet("border: None")
        folderFont: QFont = QFont("Arial", 40)
        self.folderInput.setFont(folderFont)

        # Save + status row
        self.saveButton = QPushButton("")
        self.saveButton.setIcon(QIcon("saveIcon.png"))
        self.saveButton.setIconSize(QSize(40, 40))
        self.saveButton.setStyleSheet("border: none;")
        self.saveButton.clicked.connect(self.onSaveNoteClicked)

        self.statusLabel = QLabel("")
        statusRowLayout = QHBoxLayout()
        statusRowLayout.addWidget(self.exitButton)
        statusRowLayout.addWidget(self.saveButton)
        statusRowLayout.addStretch(1)
        statusRowLayout.addWidget(self.statusLabel)

        noteWindowElementLayout: QVBoxLayout = QVBoxLayout()
        noteWindowElementLayout.addLayout(statusRowLayout)
        noteWindowElementLayout.addWidget(self.titleInput)
        noteWindowElementLayout.addWidget(self.editableContentText)

        self.notePage.setLayout(noteWindowElementLayout)

        # ---------------- HOME PAGE ----------------
        self.homePage: QWidget = QWidget()
        self.homeLayout: QVBoxLayout = QVBoxLayout()

        # Logo
        self.logoLabel = QLabel()
        logoPixmap = QPixmap("logo_160x160.png")
        self.logoLabel.setPixmap(logoPixmap)
        self.logoLabel.setAlignment(Qt.AlignCenter)

        # Title
        self.homeTitleLabel = QLabel("Synapse")
        homeTitleFont = QFont("Arial", 36, QFont.Bold)
        self.homeTitleLabel.setFont(homeTitleFont)
        self.homeTitleLabel.setAlignment(Qt.AlignCenter)

        self.homeLayout.addWidget(self.logoLabel)
        self.homeLayout.addWidget(self.homeTitleLabel)

        # Scroll Area
        self.scrollArea: QScrollArea = QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setStyleSheet("border: none; background-color: transparent;")

        # Grid container
        self.scrollContainer: QWidget = QWidget()
        self.scrollContainer.setStyleSheet("background-color: transparent;")

        self.gridLayout: QGridLayout = QGridLayout()
        self.scrollContainer.setLayout(self.gridLayout)

        # Put the container inside the scroll area
        self.scrollArea.setWidget(self.scrollContainer)
        self.homeLayout.addWidget(self.scrollArea)

        self.homePage.setLayout(self.homeLayout)

        # ---------------- STACK ----------------
        self.stackedLayout.addWidget(self.homePage)
        self.stackedLayout.addWidget(self.notePage)
        self.setLayout(self.stackedLayout)

        # ---------------- FLOATING NEW NOTE BUTTON ----------------
        self.newNoteButton = QPushButton(self)
        self.newNoteButton.setIcon(QIcon("createNewNoteButton.png"))
        self.newNoteButton.setIconSize(QSize(120, 120))
        self.newNoteButton.setFixedSize(140, 140)
        self.newNoteButton.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.05);
                border-radius: 70px;
            }
        """)
        self.newNoteButton.clicked.connect(self.createNewNote)
        self.newNoteButton.raise_()

        self.displayNotesOnHome()
        self.stackedLayout.setCurrentIndex(Page.HOME.value)

    def adjustTitleHeight(self) -> None:
        """Adjust title field height so wrapped text expands the box."""
        if self.titleInput.document() is not None:
            docHeight: float = self.titleInput.document().size().height()
            newHeight: int = int(docHeight + 10)
            self.titleInput.setFixedHeight(newHeight)

    def adjustMainPageColumnMax(self)->None:
        oldMax: int = self.mainPageColumnMax
        self.mainPageColumnMax = int(self.width()/390)
        if oldMax != self.mainPageColumnMax:
            self.displayNotesOnHome()

    def resizeEvent(self, event)->None: # type: ignore
        # This method is called whenever the window is resized
        self.adjustTitleHeight()
        self.adjustMainPageColumnMax()

        margin = 30
        btnWidth = self.newNoteButton.width()
        btnHeight = self.newNoteButton.height()

        self.newNoteButton.move(
            self.width() - btnWidth - margin,
            self.height() - btnHeight - margin
        )

        QWidget.resizeEvent(self, event)

    def createNewNote(self) -> None:
        """Open a blank note editor."""
        self.currentNoteId = None
        self.titleInput.clear()
        self.editableContentText.clear()
        self.statusLabel.setText("")
        self.stackedLayout.setCurrentIndex(Page.NOTE.value)

    def goToMainScreen(self) -> None:
        """Return to home page and refresh note cards."""
        self.displayNotesOnHome()
        self.currentNoteId = None
        self.stackedLayout.setCurrentIndex(Page.HOME.value)
        self.newNoteButton.raise_()

    def clearLayout(self, layout: QLayout)->None:
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

        # Groups the cards closely together
        self.clearLayout(self.gridLayout)
        self.gridLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.gridLayout.setSpacing(30) # Pixel gap

        allNotes:dict[str, str]|list = noteLogic.getNotesHandler(databaseName) # type: ignore[type-arg]

        if type(allNotes) is list: # pylint: disable=unidiomatic-typecheck
            # Grid positioning coordinates
            row = 0
            col = 0

            # Builds a card for each note
            for note in allNotes:
                noteTitle:str = note[1]
                noteContent:str = note[2]
                noteId: int = note[0]
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
                card.mousePressEvent = lambda event, id=noteId: self.openNoteFromCard(id)

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

                # Add overflow menu
                noteMenu: QMenu = QMenu(self)
                noteMenu.addAction("Add/Remove Tags")
                noteMenu.setLayoutDirection(Qt.RightToLeft)

                # Add overflow menu button
                overflowMenuButton: QPushButton = QPushButton()
                overflowMenuButton.setIcon(QIcon("more-dots-v.png"))
                overflowMenuButton.clicked.connect(lambda _, b=overflowMenuButton, m=noteMenu:  self.showMenu(m, b))
                overflowMenuButton.setFixedSize(24,24)

                # Put text in the card, and put the card in the grid
                cardLayout.addWidget(overflowMenuButton, alignment=Qt.AlignRight)
                cardLayout.addWidget(titleLabel)
                cardLayout.addWidget(previewLabel)
                card.setLayout(cardLayout)

                self.gridLayout.addWidget(card, row, col)

                # Move to the next column
                col += 1
                if col >= self.mainPageColumnMax:
                    col = 0
                    row += 1

    #for showing and hiding the note menu
    def showMenu(self, menu:QMenu, button: QPushButton)->None:
        pos = button.mapToGlobal(QPoint(button.width(), 0))
        menu.popup(pos)

    def openNoteFromCard(self, clickedId: int) -> None:
        """Gets the clicked note's content and switches to the editing page."""
        result: tuple | dict[str, str] = noteLogic.getNoteHandler(databaseName, clickedId) # type: ignore[type-arg]
        if type(result) == tuple:
            noteTitle:str = result[1]
            noteContent:str = result[2]
            self.currentNoteId = clickedId
            self.statusLabel.setText("")

            self.titleInput.setText(noteTitle)
            self.editableContentText.setText(noteContent)
            self.statusLabel.setText("")
            self.stackedLayout.setCurrentIndex(Page.NOTE.value)

    def onSaveNoteClicked(self) -> None:
        """Save a new note or update the currently open one."""
        saveResult: dict[str, str] | str = noteLogic.onNoteSaveClicked(
            self.titleInput.toPlainText().strip(),
            self.editableContentText.toPlainText().strip(),
            databaseName,
            self.currentNoteId
        )

        if type(saveResult) is not str and type(saveResult) is dict:  # pylint: disable=unidiomatic-typecheck
            QMessageBox.critical(
                self,
                saveResult["title"],
                saveResult["msg"],
            )
            self.statusLabel.setText("Save failed")
        else:
            self.statusLabel.setText(saveResult)
            self.currentNoteId = int("".join(filter(str.isdigit, saveResult)))
            self.displayNotesOnHome()


def runApp() -> int:
    """Create and run the PyQt application."""
    app: QApplication = QApplication([])
    window: MainWindow = MainWindow()
    window.show()
    return int(app.exec())


if __name__ == "__main__":
    raise SystemExit(runApp())
