import unittest
from unittest.mock import patch, Mock
from fastapi.testclient import TestClient
from data.models import CategoryResponse, Category
from routers import categories
from main import app  # Assuming your FastAPI app is in main.py


class TestCategoriesRouter(unittest.TestCase):



