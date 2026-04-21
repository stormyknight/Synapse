# Synapse
# guiModule
# mainScreen.py

from __future__ import annotations
from enum import Enum

from PyQt5.QtGui import QFont, QIcon, QPixmap
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
    QFrame,
)

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

        self.setWindowTitle("Synapse")
        self.resize(1400, 1200)
        self.setMinimumSize(500, 400)
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

        # Back button
        self.exitButton = QPushButton("← Back to Main")
        self.exitButton.setStyleSheet("border: None; text-align: left; color: black;")
        exitFont: QFont = QFont("Arial", 13)
        self.exitButton.setFont(exitFont)
        self.exitButton.clicked.connect(self.goToMainScreen)

        # Content editor
        self.editableContentText = QTextEdit()
        self.editableContentText.setStyleSheet("border: None;")
        contentFont: QFont = QFont("Arial", 13)
        self.editableContentText.setFont(contentFont)

        # Placeholder for future folder/category field if needed
        self.folder_input = QLineEdit()
        self.folder_input.setStyleSheet("border: None;")
        folderFont: QFont = QFont("Arial", 40)
        self.folder_input.setFont(folderFont)

        # Save + status row
        self.saveButton = QPushButton("")
        self.saveButton.setIcon(QIcon("saveIcon.png"))
        self.saveButton.setIconSize(QSize(40, 40))
        self.saveButton.setStyleSheet("border: none;")
        self.saveButton.clicked.connect(self.onSaveNoteClicked)

        self.analyzeButton = QPushButton("Analyze Note")
        self.analyzeButton.setStyleSheet("""
            QPushButton {
                background-color: #90E0EF;
                border-radius: 10px;
                padding: 8px 14px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #7AD5E8;
            }
        """)
        self.analyzeButton.clicked.connect(self.onAnalyzeNoteClicked)

        self.statusLabel = QLabel("")
        statusRowLayout = QHBoxLayout()
        statusRowLayout.addWidget(self.exitButton)
        statusRowLayout.addWidget(self.saveButton)
        statusRowLayout.addWidget(self.analyzeButton)
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

        self.scrollArea.setWidget(self.scrollContainer)
        self.homeLayout.addWidget(self.scrollArea)

        self.homePage.setLayout(self.homeLayout)

        # ---------------- STACK ----------------
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

    def resizeEvent(self, event) -> None:  # type: ignore
        """Keep title height adjusted and floating button pinned bottom-right."""
        self.adjustTitleHeight()

        margin = 30
        btn_width = self.newNoteButton.width()
        btn_height = self.newNoteButton.height()

        self.newNoteButton.move(
            self.width() - btn_width - margin,
            self.height() - btn_height - margin
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
        self.stackedLayout.setCurrentIndex(Page.HOME.value)
        
        # NEW: Navigate to settings page
    def goToSettingsPage(self) -> None:
        self.stackedLayout.setCurrentIndex(Page.SETTINGS.value)
        self.newNoteButton.raise_()

    def displayNotesOnHome(self) -> None:
        """Fetch notes and build custom rounded cards in a grid."""
        import sqlite3

        # Clear old cards before rebuilding
        while self.gridLayout.count():
            item = self.gridLayout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        self.gridLayout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        self.gridLayout.setSpacing(30)

        dbConnection: sqlite3.Connection = sqlite3.connect(databaseName)
        cursor: sqlite3.Cursor = dbConnection.cursor()
        cursor.execute("SELECT id, title, content FROM notes ORDER BY id DESC")
        allNotes: list = cursor.fetchall()
        dbConnection.close()

        row = 0
        col = 0
        maxColumns = 5

        for note in allNotes:
            noteId: int = note[0]
            noteTitle: str = note[1]
            noteContent: str = note[2]

            card: QFrame = QFrame()
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
            card.mousePressEvent = lambda event, note_id=noteId: self.openNoteFromCard(note_id)

            cardLayout: QVBoxLayout = QVBoxLayout()
            cardLayout.setContentsMargins(20, 20, 20, 20)
            cardLayout.setAlignment(Qt.AlignTop)

            titleLabel: QLabel = QLabel(noteTitle)
            titleLabel.setFont(QFont("Arial", 18, QFont.Bold))
            titleLabel.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
            titleLabel.setWordWrap(True)
            titleLabel.setStyleSheet("color: black; background-color: transparent;")

            cardLayout.addSpacing(15)

            previewString: str = noteContent[:100] + "..." if len(noteContent) > 100 else noteContent
            previewLabel: QLabel = QLabel(previewString)
            previewLabel.setFont(QFont("Arial", 11))
            previewLabel.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
            previewLabel.setWordWrap(True)
            previewLabel.setStyleSheet("color: #333333; background-color: transparent;")

            cardLayout.addWidget(titleLabel)
            cardLayout.addWidget(previewLabel)
            card.setLayout(cardLayout)

            self.gridLayout.addWidget(card, row, col)

            col += 1
            if col >= maxColumns:
                col = 0
                row += 1

    def openNoteFromCard(self, noteId: int) -> None:
        """Load an existing note into the editor."""
        import sqlite3

        dbConnection: sqlite3.Connection = sqlite3.connect(databaseName)
        cursor: sqlite3.Cursor = dbConnection.cursor()

        cursor.execute("SELECT title, content FROM notes WHERE id = ?", (noteId,))
        result = cursor.fetchone()
        dbConnection.close()

        if result:
            noteTitle: str = result[0]
            noteContent: str = result[1]

            self.currentNoteId = noteId
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
            self.displayNotesOnHome()
    
    def onAnalyzeNoteClicked(self) -> None:
        """Analyze the currently open note and store the results."""
        if self.currentNoteId is None:
            QMessageBox.warning(
                self,
                "Analyze Note",
                "Please save the note before analyzing it."
            )
            self.statusLabel.setText("Analyze failed")
            return

        content: str = self.editableContentText.toPlainText().strip()
        if not content:
            QMessageBox.warning(
                self,
                "Analyze Note",
                "Note content is empty."
            )
            self.statusLabel.setText("Analyze failed")
            return

        result = noteLogic.analyzeAndStoreNote(
            self.currentNoteId,
            content,
            databaseName
        )

        if isinstance(result, dict):
            summary = result.get("summary", "")
            mood = result.get("mood", "")
            tags = result.get("tags", [])

            self.statusLabel.setText("Analysis saved")

            QMessageBox.information(
                self,
                "Note Analysis",
                f"Summary: {summary}\n\nMood: {mood}\n\nTags: {', '.join(tags) if isinstance(tags, list) else ''}"
            )
        else:
            self.statusLabel.setText("Analyze failed")


def runApp() -> int:
    """Create and run the PyQt application."""
    app: QApplication = QApplication([])
    window: MainWindow = MainWindow()
    window.show()
    return int(app.exec())


if __name__ == "__main__":
    raise SystemExit(runApp())