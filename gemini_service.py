
import json
import streamlit as st

from google import genai
from google.genai import types

from prompts import DEADLINE_EXTRACTION_PROMPT

# Create the Gemini client only once
@st.cache_resource
def get_gemini_client():
    return genai.Client(
        api_key=st.secrets["GEMINI_API_KEY"]
    )


def _generate_deadline_response(contents):
    """Send input to Gemini and validate its JSON response."""

    client = get_gemini_client()
    model_name = st.secrets["GEMINI_MODEL"]

    response = client.models.generate_content(
        model=model_name,
        contents=contents,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.1,
        ),
    )

    if not response.text:
        raise ValueError(
            "Gemini returned an empty response. Please try again."
        )

    try:
        result = json.loads(response.text)
    except json.JSONDecodeError as exc:
        raise ValueError(
            "Gemini returned invalid JSON. Please try again."
        ) from exc

    if not isinstance(result, dict):
        raise ValueError("Unexpected response format from Gemini.")

    deadlines = result.get("deadlines")
    notes = result.get("notes", [])

    if not isinstance(deadlines, list):
        raise ValueError("The response does not contain a valid deadlines list.")

    if not isinstance(notes, list):
        raise ValueError("The response contains invalid notes.")

    # Validate the basic structure of every deadline
    required_fields = [
        "title",
        "subject",
        "due_date",
        "due_time",
        "task_type",
        "priority",
        "evidence",
        "needs_confirmation",
    ]

    for deadline in deadlines:
        if not isinstance(deadline, dict):
            raise ValueError("A deadline entry has an invalid format.")

        missing = [
            field for field in required_fields
            if field not in deadline
        ]

        if missing:
            raise ValueError(
                f"A deadline entry is missing fields: {missing}"
            )

        if not isinstance(deadline["title"], str):
            raise ValueError("A deadline title must be text.")

        if not isinstance(deadline["needs_confirmation"], bool):
            raise ValueError(
                "The needs_confirmation field must be true or false."
            )

    return result


def extract_deadlines(image_bytes, mime_type):
    """Extract academic deadlines from an uploaded image."""

    if not image_bytes:
        raise ValueError("The uploaded image is empty.")

    if mime_type not in ("image/jpeg", "image/png"):
        raise ValueError("Please upload a JPG or PNG image.")

    contents = [
        DEADLINE_EXTRACTION_PROMPT,
        "Analyze this academic document and extract its deadlines.",
        types.Part.from_bytes(
            data=image_bytes,
            mime_type=mime_type,
        ),
    ]

    return _generate_deadline_response(contents)


def extract_deadlines_from_text(text):
    """Extract academic deadlines from pasted text."""

    if not text or not text.strip():
        raise ValueError("Please enter some academic text.")

    contents = [
        DEADLINE_EXTRACTION_PROMPT,
        "Extract deadlines from the following academic text:\n\n"
        + text.strip(),
    ]

    return _generate_deadline_response(contents)
