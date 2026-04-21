# Synapse
# logicModule
# llm_helper.py

from ollama import chat
from pydantic import BaseModel, ValidationError


MODEL_NAME = "alibayram/smollm3"


class NoteAnalysis(BaseModel):
    summary: str
    tags: list[str]
    mood: str


def is_llm_available() -> bool:
    """
    Quick check to see whether the local Ollama model/server is reachable.
    Returns True if the model responds, otherwise False.
    """
    try:
        response = chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": "Reply with the single word: ready"
                }
            ],
            options={"temperature": 0}
        )

        content = response.message.content.strip().lower()
        return "ready" in content
    except Exception:
        return False


def analyze_note(note_text: str) -> dict[str, str | list[str]]:
    """
    Analyze a note and return structured results.

    Returns a dictionary with:
    - summary
    - tags
    - mood
    """
    if not note_text or not note_text.strip():
        return {
            "summary": "",
            "tags": [],
            "mood": ""
        }

    try:
        response = chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": f"""
Analyze this personal note.

Return:
- summary
- 3 to 5 tags
- mood

Keep the summary short and clear.
Keep the tags short, lowercase if possible.
Keep the mood to a short phrase.

Note:
{note_text}
"""
                }
            ],
            format=NoteAnalysis.model_json_schema(),
            options={"temperature": 0}
        )

        parsed = NoteAnalysis.model_validate_json(response.message.content)

        return {
            "summary": parsed.summary,
            "tags": parsed.tags,
            "mood": parsed.mood
        }

    except ValidationError:
        return {
            "summary": "Could not parse model response.",
            "tags": [],
            "mood": "unknown"
        }
    except Exception as exc:
        return {
            "summary": f"LLM error: {exc}",
            "tags": [],
            "mood": "unavailable"
        }


def generate_summary(note_text: str) -> str:
    """
    Return only the summary portion of the analysis.
    """
    result = analyze_note(note_text)
    summary = result.get("summary", "")
    return summary if isinstance(summary, str) else ""


def generate_tags(note_text: str) -> list[str]:
    """
    Return only the tags portion of the analysis.
    """
    result = analyze_note(note_text)
    tags = result.get("tags", [])
    return tags if isinstance(tags, list) else []


def generate_mood(note_text: str) -> str:
    """
    Return only the mood portion of the analysis.
    """
    result = analyze_note(note_text)
    mood = result.get("mood", "")
    return mood if isinstance(mood, str) else ""