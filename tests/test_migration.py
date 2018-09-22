"""
Test file for database methods written in db.py

All test methods must receive client as an argument,
otherwise the database variable won't be configured correctly
"""
from mflix.db import get_movie
from datetime import datetime
import pytest


@pytest.mark.migration
def test_proper_type(client):
    result = get_movie("573a1391f29313caabcd8526")
    assert isinstance(result.get('lastupdated'), datetime)
