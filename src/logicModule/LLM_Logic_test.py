# pylint: disable=invalid-name
from unittest.mock import MagicMock, patch

from src.logicModule import noteLogic
import src.logicModule.LLM_Helper as LLM_Helper


sampleNote = """
Today I worked on Synapse and finally got the offline model connected.
I still feel stressed because school is busy, but I am happy that progress is being made.
"""

result = noteLogic.analyzeNoteContent(sampleNote)

print(result)


result2 = noteLogic.analyzeAndStoreNote(
    noteId=1,
    content="Today I worked on Synapse and felt pretty good about my progress.",
    databaseName="synapse.db"
)

print(result2)


# pylint: disable=invalid-name
@patch("src.logicModule.LLM_Helper.chat")
def test_isLlmAvailable_true(mock_chat) -> None: # type: ignore[no-untyped-def]
    # Create a mock response object
    mockResponse = MagicMock()
    mockResponse.message.content = "ready"

    # Make chat() return this mock response
    mock_chat.return_value = mockResponse

    assert LLM_Helper.isLlmAvailable()


# pylint: disable=invalid-name
@patch("src.logicModule.LLM_Helper.chat")
def test_isLlmAvailable_exception(mock_chat) -> None: # type: ignore[no-untyped-def]
    # Make chat() raise an exception when called
    mock_chat.side_effect = Exception("Connection error")

    assert not LLM_Helper.isLlmAvailable()


# pylint: disable=invalid-name
def test_analyzeNote_emptyNote() -> None:
    assert LLM_Helper.analyzeNote("") == { "summary": "", "tags": [], "mood": "" }


# pylint: disable=invalid-name
@patch("src.logicModule.LLM_Helper.NoteAnalysis")
def test_analyzeNote_validationError(mock_analysis) -> None: # type: ignore[no-untyped-def]
    # Make chat() raise an exception when called
    mock_analysis.model_validate_json = MagicMock()
    mock_analysis.model_validate_json.side_effect = Exception("error")

    assert LLM_Helper.analyzeNote("test") == { "summary": "Could not parse model response.", "tags": [], "mood": "unknown" }


# pylint: disable=invalid-name
@patch("src.logicModule.LLM_Helper.chat")
def test_analyzeNote__exception(mock_chat) -> None: # type: ignore[no-untyped-def]
    # Make chat() raise an exception when called
    mock_chat.side_effect = Exception("Connection error")

    assert LLM_Helper.analyzeNote("test") == {  "summary": "LLM error: Connection error", "tags": [], "mood": "unavailable" }


# pylint: disable=invalid-name
@patch("src.logicModule.LLM_Helper.analyzeNote")
def test_generateSummary(mock_analyzeNote) -> None: # type: ignore[no-untyped-def]
    # analyzeNote Mock
    mock_analyzeNote.return_value =  { "summary": "parsed.summary", "tags": "parsed.tags", "mood": "parsed.mood" }

    assert LLM_Helper.generateSummary("content") == "parsed.summary"


@patch("src.logicModule.LLM_Helper.analyzeNote")
# pylint: disable=invalid-name
def test_generateTags(mock_analyzeNote) -> None: # type: ignore[no-untyped-def]
    # analyzeNote Mock
    mock_analyzeNote.return_value =  { "summary": "parsed.summary", "tags": ["parsed.tags"], "mood": "parsed.mood" }

    assert LLM_Helper.generateTags("content") == ["parsed.tags"]


@patch("src.logicModule.LLM_Helper.analyzeNote")
# pylint: disable=invalid-name
def test_generateMood(mock_analyzeNote) -> None: # type: ignore[no-untyped-def]
    # analyzeNote Mock
    mock_analyzeNote.return_value =  { "summary": "parsed.summary", "tags": ["parsed.tags"], "mood": "parsed.mood" }

    assert LLM_Helper.generateMood("content") == "parsed.mood"
