"""
Pytest configuration and fixtures
"""
import pytest
import os


@pytest.fixture(autouse=True)
def setup_test_env():
    """Setup test environment variables"""
    os.environ["TESTING"] = "true"
    yield
    if "TESTING" in os.environ:
        del os.environ["TESTING"]
