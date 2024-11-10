import unittest
from unittest.mock import Mock, patch
from fastapi.exceptions import HTTPException
from common.responses import BadRequest, Unauthorized, NotFound, Forbidden
from routers import topics as topics_router
from data.models import TopicResponse, CategoryResponse, TopicCreation
