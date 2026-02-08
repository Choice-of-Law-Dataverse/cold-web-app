"""Tests for the email notification service."""

from unittest.mock import patch

from app.services.email_notifications import (
    _build_moderation_url,
    _extract_summary,
    _get_admin_emails,
    send_new_suggestion_notification,
)


class TestGetAdminEmails:
    """Tests for parsing ADMIN_NOTIFICATION_EMAILS config."""

    def test_returns_empty_when_not_configured(self):
        with patch("app.services.email_notifications.config") as mock_config:
            mock_config.ADMIN_NOTIFICATION_EMAILS = None
            assert _get_admin_emails() == []

    def test_returns_empty_for_empty_string(self):
        with patch("app.services.email_notifications.config") as mock_config:
            mock_config.ADMIN_NOTIFICATION_EMAILS = ""
            assert _get_admin_emails() == []

    def test_single_email(self):
        with patch("app.services.email_notifications.config") as mock_config:
            mock_config.ADMIN_NOTIFICATION_EMAILS = "admin@cold.global"
            assert _get_admin_emails() == ["admin@cold.global"]

    def test_multiple_emails(self):
        with patch("app.services.email_notifications.config") as mock_config:
            mock_config.ADMIN_NOTIFICATION_EMAILS = "a@cold.global,b@cold.global,c@cold.global"
            assert _get_admin_emails() == ["a@cold.global", "b@cold.global", "c@cold.global"]

    def test_strips_whitespace(self):
        with patch("app.services.email_notifications.config") as mock_config:
            mock_config.ADMIN_NOTIFICATION_EMAILS = " a@cold.global , b@cold.global "
            assert _get_admin_emails() == ["a@cold.global", "b@cold.global"]

    def test_skips_empty_segments(self):
        with patch("app.services.email_notifications.config") as mock_config:
            mock_config.ADMIN_NOTIFICATION_EMAILS = "a@cold.global,,b@cold.global,"
            assert _get_admin_emails() == ["a@cold.global", "b@cold.global"]


class TestExtractSummary:
    """Tests for category-aware summary extraction."""

    def test_court_decision_uses_case_citation(self):
        payload = {"case_citation": "Doe v. Smith, 123 A.3d 456", "case_title": "Doe v. Smith"}
        assert _extract_summary("court_decisions", payload) == "Doe v. Smith, 123 A.3d 456"

    def test_court_decision_falls_back_to_case_title(self):
        payload = {"case_title": "Doe v. Smith"}
        assert _extract_summary("court_decisions", payload) == "Doe v. Smith"

    def test_court_decision_unknown_fallback(self):
        assert _extract_summary("court_decisions", {}) == "Unknown court decision"

    def test_domestic_instrument_uses_title(self):
        payload = {"title": "Rome I Regulation", "abbreviation": "Rome I"}
        assert _extract_summary("domestic_instruments", payload) == "Rome I Regulation"

    def test_domestic_instrument_uses_official_title(self):
        payload = {"official_title": "Bundesgesetz über das IPR"}
        assert _extract_summary("domestic_instruments", payload) == "Bundesgesetz über das IPR"

    def test_domestic_instrument_uses_title_en(self):
        payload = {"title_en": "Swiss PIL Act"}
        assert _extract_summary("domestic_instruments", payload) == "Swiss PIL Act"

    def test_regional_instrument_uses_abbreviation(self):
        payload = {"abbreviation": "EU-Rome I"}
        assert _extract_summary("regional_instruments", payload) == "EU-Rome I"

    def test_international_instrument_uses_name(self):
        payload = {"name": "HCCH Principles"}
        assert _extract_summary("international_instruments", payload) == "HCCH Principles"

    def test_instrument_unknown_fallback(self):
        assert _extract_summary("domestic_instruments", {}) == "Unknown instrument"

    def test_literature_combines_author_and_title(self):
        payload = {"author": "Jane Doe", "title": "Choice of Law in Contracts"}
        assert _extract_summary("literature", payload) == "Jane Doe — Choice of Law in Contracts"

    def test_literature_unknown_author(self):
        payload = {"title": "Some Title"}
        assert _extract_summary("literature", payload) == "Unknown author — Some Title"

    def test_literature_unknown_title(self):
        payload = {"author": "Jane Doe"}
        assert _extract_summary("literature", payload) == "Jane Doe — Unknown title"

    def test_generic_uses_data_key(self):
        payload = {"data": {"table": "Answers", "field": "Summary"}}
        result = _extract_summary("generic", payload)
        assert "Answers" in result

    def test_generic_truncates_long_payload(self):
        payload = {"data": "x" * 300}
        result = _extract_summary("generic", payload)
        assert len(result) <= 200


class TestBuildModerationUrl:
    """Tests for moderation URL generation."""

    def test_court_decisions(self):
        assert _build_moderation_url("court_decisions", 42) == "https://cold.global/moderation/court-decisions/42"

    def test_domestic_instruments(self):
        assert _build_moderation_url("domestic_instruments", 7) == "https://cold.global/moderation/domestic-instruments/7"

    def test_regional_instruments(self):
        assert _build_moderation_url("regional_instruments", 1) == "https://cold.global/moderation/regional-instruments/1"

    def test_international_instruments(self):
        url = _build_moderation_url("international_instruments", 99)
        assert url == "https://cold.global/moderation/international-instruments/99"

    def test_literature(self):
        assert _build_moderation_url("literature", 5) == "https://cold.global/moderation/literature/5"

    def test_generic(self):
        assert _build_moderation_url("generic", 10) == "https://cold.global/moderation/generic/10"

    def test_unknown_category_uses_raw_value(self):
        assert _build_moderation_url("unknown_cat", 3) == "https://cold.global/moderation/unknown_cat/3"


class TestSendNewSuggestionNotification:
    """Tests for the main send_new_suggestion_notification function."""

    def test_noop_when_api_key_missing(self, caplog):
        with patch("app.services.email_notifications.config") as mock_config:
            mock_config.RESEND_API_KEY = None
            with patch("app.services.email_notifications.resend") as mock_resend:
                send_new_suggestion_notification("court_decisions", 1, {"case_citation": "Test"})
                mock_resend.Emails.send.assert_not_called()

    def test_noop_when_admin_emails_missing(self, caplog):
        with patch("app.services.email_notifications.config") as mock_config:
            mock_config.RESEND_API_KEY = "re_test_key"
            mock_config.ADMIN_NOTIFICATION_EMAILS = None
            with patch("app.services.email_notifications.resend") as mock_resend:
                send_new_suggestion_notification("court_decisions", 1, {"case_citation": "Test"})
                mock_resend.Emails.send.assert_not_called()

    def test_sends_email_for_new_submission(self):
        with patch("app.services.email_notifications.config") as mock_config:
            mock_config.RESEND_API_KEY = "re_test_key"
            mock_config.ADMIN_NOTIFICATION_EMAILS = "admin@cold.global"
            mock_config.NOTIFICATION_SENDER_EMAIL = "CoLD <notifications@mail.cold.global>"
            with patch("app.services.email_notifications.resend") as mock_resend:
                send_new_suggestion_notification(
                    "court_decisions",
                    42,
                    {"case_citation": "Doe v. Smith", "submitter_email": "user@example.com"},
                )
                mock_resend.Emails.send.assert_called_once()
                call_args = mock_resend.Emails.send.call_args[0][0]
                assert call_args["from"] == "CoLD <notifications@mail.cold.global>"
                assert call_args["to"] == ["admin@cold.global"]
                assert "[CoLD] New Suggestion: Court Decision" in call_args["subject"]
                assert "Doe v. Smith" in call_args["text"]
                assert "user@example.com" in call_args["text"]
                assert "https://cold.global/moderation/court-decisions/42" in call_args["text"]

    def test_sends_email_for_edit_submission(self):
        with patch("app.services.email_notifications.config") as mock_config:
            mock_config.RESEND_API_KEY = "re_test_key"
            mock_config.ADMIN_NOTIFICATION_EMAILS = "admin@cold.global"
            mock_config.NOTIFICATION_SENDER_EMAIL = "CoLD <notifications@mail.cold.global>"
            with patch("app.services.email_notifications.resend") as mock_resend:
                send_new_suggestion_notification(
                    "literature",
                    7,
                    {"edit_entity_id": "LIT-123", "author": "Jane Doe", "title": "PIL Book"},
                )
                call_args = mock_resend.Emails.send.call_args[0][0]
                assert "Edit Suggestion" in call_args["subject"]
                assert "LIT-123" in call_args["text"]
                assert "Jane Doe — PIL Book" in call_args["text"]

    def test_sends_to_multiple_recipients(self):
        with patch("app.services.email_notifications.config") as mock_config:
            mock_config.RESEND_API_KEY = "re_test_key"
            mock_config.ADMIN_NOTIFICATION_EMAILS = "a@cold.global,b@cold.global"
            mock_config.NOTIFICATION_SENDER_EMAIL = "CoLD <notifications@mail.cold.global>"
            with patch("app.services.email_notifications.resend") as mock_resend:
                send_new_suggestion_notification("literature", 1, {"author": "X", "title": "Y"})
                call_args = mock_resend.Emails.send.call_args[0][0]
                assert call_args["to"] == ["a@cold.global", "b@cold.global"]

    def test_includes_submitter_comments_when_present(self):
        with patch("app.services.email_notifications.config") as mock_config:
            mock_config.RESEND_API_KEY = "re_test_key"
            mock_config.ADMIN_NOTIFICATION_EMAILS = "admin@cold.global"
            mock_config.NOTIFICATION_SENDER_EMAIL = "CoLD <notifications@mail.cold.global>"
            with patch("app.services.email_notifications.resend") as mock_resend:
                send_new_suggestion_notification(
                    "domestic_instruments",
                    3,
                    {"official_title": "Test Act", "submitter_comments": "Please review ASAP"},
                )
                call_args = mock_resend.Emails.send.call_args[0][0]
                assert "Please review ASAP" in call_args["text"]
                assert "Please review ASAP" in call_args["html"]

    def test_omits_comments_when_absent(self):
        with patch("app.services.email_notifications.config") as mock_config:
            mock_config.RESEND_API_KEY = "re_test_key"
            mock_config.ADMIN_NOTIFICATION_EMAILS = "admin@cold.global"
            mock_config.NOTIFICATION_SENDER_EMAIL = "CoLD <notifications@mail.cold.global>"
            with patch("app.services.email_notifications.resend") as mock_resend:
                send_new_suggestion_notification(
                    "domestic_instruments",
                    3,
                    {"official_title": "Test Act"},
                )
                call_args = mock_resend.Emails.send.call_args[0][0]
                assert "Comments:" not in call_args["text"]

    def test_resend_error_does_not_raise(self, caplog):
        with patch("app.services.email_notifications.config") as mock_config:
            mock_config.RESEND_API_KEY = "re_test_key"
            mock_config.ADMIN_NOTIFICATION_EMAILS = "admin@cold.global"
            mock_config.NOTIFICATION_SENDER_EMAIL = "CoLD <notifications@mail.cold.global>"
            with patch("app.services.email_notifications.resend") as mock_resend:
                mock_resend.Emails.send.side_effect = Exception("Resend API error")
                send_new_suggestion_notification("court_decisions", 1, {"case_citation": "Test"})

    def test_html_body_contains_review_link(self):
        with patch("app.services.email_notifications.config") as mock_config:
            mock_config.RESEND_API_KEY = "re_test_key"
            mock_config.ADMIN_NOTIFICATION_EMAILS = "admin@cold.global"
            mock_config.NOTIFICATION_SENDER_EMAIL = "CoLD <notifications@mail.cold.global>"
            with patch("app.services.email_notifications.resend") as mock_resend:
                send_new_suggestion_notification("regional_instruments", 15, {"abbreviation": "EU-Rome I"})
                call_args = mock_resend.Emails.send.call_args[0][0]
                assert "https://cold.global/moderation/regional-instruments/15" in call_args["html"]
                assert "EU-Rome I" in call_args["html"]

    def test_submitter_falls_back_to_user_token_email(self):
        with patch("app.services.email_notifications.config") as mock_config:
            mock_config.RESEND_API_KEY = "re_test_key"
            mock_config.ADMIN_NOTIFICATION_EMAILS = "admin@cold.global"
            mock_config.NOTIFICATION_SENDER_EMAIL = "CoLD <notifications@mail.cold.global>"
            with patch("app.services.email_notifications.resend") as mock_resend:
                send_new_suggestion_notification(
                    "domestic_instruments",
                    5,
                    {"official_title": "Test Act", "submitter_email": None},
                    user={"https://cold.global/email": "token-user@example.com"},
                )
                call_args = mock_resend.Emails.send.call_args[0][0]
                assert "token-user@example.com" in call_args["text"]
                assert "None" not in call_args["text"]

    def test_submitter_falls_back_to_user_email_field(self):
        with patch("app.services.email_notifications.config") as mock_config:
            mock_config.RESEND_API_KEY = "re_test_key"
            mock_config.ADMIN_NOTIFICATION_EMAILS = "admin@cold.global"
            mock_config.NOTIFICATION_SENDER_EMAIL = "CoLD <notifications@mail.cold.global>"
            with patch("app.services.email_notifications.resend") as mock_resend:
                send_new_suggestion_notification(
                    "domestic_instruments",
                    5,
                    {"official_title": "Test Act"},
                    user={"email": "fallback@example.com"},
                )
                call_args = mock_resend.Emails.send.call_args[0][0]
                assert "fallback@example.com" in call_args["text"]

    def test_submitter_not_provided_when_no_user(self):
        with patch("app.services.email_notifications.config") as mock_config:
            mock_config.RESEND_API_KEY = "re_test_key"
            mock_config.ADMIN_NOTIFICATION_EMAILS = "admin@cold.global"
            mock_config.NOTIFICATION_SENDER_EMAIL = "CoLD <notifications@mail.cold.global>"
            with patch("app.services.email_notifications.resend") as mock_resend:
                send_new_suggestion_notification(
                    "domestic_instruments",
                    5,
                    {"official_title": "Test Act", "submitter_email": None},
                )
                call_args = mock_resend.Emails.send.call_args[0][0]
                assert "Not provided" in call_args["text"]

    def test_payload_submitter_email_takes_precedence(self):
        with patch("app.services.email_notifications.config") as mock_config:
            mock_config.RESEND_API_KEY = "re_test_key"
            mock_config.ADMIN_NOTIFICATION_EMAILS = "admin@cold.global"
            mock_config.NOTIFICATION_SENDER_EMAIL = "CoLD <notifications@mail.cold.global>"
            with patch("app.services.email_notifications.resend") as mock_resend:
                send_new_suggestion_notification(
                    "domestic_instruments",
                    5,
                    {"official_title": "Test Act", "submitter_email": "form@example.com"},
                    user={"https://cold.global/email": "token@example.com"},
                )
                call_args = mock_resend.Emails.send.call_args[0][0]
                assert "form@example.com" in call_args["text"]
