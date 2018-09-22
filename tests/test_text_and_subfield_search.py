"""
Test file for database methods written in db.py

All test methods must receive client as an argument,
otherwise the database variable won't be configured correctly
"""
import pytest
from mflix.db import get_movies


@pytest.mark.text_and_subfield_search
def test_text_search(client):
    # ensure you sort text results based on their metaScore!!
    filter = {'text': 'mongo'}
    (movies, results) = get_movies(filter, 0, 20)
    movies = list(movies)
    assert len(movies) == 9
    assert results == 9
    assert movies[0].get('title') == "Flash Gordon Conquers the Universe"


@pytest.mark.text_and_subfield_search
def test_genre_search(client):
    filter = {'genres': ['Action']}
    (movies, results) = get_movies(filter, 0, 20)
    assert len(list(movies)) == 20
    assert results == 5917


@pytest.mark.text_and_subfield_search
def test_multiple_genre_search(client):
    filter = {'genres': ['Action', 'Adventure']}
    (movies, results) = get_movies(filter, 0, 25)
    assert len(list(movies)) == 25
    assert results == 8385


@pytest.mark.text_and_subfield_search
def test_cast_search(client):
    filter = {'cast': ['Elon Musk']}
    (movies, results) = get_movies(filter, 0, 20)
    assert len(list(movies)) == 1
    assert results == 1


@pytest.mark.text_and_subfield_search
def test_multiple_cast_search(client):
    filter = {'cast': ['Elon Musk', 'Robert Redford', 'Julia Roberts']}
    (movies, results) = get_movies(filter, 0, 33)
    assert (len(list(movies))) == 33
    assert results == 75
