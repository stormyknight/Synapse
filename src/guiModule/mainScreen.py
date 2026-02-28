# Synapse
# guiModule
# mainScreen.py

from __future__ import annotations

import os
import sqlite3
from datetime import datetime
import math

from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,)
from PyQt5.QtCore import Qt

databaseName = "synapse.db"


def connectDb(dbPath: str) -> sqlite3.Connection:
    """Connect to SQLite and enforce foreign keys."""
    conn = sqlite3.connect(dbPath)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def addNote(cursor: sqlite3.Cursor, title: str, content: str, source: str) -> int:
    """Insert a note into the notes table and return new note id."""
    cursor.execute(
        """
        INSERT INTO notes (title, content, source)
        VALUES (?, ?, ?)
        """,
        (title, content, source),
    )
    return cursor.lastrowid if cursor.lastrowid is not None else int(math.nan)


# Window for notes and homepage
class MainWindow(QWidget): # type: ignore
    def __init__(self) -> None:
        super().__init__()

        # Setting main window size and background color
        self.setWindowTitle("Synapse")
        self.resize(1400, 1200)
        self.setMinimumSize(500,400)
        self.setStyleSheet("background-color: #A5F3FF;")

        # Title row and setting title font
        self.titleInput: QTextEdit = QTextEdit()
        titleFont: QFont = QFont("Arial", 26)
        self.titleInput.setStyleSheet("border: None;")

        # Disable Scroll bars
        self.titleInput.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.titleInput.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Start as one line tall
        self.titleInput.setFixedHeight(75)
        # Expand when text changes
        self.titleInput.textChanged.connect(self.adjustTitleHeight)
        self.titleInput.setFont(titleFont)

        # Creating the content textedit and setting font and removing border
        self.editableContentText = QTextEdit()
        self.editableContentText.setStyleSheet("border: None;")
        contentFont: QFont = QFont("Arial", 13)
        self.editableContentText.setFont(contentFont)

        # Save + status row
        self.saveButton = QPushButton("")
        self.saveButton.setIcon(QIcon("saveIcon.png"))
        self.saveButton.setIconSize(QSize(40,40))
        self.saveButton.setStyleSheet("border: none;")
        self.saveButton.clicked.connect(self.onSaveClicked)

        self.statusLabel = QLabel("")
        statusRowLayout = QHBoxLayout()
        statusRowLayout.addWidget(self.saveButton)
        statusRowLayout.addStretch(1)
        statusRowLayout.addWidget(self.statusLabel)

        # Creating a vertical box layout to format elements
        windowElementLayout: QVBoxLayout = QVBoxLayout(self)

        windowElementLayout.addLayout(statusRowLayout)
        windowElementLayout.addWidget(self.titleInput)
        windowElementLayout.addWidget(self.editableContentText)

        self.setLayout(windowElementLayout)

    def adjustTitleHeight(self)->None:
        if self.titleInput.document() is not None:
            docHeight: float = self.titleInput.document().size().height()
            newHeight: int = int(docHeight + 10)  # padding
            self.titleInput.setFixedHeight(newHeight)

    def getDbPath(self) -> str:
        """Resolve DB path relative to current working directory."""
        return os.path.join(os.getcwd(), databaseName)

    def makeDefaultTitle(self) -> str:
        """Create a default title when none is given."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        return f"Untitled Note ({timestamp})"

    def onSaveClicked(self) -> None:
        """Save current note contents into synapse.db."""
        title = self.titleInput.toPlainText().strip()
        if not title:
            title = self.makeDefaultTitle()

        content = self.editableContentText.toPlainText().strip()
        if not content:
            QMessageBox.warning(self, "Cannot Save", "Note content is required.")
            return

        dbPath = self.getDbPath()
        if not os.path.exists(dbPath):
            QMessageBox.critical(
                self,
                "Database Missing",
                f"Database '{databaseName}' not found.\nRun setup_database.py first.",
            )
            self.statusLabel.setText("Save failed")
            return

        try:
            conn = connectDb(dbPath)
            try:
                cursor = conn.cursor()
                noteId = addNote(cursor, title, content, "gui")
                conn.commit()
            finally:
                conn.close()

            self.statusLabel.setText(f"Saved (id={noteId})")
        except sqlite3.Error as exc:
            QMessageBox.critical(self, "Database Error", f"SQLite error:\n{exc}")
            self.statusLabel.setText("Save failed")


def runApp() -> int:
    """Create and run the PyQt application."""
    app: QApplication = QApplication([])
    window: MainWindow = MainWindow()
    window.show()
    return int(app.exec())


if __name__ == "__main__":
    raise SystemExit(runApp())
