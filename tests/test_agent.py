import pytest
from app.agent import analyze_text, rewrite_text
import os
from unittest.mock import patch, MagicMock

SAMPLE = (
    """This is a bad sentnence with a typo. This is a very very long sentence """
    + "that will be flagged by the spaCy rule because it contains many tokens "
    "" + "and keeps going to reach the threshold."
    ""
)


def test_analyze_text():
    report = analyze_text(SAMPLE)
    assert "issues" in report
    assert isinstance(report["issues"], list)
    # long_sentences may be present as a list
    assert "long_sentences" in report


@patch("app.agent.openai.ChatCompletion.create")
def test_rewrite_with_openai(mock_create):
    # mock OpenAI response
    mock_resp = MagicMock()
    mock_resp.choices = [MagicMock(message=MagicMock(content="Rewritten text"))]
    mock_create.return_value = mock_resp
    os.environ["OPENAI_API_KEY"] = "testkey"
    out = rewrite_text("Some text to rewrite.")
    assert out == "Rewritten text"
    del os.environ["OPENAI_API_KEY"]


def test_rewrite_without_key():
    if "OPENAI_API_KEY" in os.environ:
        del os.environ["OPENAI_API_KEY"]
    out = rewrite_text("A simple text with bad grammar too see.")
    assert isinstance(out, str)
