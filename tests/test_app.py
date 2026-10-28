from pathlib import Path
from unittest.mock import patch
import sys

import pandas as pd
from streamlit.testing.v1 import AppTest


# Configure project paths so the application modules can be imported.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

APP_PATH = SRC_DIR / "app.py"


def run_app():
    """Start the Streamlit application for testing."""
    return AppTest.from_file(
        str(APP_PATH),
        default_timeout=10,
    ).run()


def test_app_starts_without_exception():
    """The Streamlit application should start without an exception."""
    at = run_app()

    assert not at.exception


def test_app_displays_main_title_and_tabs():
    """The application should display its title and three workflow tabs."""
    at = run_app()

    assert not at.exception

    assert any(
        "AI-Assisted Web Content Governance" in title.value
        for title in at.title
    )

    assert len(at.tabs) == 3


def test_app_displays_content_assessment_controls():
    """The content assessment tab should display its primary controls."""
    at = run_app()

    assert not at.exception

    assert any(
        "Select a content item" in selectbox.label
        for selectbox in at.selectbox
    )


def test_app_displays_human_review_controls():
    """The human review tab should expose decision and rationale controls."""
    at = run_app()

    assert not at.exception

    assert any(
        "Content item for review" in selectbox.label
        for selectbox in at.selectbox
    )

    assert any(
        "Final decision" in selectbox.label
        for selectbox in at.selectbox
    )

    assert any(
        "Reviewer rationale (required)" in text_area.label
        for text_area in at.text_area
    )


def test_app_displays_save_decision_button():
    """The interface should provide a control to save a human decision."""
    at = run_app()

    assert not at.exception

    assert any(
        button.label == "Save Human Decision"
        for button in at.button
    )


def test_blank_rationale_is_rejected():
    """Saving without a rationale should display a validation error."""
    with patch("app.save_review") as save_review:
        at = run_app()

        rationale = next(
            item
            for item in at.text_area
            if item.label == "Reviewer rationale (required)"
        )

        rationale.set_value("")

        next(
            item
            for item in at.button
            if item.label == "Save Human Decision"
        ).click().run()

        assert not at.exception

        assert any(
            "A reviewer rationale is required." in error.value
            for error in at.error
        )

        save_review.assert_not_called()


def test_valid_decision_calls_save_review():
    """Saving a valid human decision calls the database function."""
    with patch("database.save_review") as save_review:
        at = run_app()

        rationale = next(
            item
            for item in at.text_area
            if item.label == "Reviewer rationale (required)"
        )
        rationale.set_value(
            "Reviewed the evidence and retained the page."
        )

        save_button = next(
            item
            for item in at.button
            if item.label == "Save Human Decision"
        )
        save_button.click().run()

        assert not at.exception
        save_review.assert_called_once()

        saved_arguments = save_review.call_args.kwargs
        assert saved_arguments["rationale"] == (
            "Reviewed the evidence and retained the page."
        )

        assert any(
            "Human decision recorded in the audit history."
            in message.value
            for message in at.success
        )


def test_empty_audit_history_displays_message():
    """The app handles an empty audit history without an exception."""
    with patch(
        "database.get_audit_records",
        return_value=pd.DataFrame(),
    ):
        at = run_app()

        assert not at.exception
