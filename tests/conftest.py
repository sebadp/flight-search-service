import os
import pytest

# Set the TESTING environment variable to "true" before importing the FastAPI application.
os.environ["TESTING"] = "true"

# Import the FastAPI application that will be used by all tests.
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    return TestClient(app)
