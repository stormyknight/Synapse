# Synapse
# guiModule
# mainScreen.py

from __future__ import annotations
from enum import Enum

from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import QRect, QSize, Qt, QPoint, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication,
    QBoxLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTextEdit,
    QVBoxLayout,
    QLineEdit,
    QWidget,
    QStackedLayout,
    QScrollArea,
    QGridLayout,
    QFrame,
    QLayout,
    QMenu,
    QAction,
    QInputDialog
)

from src.logicModule import noteLogic, tagLogic

databaseName = "synapse.db"

def clearLayout( layout: QLayout)->None:
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater() # Deletes the widget
                else:
                    clearLayout(item.layout()) # Recursively clear nested layouts


class Page(Enum):
    HOME = 0
    NOTE = 1

class FlowLayout(QLayout):
    """A ``QLayout`` that aranges its child widgets horizontally and
    vertically.

    If enough horizontal space is available, it looks like an ``HBoxLayout``,
    but if enough space is lacking, it automatically wraps its children into
    multiple rows.

    """
    heightChanged = pyqtSignal(int)

    def __init__(self, parent=None, margin=0, spacing=-1):
        super().__init__(parent)
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)

        self._item_list = []

    def __del__(self):
        while self.count():
            self.takeAt(0)

    def addItem(self, item):  # pylint: disable=invalid-name
        self._item_list.append(item)

    def addSpacing(self, size):  # pylint: disable=invalid-name
        self.addItem(QSpacerItem(size, 0, QSizePolicy.Fixed, QSizePolicy.Minimum))

    def count(self):
        return len(self._item_list)

    def itemAt(self, index):  # pylint: disable=invalid-name
        if 0 <= index < len(self._item_list):
            return self._item_list[index]
        return None

    def takeAt(self, index):  # pylint: disable=invalid-name
        if 0 <= index < len(self._item_list):
            return self._item_list.pop(index)
        return None

    def expandingDirections(self):  # pylint: disable=invalid-name,no-self-use
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self):  # pylint: disable=invalid-name,no-self-use
        return True

    def heightForWidth(self, width):  # pylint: disable=invalid-name
        height = self._do_layout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):  # pylint: disable=invalid-name
        super().setGeometry(rect)
        self._do_layout(rect, False)

    def sizeHint(self):  # pylint: disable=invalid-name
        return self.minimumSize()

    def minimumSize(self):  # pylint: disable=invalid-name
        size = QSize()

        for item in self._item_list:
            minsize = item.minimumSize()
            extent = item.geometry().bottomRight()
            size = size.expandedTo(QSize(minsize.width(), extent.y()))

        margin = self.contentsMargins().left()
        size += QSize(2 * margin, 2 * margin)
        return size

    def _do_layout(self, rect, test_only=False):
        m = self.contentsMargins()
        effective_rect = rect.adjusted(+m.left(), +m.top(), -m.right(), -m.bottom())
        x = effective_rect.x()
        y = effective_rect.y()
        line_height = 0

        for item in self._item_list:
            wid = item.widget()

            space_x = self.spacing()
            space_y = self.spacing()
            if wid is not None:
                space_x += wid.style().layoutSpacing(
                    QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Horizontal)
                space_y += wid.style().layoutSpacing(
                    QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Vertical)

            next_x = x + item.sizeHint().width() + space_x
            if next_x - space_x > effective_rect.right() and line_height > 0:
                x = effective_rect.x()
                y = y + line_height + space_y
                next_x = x + item.sizeHint().width() + space_x
                line_height = 0

            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = next_x
            line_height = max(line_height, item.sizeHint().height())

        new_height = y + line_height - rect.y()
        self.heightChanged.emit(new_height)
        return new_height



class TagWindow(QWidget): # type: ignore
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Add/Remove Tags")
        self.setStyleSheet("background-color: #A5F3FF;")
        self.setFixedSize(600,600)
        self.currentNoteId: int = None

        self.layout:QVBoxLayout = QVBoxLayout()

        self.addTagLayout: QHBoxLayout = QHBoxLayout()

        self.addButton: QPushButton = QPushButton("+")
        self.addButton.setFixedSize(24,24)
        self.addButton.setStyleSheet("" \
        "background-color: black;" \
        "color: #A5F3FF;" \
        "border-radius: 12")
        self.addButton.clicked.connect(self.getTagName)

        self.addTagLabel: QLabel = QLabel('Create Tag')
        addTagLabelFont = QFont("Arial", 18)
        self.addTagLabel.setFont(addTagLabelFont)

        self.currentTagsLabel: QLabel = QLabel('Current Tags')
        self.currentTagsLabel.setFont(addTagLabelFont)

        self.currentTagsBox: FlowLayout = FlowLayout()

        self.availableTagsLabel: QLabel = QLabel('Available Tags')
        self.availableTagsLabel.setFont(addTagLabelFont)

        self.availableTagsBox: FlowLayout = FlowLayout()

        self.addTagLayout.addWidget(self.addButton)
        self.addTagLayout.addWidget(self.addTagLabel)
        self.layout.addLayout(self.addTagLayout)
        self.layout.addWidget(self.currentTagsLabel)
        self.layout.addLayout(self.currentTagsBox)
        self.layout.addWidget(self.availableTagsLabel)
        self.layout.addLayout(self.availableTagsBox)

        self.setLayout(self.layout)

    def getTagName(self):
        name, done = QInputDialog.getText(self, "Tag Name Window", "Input Tag Name")
        if done:
            createTagResponse: dict[str,str] | int = tagLogic.createTagHandler(name, databaseName)
            if type(createTagResponse) is int:
                tagLogic.associateTagWithNoteHandler(createTagResponse, self.currentNoteId, databaseName)
                self.showCurrentTags()

    def showCurrentTags(self):
        clearLayout(self.currentTagsBox)
        tagAssociations: list[tuple] = tagLogic.getTagAssociationsHandler(noteId=self.currentNoteId, databaseName=databaseName)
        associatedTags: list[tuple] = tagLogic.getSelectedTagsHandler([tag[2] for tag in tagAssociations],databaseName=databaseName)
        for tag, assoc in zip(associatedTags, tagAssociations):
            tagBox: QFrame = QFrame()
            tagBox.setStyleSheet(("""
                    QFrame {
                        background-color: #000000;
                        border-radius: 20px;
                    }
                """))
            tagBoxLabel: QLabel = QLabel(tag[1])
            tagBoxLabel.setStyleSheet("color: #A5F3FF")
            tagBoxLayout: QHBoxLayout = QHBoxLayout()
            removeTagButton: QPushButton = QPushButton()
            removeTagButton.setIcon(QIcon("removeIcon.png"))
            removeTagButton.setStyleSheet("color: #A5F3FF;" \
            "background-color: #000000")
            removeTagButton.setFixedSize(24,24)
            removeTagButton.clicked.connect(lambda _, id = assoc[0]: self.removeTag(id))

            tagBoxLayout.addWidget(tagBoxLabel)
            tagBoxLayout.addWidget(removeTagButton)
            tagBox.setLayout(tagBoxLayout)

            self.currentTagsBox.addWidget(tagBox)

    def showAvailableTags(self):
        clearLayout(self.availableTagsBox)
        tagAssociations: list[int] = tagLogic.getTagAssociationsHandler(noteId=self.currentNoteId, databaseName=databaseName)
        availableTags: list[tuple] = [tag for tag in tagLogic.getTagsHandler(databaseName=databaseName) if tag[0] not in [assoc[2] for assoc in tagAssociations]]
        for tag in availableTags:
            tagBox: QFrame = QFrame()
            tagBox.setStyleSheet(("""
                    QFrame {
                        background-color: #000000;
                        border-radius: 20px;
                    }
                """))
            tagBoxLabel: QLabel = QLabel(tag[1])
            tagBoxLabel.setStyleSheet("color: #A5F3FF")
            tagBoxLayout: QHBoxLayout = QHBoxLayout()
            addTagButton: QPushButton = QPushButton("+")
            addTagButton.setStyleSheet("color: #A5F3FF;" \
            "background-color: #000000")
            addTagButton.setFixedSize(24,24)
            addTagButton.clicked.connect(lambda _, tid=tag[0], nid=self.currentNoteId: self.associateTag(tid,nid))

            tagBoxLayout.addWidget(tagBoxLabel)
            tagBoxLayout.addWidget(addTagButton)
            tagBox.setLayout(tagBoxLayout)

            self.availableTagsBox.addWidget(tagBox)

    def removeTag(self, tagAssociationId: int)->None:
        tagLogic.removeTagAssociationHandler(databaseName, tagAssociationId)
        self.showAvailableTags()
        self.showCurrentTags()

    def associateTag(self, tagId: int, noteId: int)->None:
        tagLogic.associateTagWithNoteHandler(tagId, noteId, databaseName)
        self.showAvailableTags()
        self.showCurrentTags()

    def setCurrentNoteId(self, noteId: int):
        self.currentNoteId = noteId
        self.showCurrentTags()
        self.showAvailableTags()



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

        # create window for tags
        self.newTagWindow: TagWindow = TagWindow()

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

    def displayNotesOnHome(self) -> None:
        """Fetches notes and builds custom rounded cards in a grid."""

        # Groups the cards closely together
        clearLayout(self.gridLayout)
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
                card.setFixedSize(350, 350)
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
                addRemoveTag: QAction = QAction("Add/Remove Tag", self)
                addRemoveTag.triggered.connect(lambda _, id=noteId: self.showTagWindow(id))
                noteMenu.addAction(addRemoveTag)
                noteMenu.setLayoutDirection(Qt.RightToLeft)

                # Add overflow menu button
                overflowMenuButton: QPushButton = QPushButton()
                overflowMenuButton.setIcon(QIcon("more-dots-v.png"))
                overflowMenuButton.clicked.connect(lambda _, b=overflowMenuButton, m=noteMenu:  self.showMenu(m, b))
                overflowMenuButton.setFixedSize(24,24)

                # show tags on cards
                tagLayout: QHBoxLayout = QHBoxLayout()
                tags: list[tuple] = self.getTags(noteId)
                widthCounter: int = 0
                for tag in tags:
                    tagBox: QFrame = QFrame()
                    tagBox.setStyleSheet(("""
                            QFrame {
                                background-color: #000000;
                                border-radius: 20px;
                            }
                        """))
                    tagBoxLabel: QLabel = QLabel(tag[1])
                    tagBoxLabel.setStyleSheet("color: #A5F3FF")
                    tagBoxLabel.setFont(QFont("Arial", 11))
                    tagBoxLayout: QHBoxLayout = QHBoxLayout()
                    tagBoxLayout.addWidget(tagBoxLabel)
                    tagBox.setLayout(tagBoxLayout)
                    print(card.width())
                    print(tagBox.width())
                    tagLayout.addWidget(tagBox)

                # Put text in the card, and put the card in the grid
                cardLayout.addWidget(overflowMenuButton, alignment=Qt.AlignRight)
                cardLayout.addWidget(titleLabel)
                cardLayout.addWidget(previewLabel)
                cardLayout.addStretch(1)
                cardLayout.addLayout(tagLayout)
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

    def showTagWindow(self, clickedId:int)->None:
        self.newTagWindow.setCurrentNoteId(clickedId)
        self.newTagWindow.show()

    def getTags(self, noteId: int)->list[tuple]:
        tagAssociations:list[tuple] = tagLogic.getTagAssociationsHandler(noteId, databaseName)
        return tagLogic.getSelectedTagsHandler([assoc[2] for assoc in tagAssociations], databaseName)


def runApp() -> int:
    """Create and run the PyQt application."""
    app: QApplication = QApplication([])
    window: MainWindow = MainWindow()
    window.show()
    return int(app.exec())


if __name__ == "__main__":
    raise SystemExit(runApp())
