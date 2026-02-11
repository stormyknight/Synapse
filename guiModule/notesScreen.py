from PyQt5.QtWidgets import QApplication, QWidget, QTextEdit, QVBoxLayout
from PyQt5.QtGui import QFont


# Subclass QMainWindow to customize your application's main window
class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Synapse")
        self.resize(1400, 1200)
        self.setStyleSheet("background-color: #A5F3FF;")

        # Creating the first textedit
        self.textEdit1 = QTextEdit()
        self.textEdit1.setStyleSheet("border: None")
        contentFont: QFont = QFont("Arial", 13)
        self.textEdit1.setFont(contentFont)

        # Creating a vertical box layout
        layout = QVBoxLayout(self)

        # Adding the first textedit into the layout
        layout.addWidget(self.textEdit1)

        self.setLayout(layout)


app = QApplication([])

window = MainWindow()
window.show()

app.exec()
