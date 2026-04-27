# Synapse
# guiModule
# mainScreen.py

from __future__ import annotations
from enum import Enum
from typing import Any

from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtCore import QRect, QSize, Qt, QPoint, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication,
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


# a custom layout I found online that will expand horizontally and vertically to fit content and container
class FlowLayout(QLayout): # type: ignore
    """A ``QLayout`` that aranges its child widgets horizontally and
    vertically.

    If enough horizontal space is available, it looks like an ``HBoxLayout``,
    but if enough space is lacking, it automatically wraps its children into
    multiple rows.

    """
    heightChanged = pyqtSignal(int)

    def __init__(self, parent=None, margin=0, spacing=-1) -> None: # type: ignore[no-untyped-def]
        super().__init__(parent)
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        self.setSpacing(spacing)

        self._itemList: list = []  # type: ignore[type-arg]

    def __del__(self) -> None:
        while self.count():
            self.takeAt(0)

    def addItem(self, item) -> None:  # type: ignore[no-untyped-def]

        self._itemList.append(item)

    def addSpacing(self, size) -> None:  # type: ignore[no-untyped-def]
        self.addItem(QSpacerItem(size, 0, QSizePolicy.Fixed, QSizePolicy.Minimum))

    def count(self) -> int:
        return len(self._itemList)

    def itemAt(self, index) -> Any:  # type: ignore[no-untyped-def]
        if 0 <= index < len(self._itemList):
            return self._itemList[index]
        return None

    def takeAt(self, index) -> Any | None:  # type: ignore[no-untyped-def]
        if 0 <= index < len(self._itemList):
            return self._itemList.pop(index)
        return None

    def expandingDirections(self) -> Qt.Orientations:
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self) -> bool:
        return True

    def heightForWidth(self, width) -> Any: # type: ignore[no-untyped-def]
        height = self._doLayout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect) -> None:  # type: ignore[no-untyped-def]
        super().setGeometry(rect)
        self._doLayout(rect, False)

    def sizeHint(self) -> QSize:  # pylint: disable=invalid-name
        return self.minimumSize()

    def minimumSize(self) -> QSize:  # pylint: disable=invalid-name
        size = QSize()

        for item in self._itemList:
            minsize = item.minimumSize()
            extent = item.geometry().bottomRight()
            size = size.expandedTo(QSize(minsize.width(), extent.y()))

        margin = self.contentsMargins().left()
        size += QSize(2 * margin, 2 * margin)
        return size

    def _doLayout(self, rect, testOnly=False) -> Any: # type: ignore  [no-untyped-def]
        m = self.contentsMargins()
        effectiveRect = rect.adjusted(+m.left(), +m.top(), -m.right(), -m.bottom())
        x = effectiveRect.x()
        y = effectiveRect.y()
        lineHeight = 0

        for item in self._itemList:
            wid = item.widget()

            spaceX = self.spacing()
            spaceY = self.spacing()
            if wid is not None:
                spaceX += wid.style().layoutSpacing(
                    QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Horizontal)
                spaceY += wid.style().layoutSpacing(
                    QSizePolicy.PushButton, QSizePolicy.PushButton, Qt.Vertical)

            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > effectiveRect.right() and lineHeight > 0:
                x = effectiveRect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())

        newHeight = y + lineHeight - rect.y()
        self.heightChanged.emit(newHeight)
        return newHeight


class TagWindow(QWidget): # type: ignore
    mainWindow: MainWindow

    def __init__(self, mainWindow: MainWindow) -> None: # mainWindow is passed as parameter so mainWindow can update with tag changes.
        super().__init__()
        # Set Window attributes
        self.setWindowTitle("Add/Remove Tags")
        self.setStyleSheet("background-color: #A5F3FF;")
        self.setFixedSize(600,600)

        # ID of not that window was opened for
        self.currentNoteId: int | None = None

        # setting local mainWindow to parameter
        self.mainWindow = mainWindow

        # window layout
        self.layout:QVBoxLayout = QVBoxLayout()

        # Layout for add tag row
        self.addTagLayout: QHBoxLayout = QHBoxLayout()

        # Button for creating a new tag and assigning it to the note
        self.addButton: QPushButton = QPushButton("+")
        self.addButton.setFixedSize(24,24)
        self.addButton.setStyleSheet("" \
        "background-color: black;" \
        "color: #A5F3FF;" \
        "border-radius: 12")
        self.addButton.clicked.connect(self.getTagName)

        # Text for creating a new tag and assigning it to the note
        self.addTagLabel: QLabel = QLabel('Create Tag')
        addTagLabelFont = QFont("Arial", 18)
        self.addTagLabel.setFont(addTagLabelFont)

        # text for tags currently assigned to note
        self.currentTagsLabel: QLabel = QLabel('Current Tags')
        self.currentTagsLabel.setFont(addTagLabelFont)

        self.currentTagsBox: FlowLayout = FlowLayout()
       # Current Tags Scroll Area
        self.currentTagsScrollArea: QScrollArea = QScrollArea()
        self.currentTagsScrollArea.setWidgetResizable(True)
        self.currentTagsScrollArea.setStyleSheet("border: none; background-color: transparent;")
        self.currentTagsScrollArea.setFixedHeight(210)

        # Current Tags Grid container
        self.currentTagsScrollContainer: QWidget = QWidget()
        self.currentTagsScrollContainer.setStyleSheet("background-color: transparent;")

        self.gridLayout: QGridLayout = QGridLayout()
        self.currentTagsScrollContainer.setLayout(self.currentTagsBox)

        # Put the container inside the scroll area for Current Tags
        self.currentTagsScrollArea.setWidget(self.currentTagsScrollContainer)

        # text header for tags not assigned to note
        self.availableTagsLabel: QLabel = QLabel('Available Tags')
        self.availableTagsLabel.setFont(addTagLabelFont)

        self.availableTagsBox: FlowLayout = FlowLayout()

        # Available Tags Scroll Area
        self.availableTagsScrollArea: QScrollArea = QScrollArea()
        self.availableTagsScrollArea.setWidgetResizable(True)
        self.availableTagsScrollArea.setStyleSheet("border: none; background-color: transparent;")

        # Available Tags Grid container
        self.availableTagsScrollContainer: QWidget = QWidget()
        self.availableTagsScrollContainer.setStyleSheet("background-color: transparent;")

        self.availableTagsScrollContainer.setLayout(self.availableTagsBox)

        # Put the container inside the scroll area for Available Tags
        self.availableTagsScrollArea.setWidget(self.availableTagsScrollContainer)

        self.addTagLayout.addWidget(self.addButton)
        self.addTagLayout.addWidget(self.addTagLabel)

        # adding all components to main layout
        self.layout.addLayout(self.addTagLayout)
        self.layout.addWidget(self.currentTagsLabel)
        self.layout.addWidget(self.currentTagsScrollArea)
        self.layout.addWidget(self.availableTagsLabel)
        self.layout.addWidget(self.availableTagsScrollArea)

        self.setLayout(self.layout)

    # Function to get name of tag to be created. When ok is clicked (done is true), the tag is created and associated with the note
    def getTagName(self) -> None:
        # get tag name and confirmation form input box
        name, done = QInputDialog.getText(self, "Tag Name Window", "Input Tag Name")
        if done:
            createTagResponse: dict[str,str] | int = tagLogic.createTagHandler(name, databaseName)
            # check for create tag success
            if type(createTagResponse) is int:
                assoicateTagResponse: int | dict[str,str] = tagLogic.associateTagWithNoteHandler(createTagResponse, self.currentNoteId, databaseName)
                # check associate tag successful
                if type(assoicateTagResponse) is int:
                    self.showCurrentTags()
                    self.mainWindow.displayNotesOnHome()
                else:
                    # error popup for failed tag association
                    QMessageBox.critical(self, assoicateTagResponse["title"], assoicateTagResponse["msg"]) # type: ignore  [index]
            else:
                # error popup for failed tag creation
                QMessageBox.critical(self, createTagResponse["title"], createTagResponse["msg"]) # type: ignore  [index]

    # fetches and displays tags associated with note
    def showCurrentTags(self) -> None:
        clearLayout(self.currentTagsBox)
        tagAssociations: list[int] | dict[str,str] = tagLogic.getTagAssociationsHandler(noteId=self.currentNoteId, databaseName=databaseName)
        # check that fetch tag associations succeeded
        if type(tagAssociations) is dict:
            QMessageBox.critical(self, tagAssociations["title"], tagAssociations["msg"])
            return None

        # "[tag[2] for tag in tagAssociations]" is a list comprehension that return an array of tag IDs
        associatedTags: list[tuple] | dict[str,str] = tagLogic.getSelectedTagsHandler([tag[2] for tag in tagAssociations],databaseName=databaseName) # type: ignore  [type-arg, index]
        # check that fetch selected tags succeeded
        if type(associatedTags) is dict:
            QMessageBox.critical(self, associatedTags["title"], associatedTags["msg"])

        # iterate through both tags and tag-note associations to display tags associated notes
        if type(associatedTags) is not dict and type(tagAssociations) is not dict:
            for tag, assoc in zip(associatedTags, tagAssociations):
                # create box to display individual tags
                tagBox: QFrame = QFrame()
                tagBox.setStyleSheet(("""
                        QFrame {
                            background-color: #000000;
                            border-radius: 20px;
                        }
                    """))

                # text for tag name
                tagBoxLabel: QLabel = QLabel(tag[1])
                tagBoxLabel.setStyleSheet("color: #A5F3FF")

                # layout for tag to be added to tagBox QFrame
                tagBoxLayout: QHBoxLayout = QHBoxLayout()

                # Button for de-associating tag from note
                removeTagButton: QPushButton = QPushButton()
                removeTagButton.setIcon(QIcon("removeIcon.png"))
                removeTagButton.setStyleSheet("color: #A5F3FF;" \
                "background-color: #000000")
                removeTagButton.setFixedSize(24,24)
                removeTagButton.clicked.connect(lambda _, id = assoc[0]: self.removeTag(id)) # type: ignore  [index]

                # adding components to tag box
                tagBoxLayout.addWidget(tagBoxLabel)
                tagBoxLayout.addWidget(removeTagButton)
                tagBox.setLayout(tagBoxLayout)

                # adding add tagBox to current tags space
                self.currentTagsBox.addWidget(tagBox)

    def showAvailableTags(self) -> None:
        clearLayout(self.availableTagsBox)
        tagAssociations: list[int] | dict[str,str] = tagLogic.getTagAssociationsHandler(noteId=self.currentNoteId, databaseName=databaseName)
        # check that fetch tag associations succeeded
        if type(tagAssociations) is dict:
            QMessageBox.critical(self, tagAssociations["title"], tagAssociations["msg"])

        # "[tag for tag in tagLogic.getTagsHandler(databaseName=databaseName) if tag[0] not in [assoc[2] for assoc in tagAssociations]]" is a list comprehension that returns all tags not associated with note
        availableTags: list[tuple]  = [tag for tag in tagLogic.getTagsHandler(databaseName=databaseName) if tag[0] not in [assoc[2] for assoc in tagAssociations]] # type: ignore  [type-arg, index]

        # iterate through unassociated tags to diplay them
        for tag in availableTags:
            # create frame for tags
            tagBox: QFrame = QFrame()
            tagBox.setStyleSheet(("""
                    QFrame {
                        background-color: #000000;
                        border-radius: 20px;
                    }
                """))

            # text for tag name
            tagBoxLabel: QLabel = QLabel(tag[1])
            tagBoxLabel.setStyleSheet("color: #A5F3FF")

            # layout for frame
            tagBoxLayout: QHBoxLayout = QHBoxLayout()

            # button to associate tag with note
            addTagButton: QPushButton = QPushButton("+")
            addTagButton.setStyleSheet("color: #A5F3FF;" \
            "background-color: #000000")
            addTagButton.setFixedSize(24,24)
            addTagButton.clicked.connect(lambda _, tid=tag[0], nid=self.currentNoteId: self.associateTag(tid,nid))

            # adding components to frame
            tagBoxLayout.addWidget(tagBoxLabel)
            tagBoxLayout.addWidget(addTagButton)
            tagBox.setLayout(tagBoxLayout)

            self.availableTagsBox.addWidget(tagBox)

    # de-associates tag from note
    def removeTag(self, tagAssociationId: int)->None:
        removeTagAssociationResponse: None | dict[str, str] = tagLogic.removeTagAssociationHandler(databaseName, tagAssociationId)

        # check removeTagAssociation was successful
        if type(removeTagAssociationResponse) == dict:
            QMessageBox.critical(self, removeTagAssociationResponse["title"], removeTagAssociationResponse["msg"])
        else:
            self.showAvailableTags()
            self.showCurrentTags()
            self.mainWindow.displayNotesOnHome()

    # associates tag with note
    def associateTag(self, tagId: int, noteId: int)->None:
        associateTagResponse: None | dict[str, str] = tagLogic.associateTagWithNoteHandler(tagId, noteId, databaseName)

         # check removeTagAssociation was successful
        if type(associateTagResponse) == dict:
            QMessageBox.critical(self, associateTagResponse["title"], associateTagResponse["msg"])
        else:
            self.showAvailableTags()
            self.showCurrentTags()
            self.mainWindow.displayNotesOnHome()

    def setCurrentNoteId(self, noteId: int) -> None:
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

        # Track the current sorting mode for the home screen grid
        self.currentSortMode: str = "date"

        # Create Stacked Widget for holding multiple pages
        self.stackedLayout: QStackedLayout = QStackedLayout()

        # create window for tags
        self.newTagWindow: TagWindow = TagWindow(self)

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

        # ---------------- TOP NAVIGATION BAR ----------------
        self.topBarLayout = QHBoxLayout()

        # Left: Logo & Title
        logoTitleLayout = QHBoxLayout()
        self.logoLabel = QLabel()
        logoPixmap = QPixmap("logo_160x160.png")
        if not logoPixmap.isNull():
            self.logoLabel.setPixmap(logoPixmap.scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        self.homeTitleLabel = QLabel("Synapse")
        self.homeTitleLabel.setFont(QFont("Arial", 24, QFont.Bold))

        logoTitleLayout.addWidget(self.logoLabel)
        logoTitleLayout.addWidget(self.homeTitleLabel)

        # Right: Sort Controls
        sortLabel = QLabel("Sort by")
        sortLabel.setFont(QFont("Arial", 18, QFont.Bold))

        self.sortContainer = QFrame()
        self.sortContainer.setStyleSheet("background-color: rgba(130, 150, 170, 0.3); border-radius: 20px;")
        sortLayout = QHBoxLayout(self.sortContainer)
        sortLayout.setContentsMargins(20, 10, 20, 10)

        self.btnSortName = QPushButton("Name")
        self.btnSortTag = QPushButton("Tag")
        self.btnSortDate = QPushButton("Date")

        self.updateSortButtonStyles()

        # Wire the buttons to update the state and refresh the screen
        self.btnSortName.clicked.connect(lambda: self.changeSortOrder("name"))
        self.btnSortTag.clicked.connect(lambda: self.changeSortOrder("tag"))
        self.btnSortDate.clicked.connect(lambda: self.changeSortOrder("date"))

        sortLayout.addWidget(self.btnSortName)
        sortLayout.addWidget(self.btnSortTag)
        sortLayout.addWidget(self.btnSortDate)

        # Assemble the Top Bar
        self.topBarLayout.addLayout(logoTitleLayout)
        self.topBarLayout.addStretch()
        self.topBarLayout.addWidget(sortLabel)
        self.topBarLayout.addSpacing(15)
        self.topBarLayout.addWidget(self.sortContainer)
        self.topBarLayout.addSpacing(70)

        self.homeLayout.addLayout(self.topBarLayout)
        self.homeLayout.addSpacing(20)

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

    # pylint: disable=unused-argument
    def closeEvent(self, event) -> None: # type: ignore
        self.newTagWindow.close()

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

    def changeSortOrder(self, mode: str) -> None:
        """Updates the active sort mode and refreshes the grid."""
        self.currentSortMode = mode
        self.updateSortButtonStyles()
        self.displayNotesOnHome()

    def updateSortButtonStyles(self) -> None:
        """Applies a white background to the active sort button."""
        baseStyle = """
            QPushButton { 
                border: none; 
                background: transparent; 
                font-size: 18px; 
                font-weight: bold;
                padding: 5px 15px; 
                color: black; 
                border-radius: 12px;
            } 
            QPushButton:hover { color: #555555; }
        """

        selectedStyle = """
            QPushButton { 
                border: none; 
                background: black; 
                font-size: 18px; 
                font-weight: bold;
                padding: 5px 15px; 
                color: white; 
                border-radius: 12px;
            } 
        """

        # Apply the selected style only to the active mode, and base style to the rest
        self.btnSortName.setStyleSheet(selectedStyle if self.currentSortMode == "name" else baseStyle)
        self.btnSortTag.setStyleSheet(selectedStyle if self.currentSortMode == "tag" else baseStyle)
        self.btnSortDate.setStyleSheet(selectedStyle if self.currentSortMode == "date" else baseStyle)

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

            # sorts notes accordingly
            if self.currentSortMode == "name":
                allNotes.sort(key = lambda note: note[1].lower())
            elif self.currentSortMode == "tag":
                allNotes.sort(key = lambda note: self.sortByTag(self.getTags(note[0]))) # type: ignore[arg-type]
            else:
                allNotes.sort(key=lambda note: note[3])

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
                tags: list[tuple] | dict[str, str] | None = self.getTags(noteId) # type: ignore [type-arg]
                widthCounter: int = 0
                for tag in tags: # type: ignore [union-attr]
                    tagBox: QFrame = QFrame()
                    ellipsisBox: QFrame = QFrame()
                    oldWidthCounter: int = widthCounter
                    if widthCounter != 0:
                        widthCounter += 5
                    widthCounter += len(tag[1])
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

                    # create show more tags box
                    ellipsisBox.setStyleSheet(("""
                            QFrame {
                                background-color: #000000;
                                border-radius: 20px;
                            }
                        """))

                    # "text" for show more tags box
                    ellipsisBoxLabel: QLabel = QLabel("···")
                    ellipsisBoxLabel.setStyleSheet("color: #A5F3FF")
                    ellipsisBoxLabel.setFont(QFont("Arial", 11))

                    # layout for show more tags box
                    ellipsisBoxLayout: QHBoxLayout = QHBoxLayout()
                    ellipsisBoxLayout.addWidget(ellipsisBoxLabel)

                    tagBoxLayout.addWidget(tagBoxLabel, alignment=Qt.AlignCenter)
                    tagBox.setLayout(tagBoxLayout)

                    ellipsisBox.setLayout(ellipsisBoxLayout)

                    # click event to show add/tags window
                    ellipsisBox.mousePressEvent = lambda event, id=noteId: self.showTagWindow(id)
                    ellipsisBox.setFixedWidth(50)

                    # if statements to determine whether to add show more tags box and truncate tags
                    if widthCounter > 25 and oldWidthCounter != 0:
                        tagLayout.addWidget(ellipsisBox)
                        break
                    if widthCounter > 25 and oldWidthCounter == 0:
                        tagBoxLabel.setText(tag[1][:17]+"...")
                        tagLayout.addWidget(tagBox)
                        tagLayout.addWidget(ellipsisBox)
                    else:
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

        print(result)
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

    def getTags(self, noteId: int)->list[tuple] | dict[str, str] | None: # type: ignore [type-arg]
        tagAssociations:list[tuple] | dict[str, str] = tagLogic.getTagAssociationsHandler(noteId, databaseName) # type: ignore [type-arg]
        if type(tagAssociations) == dict[str, str]:
            QMessageBox.critical(self, tagAssociations["title"], tagAssociations["msg"])
            return None
        getSelectedTagsResponse: list[tuple] | dict[str, str] = tagLogic.getSelectedTagsHandler([assoc[2] for assoc in tagAssociations], databaseName) # type: ignore [type-arg]
        if type(getSelectedTagsResponse) == dict[str,str]:
            QMessageBox.critical(self, getSelectedTagsResponse["title"], getSelectedTagsResponse["msg"])
            return None
        return getSelectedTagsResponse

    def sortByTag(self, tags: list[tuple]): # type: ignore [type-arg, no-untyped-def]
        if tags != []:
            return tags[0][1]
        return chr(255)


def runApp() -> int:
    """Create and run the PyQt application."""
    app: QApplication = QApplication([])
    window: MainWindow = MainWindow()
    window.show()
    return int(app.exec())


if __name__ == "__main__":
    raise SystemExit(runApp())
