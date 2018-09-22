"""
Test file for database methods written in db.py

All test methods must receive client as an argument,
otherwise the database variable won't be configured correctly
"""
from mflix.db import add_comment, update_comment, delete_comment, get_movie
from mflix.api.user import User
from pymongo.results import InsertOneResult
from datetime import datetime
import pytest

test_user = {
    "name": "foobar",
    "email": "foobar@baz.com",
}

fake_user = {
    "name": "barfoo",
    "email": "baz@foobar.com"
}
# The Martian
movie_id = "573a13eff29313caabdd82f3"
now = datetime.now()
comment = {
    'text': 'fe-fi-fo-fum',
    'id': ''
}
user = User(test_user)
n_user = User(fake_user)


@pytest.mark.create_update_comments
def test_add_comment(client):
    result = add_comment(movie_id, user, comment['text'], now)
    assert isinstance(result, InsertOneResult)
    assert result.acknowledged is True
    assert result.inserted_id is not None

    comments = get_movie(movie_id).get('comments')
    assert comments[0].get('_id') == result.inserted_id
    assert comments[0].get('text') == comment['text']
    comment['id'] = result.inserted_id


@pytest.mark.create_update_comments
def test_update_comment(client):
    result = update_comment(comment['id'], user.email, 'foo foo foo', now)
    assert result.acknowledged is True

    comments = get_movie(movie_id).get('comments')
    assert result.raw_result.get('nModified') == 1
    assert comments[0].get('text') == 'foo foo foo'


@pytest.mark.create_update_comments
def test_do_not_update_comment_if_is_not_owner(client):
    result = update_comment(comment['id'], n_user.email, 'blah', now)
    assert result.raw_result.get('nModified') == 0
