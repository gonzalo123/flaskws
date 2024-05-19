from flask import request, abort


def validate_bearer_token(headers, bearer_token: str):
    if 'Authorization' not in headers:
        abort(401)
    data = request.headers['Authorization']
    if str.replace(str(data), 'Bearer ', '') != bearer_token:
        abort(401)
