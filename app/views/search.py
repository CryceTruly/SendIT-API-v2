from flask import Flask, Blueprint, jsonify, request

from app.auth.decorator import response_message, token_required
from app.database.database import Database
from flask_cors import CORS

search = Blueprint('search', __name__)
CORS(search)
db = Database()


@search.route("/api/v2/search/", methods=['POST'])
@token_required
def search_app(current_user):
    data = request.get_json()

    if not 'query' in data:
        return response_message("failed", "please search", 400)
    query = data['query']
    results = db.search_app(query)
    response_data = []
    if isinstance(results, str):
        return response_message("not_found", results, 404)
    print(results)
    for result in results:
        res_obj = {
            "user_id": result[0],
            "user_email": result[2],
            "user_name": result[1],

        }
        response_data.append(res_obj)

    return jsonify({"message": "found", "data": response_data}), 200
