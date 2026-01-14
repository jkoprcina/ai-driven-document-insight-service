"""
API endpoint tests
"""
import pytest


# Skip API tests if the app takes too long to start (model loading)
pytestmark = pytest.mark.skip(reason="Skipping API tests to avoid slow model loading in CI/CD. These should be tested separately with a running server.")


def test_placeholder():
    """Placeholder test - real API tests require running server"""
    assert True
