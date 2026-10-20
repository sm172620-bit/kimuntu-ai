"""Text cleaning shared by data preparation, training and prediction.

The same function must be used at training time and at prediction time,
otherwise the model sees text in a different form than it was trained on.
"""
import html
import re

_TAG_RE = re.compile(r"<[^>]+>")
_URL_RE = re.compile(r"https?://\S+|www\.\S+")
_SPACE_RE = re.compile(r"\s+")


def clean_text(text: str) -> str:
    """Strip HTML tags and URLs, lowercase, and collapse whitespace."""
    if not isinstance(text, str):
        return ""
    text = html.unescape(_TAG_RE.sub(" ", text))
    text = _URL_RE.sub(" ", text)
    return _SPACE_RE.sub(" ", text.lower()).strip()
