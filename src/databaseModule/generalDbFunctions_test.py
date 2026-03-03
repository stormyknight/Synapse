# pylint: disable=invalid-name
from unittest.mock import patch

from src.databaseModule import generalDbFunctions


# check to see that connectDb works
@patch("src.databaseModule.generalDbFunctions.sqlite3.connect")
# pylint: disable=invalid-name
def test_connectDb(mock_connect)->None: # type:ignore

    generalDbFunctions.connectDb("test")

    mock_connect.assert_called_once_with("test")
    mock_connect.return_value.execute.assert_called_once_with("PRAGMA foreign_keys = ON;")


#test to see that getDbPath works
# pylint: disable=invalid-name
def test_getDbPath()->None:
    assert ":memory:"  in generalDbFunctions.getDbPath(":memory:")
