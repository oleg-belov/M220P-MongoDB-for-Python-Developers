from flask import Blueprint, request, jsonify
from mflix.db import get_movie, get_movies, get_movies_by_country, \
    get_movies_faceted, add_comment, update_comment, delete_comment, \
    get_configuration

from flask_cors import CORS
from flask_jwt_extended import (
    jwt_required, get_jwt_claims
)
from mflix.api.user import jwt, User
from mflix.api.utils import expect
from datetime import datetime


movies_api_v1 = Blueprint(
    'movies_api_v1', 'movies_api_v1', url_prefix='/api/v1/movies')

CORS(movies_api_v1)


@movies_api_v1.route('/', methods=['GET'])
def api_get_movies():
    MOVIES_PER_PAGE = 20

    (movies, total_num_entries) = get_movies(
        None, page=0, movies_per_page=MOVIES_PER_PAGE)

    response = {
        "movies": movies,
        "page": 0,
        "filters": {},
        "entries_per_page": MOVIES_PER_PAGE,
        "total_results": total_num_entries,
    }

    return jsonify(response)


@movies_api_v1.route('/search', methods=['GET'])
def api_search_movies():
    MOVIES_PER_PAGE = 20

    # first determine the page of the movies to collect
    try:
        page = request.args.get('page')
        # if no page, get the first page (0 indexed)
        if page is None:
            page = 0
        # otherwise pass the page along the client asked for
        else:
            page = int(page)
    except (TypeError, ValueError) as e:
        print('Got bad value for page:\t', e)
        page = 0

    # determine the filters
    filters = {}
    return_filters = {}
    cast = request.args.getlist('cast')
    genre = request.args.getlist('genre')
    if cast:
        filters["cast"] = cast
        return_filters["cast"] = cast
    if genre:
        filters["genres"] = genre
        return_filters["genre"] = genre
    search = request.args.get('text')
    if search:
        filters["text"] = search
        return_filters["search"] = search

    # finally use the database and get what is necessary
    (movies, total_num_entries) = get_movies(
        filters, page, MOVIES_PER_PAGE)

    response = {
        "status": "success",
        "movies": movies,
        "page": page,
        "filters": return_filters,
        "entries_per_page": MOVIES_PER_PAGE,
        "total_results": total_num_entries,
    }

    return jsonify(response), 200


@movies_api_v1.route('/id/<id>', methods=['GET'])
def api_get_movie_by_id(id):
    movie = get_movie(id)
    if movie is None or movie == {}:
        return jsonify({
            "status": "fail"
        }), 400
    else:
        updated_type = str(type(movie.get('lastupdated')))
        return jsonify(
            {
                "status": "success",
                "movie": movie,
                "updated_type": updated_type
            }
        ), 200


@movies_api_v1.route('/countries', methods=['GET'])
def api_get_movies_by_country():
    try:
        countries = request.args.getlist('countries')
        results = get_movies_by_country(countries)
        response_object = {
            "status": "success",
            "titles": results
        }
        return jsonify(response_object), 200
    except Exception as e:
        response_object = {
            "status": "fail",
            "error": str(e)
        }
        return jsonify(response_object), 400


@movies_api_v1.route('/facet-search', methods=['GET'])
def api_search_movies_faceted():
    MOVIES_PER_PAGE = 20

    # first determine the page of the movies to collect
    try:
        page = request.args.get('page')
        # if no page, get the first page (0 indexed)
        if page is None:
            page = 0
        # otherwise pass the page along the client asked for
        else:
            page = int(page)
    except (TypeError, ValueError) as e:
        print('Got bad value for page, defaulting to 0:\t', e)
        page = 0

    # determine the filters
    filters = {}
    return_filters = {}
    cast = request.args.getlist('cast')
    if cast:
        filters["cast"] = cast
        return_filters["cast"] = cast
    if not filters:
        return api_search_movies()

    # finally use the database and get what is necessary
    try:
        (movies, total_num_entries) = get_movies_faceted(
            filters, page, MOVIES_PER_PAGE)

        response = {
            "status": "success",
            "movies": movies.get('movies'),
            "facets":  {
                "runtime": movies.get('runtime'),
                "rating": movies.get('rating')
            },
            "page": page,
            "filters": return_filters,
            "entries_per_page": MOVIES_PER_PAGE,
            "total_results": total_num_entries,
        }

        return jsonify(response), 200
    except Exception as e:
        return jsonify({'status': 'fail', 'error': str(e)})


@movies_api_v1.route('/comment', methods=["POST"])
@jwt_required
def api_post_comment():
    """
    Posts a comment about a specific movie. Validates the user is logged in by
    ensuring a valid JWT is provided
    """
    claims = get_jwt_claims()
    user = User.from_claims(claims)
    post_data = request.get_json()
    try:
        movie_id = expect(post_data.get('movie_id'), str, 'movie_id')
        comment = expect(post_data.get('comment'), str, 'comment')
        add_comment(movie_id, user, comment, datetime.now())
        updated_comments = get_movie(movie_id).get('comments')
        return jsonify({"status": "success", "comments": updated_comments})
    except Exception as e:
        return jsonify({'status': 'fail', 'error': str(e)})


@movies_api_v1.route('/comment', methods=["PUT"])
@jwt_required
def api_update_comment():
    """
    Updates a user comment. Validates the user is logged in by ensuring a
    valid JWT is provided
    """
    claims = get_jwt_claims()
    user_email = User.from_claims(claims).email
    post_data = request.get_json()
    try:
        comment_id = expect(post_data.get('comment_id'), str, 'comment_id')
        updated_comment = expect(post_data.get(
            'updated_comment'), str, 'updated_comment')
        movie_id = expect(post_data.get('movie_id'), str, 'movie_id')
        update_comment(comment_id, user_email, updated_comment, datetime.now())
        updated_comments = get_movie(movie_id).get('comments')
        return jsonify({"status": "success", "comments": updated_comments})
    except Exception as e:
        return jsonify({'status': 'fail', 'error': str(e)})


@movies_api_v1.route('/comment', methods=["DELETE"])
@jwt_required
def api_delete_comment():
    """
    Delete a comment. Requires a valid JWT
    """
    claims = get_jwt_claims()
    user_email = User.from_claims(claims).email
    post_data = request.get_json()
    try:
        comment_id = expect(post_data.get('comment_id'), str, 'comment_id')
        movie_id = expect(post_data.get('movie_id'), str, 'movie_id')
        delete_comment(comment_id, user_email)
        updated_comments = get_movie(movie_id).get('comments')
        return jsonify({'status': 'success', 'comments': updated_comments})
    except Exception as e:
        return jsonify({'status': 'fail', 'error': str(e)}), 200


@movies_api_v1.route('/config-options', methods=["GET"])
def get_conn_pool_size():
    try:
        (pool_size, w_concern, user_info) = get_configuration()
        return jsonify({
            'status': 'success',
            'pool_size': pool_size,
            'wtimeout': w_concern._WriteConcern__document.get('wtimeout', '0'),
            **user_info
        })
    except Exception as e:
        return jsonify({'status': 'fail', 'error': str(e)})
