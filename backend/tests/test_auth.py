from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException

from app.auth import (
    EMAIL_CLAIM,
    ROLES_CLAIM,
    extract_user_identity,
    has_editor_access,
    verify_frontend_request,
)


class TestExtractUserIdentity:
    def test_none_user(self):
        assert extract_user_identity(None) is None

    def test_empty_user(self):
        assert extract_user_identity({}) is None

    def test_custom_claim(self):
        user = {EMAIL_CLAIM: "alice@example.com"}
        assert extract_user_identity(user) == "alice@example.com"

    def test_standard_email(self):
        user = {"email": "bob@example.com"}
        assert extract_user_identity(user) == "bob@example.com"

    def test_sub_fallback(self):
        user = {"sub": "auth0|123"}
        assert extract_user_identity(user) == "auth0|123"

    def test_custom_claim_takes_priority(self):
        user = {
            EMAIL_CLAIM: "custom@example.com",
            "email": "standard@example.com",
            "sub": "auth0|123",
        }
        assert extract_user_identity(user) == "custom@example.com"


class TestHasEditorAccess:
    def test_none_user(self):
        assert has_editor_access(None) is False

    def test_no_roles(self):
        assert has_editor_access({}) is False

    def test_editor_role(self):
        user = {ROLES_CLAIM: ["editor"]}
        assert has_editor_access(user) is True

    def test_admin_role(self):
        user = {ROLES_CLAIM: ["admin"]}
        assert has_editor_access(user) is True

    def test_case_insensitive(self):
        user = {ROLES_CLAIM: ["Editor"]}
        assert has_editor_access(user) is True

    def test_wrong_role(self):
        user = {ROLES_CLAIM: ["viewer"]}
        assert has_editor_access(user) is False

    def test_string_role_coerced(self):
        user = {ROLES_CLAIM: "admin"}
        assert has_editor_access(user) is True


class TestVerifyFrontendRequest:
    @patch("app.auth.config")
    def test_no_api_key_configured_raises_500(self, mock_config: MagicMock):
        mock_config.API_KEY = ""
        with pytest.raises(HTTPException) as exc_info:
            verify_frontend_request(x_api_key="")
        assert exc_info.value.status_code == 500

    @patch("app.auth.config")
    def test_missing_api_key_raises_403(self, mock_config: MagicMock):
        mock_config.API_KEY = "secret"
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            verify_frontend_request(x_api_key="")
        assert exc_info.value.status_code == 403

    @patch("app.auth.config")
    def test_wrong_api_key_raises_403(self, mock_config: MagicMock):
        mock_config.API_KEY = "secret"
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            verify_frontend_request(x_api_key="wrong-key")
        assert exc_info.value.status_code == 403

    @patch("app.auth.config")
    def test_correct_api_key_passes(self, mock_config: MagicMock):
        mock_config.API_KEY = "secret"
        assert verify_frontend_request(x_api_key="secret") is None
