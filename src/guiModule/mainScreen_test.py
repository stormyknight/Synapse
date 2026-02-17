# Synapse
# guiModule
# mainScreen_test.py

# pylint: disable=invalid-name
import mainScreen


# Test to see if the user can type in editableContentText
# pylint: disable=invalid-name
def test_EditableContentText(qtbot)->None: # type: ignore
    # An instance of MainWindow used for testing
    testMainScreen: mainScreen.MainWindow = mainScreen.MainWindow()
    qtbot.keyClicks(testMainScreen.editableContentText, "It worked")
    assert (
        testMainScreen.editableContentText.toPlainText() == "It worked"
    ), "Text typed into editableContentText does not match expected text"
