"""
Test file for database methods written in db.py

All test methods must receive client as an argument,
otherwise the database variable won't be configured correctly
"""
import pytest
from mflix.db import get_movies


@pytest.mark.paging
def test_supports_paging_by_cast(client):
    filter = {'cast': ['Tom Hanks']}
    (movies0, results0) = get_movies(filter, 0, 20)
    assert len(list(movies0)) == 20
    assert results0 == 51
    (movies1, results1) = get_movies(filter, 1, 20)
    assert results1 == 51
    assert len(list(movies1)) == 20
    (movies2, results2) = get_movies(filter, 2, 20)
    assert len(list(movies2)) == 11


@pytest.mark.paging
def test_supports_paging_by_genre(client):
    filter = {'genres': ['History']}
    (movies0, results0) = get_movies(filter, 0, 20)
    assert len(list(movies0)) == 20
    assert results0 == 1503
    last_page = int(1503 / 20)
    (movies2, results2) = get_movies(filter, last_page, 20)
    assert len(list(movies2)) == results2 % 20


@pytest.mark.paging
def test_supports_paging_by_text(client):
    filter = {'text': 'bank robbery'}
    (movies0, results0) = get_movies(filter, 0, 20)
    assert len(list(movies0)) == 20
    assert results0 == 1084
    last_page = int(1084 / 20)
    (movies2, results2) = get_movies(filter, last_page, 20)
    assert len(list(movies2)) == 1084 % 20
