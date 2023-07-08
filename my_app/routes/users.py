from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
from my_app.models.user import User
from my_app.models.history import History
from my_app.models.bird import Bird
from my_app import db
import jwt
import datetime
from my_app.config import SECRET_KEY
from my_app.utils.auth import current_user_is_admin
import datetime
from sqlalchemy import func
from functools import wraps

users_blueprint = Blueprint("users", __name__)


@users_blueprint.route("/stats", methods=["GET"])
def get_stats():
    if not current_user_is_admin():
        return jsonify({"error": "Unauthorized"}), 401

    users_count = User.query.count()
    histories_count = History.query.count()
    birds_count = Bird.query.count()

    response = {
        "users_count": users_count,
        "histories_count": histories_count,
        "birds_count": birds_count,
    }

    return jsonify(response), 200


def verify_token(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"message": "Token is missing"}), 401

        try:
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.decoded_token = decoded_token
        except jwt.InvalidTokenError:
            return jsonify({"message": "Invalid token"}), 401

        return f(*args, **kwargs)

    return decorated_function


@users_blueprint.route("/verifyToken", methods=["GET"])
@verify_token
def verify_token_route():
    return jsonify({"message": "Token is valid"})


@users_blueprint.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not check_password_hash(user.password, password):
        return jsonify({"error": "Invalid email or password"}), 401

    token_payload = {
        "user_id": user.id,
        "role": user.role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1),
    }
    token = jwt.encode(token_payload, SECRET_KEY, algorithm="HS256")

    return jsonify({"token": token}), 200


@users_blueprint.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return jsonify({"error": "Email already exists"}), 400

    user = User(email=email, password=generate_password_hash(password), role=0)

    db.session.add(user)
    db.session.commit()

    token_payload = {
        "user_id": user.id,
        "role": user.role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1),
    }
    token = jwt.encode(token_payload, SECRET_KEY, algorithm="HS256")

    return jsonify({"token": token}), 201


@users_blueprint.route("/users", methods=["GET"])
def get_all_users():
    if not current_user_is_admin():
        return jsonify({"error": "Unauthorized"}), 401

    users = User.query.all()
    result = [
        {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "created_at": user.created_at,
        }
        for user in users
    ]

    return jsonify(result), 200


@users_blueprint.route("/users/<int:user_id>/update-role", methods=["PUT"])
def update_user_role(user_id):
    if not current_user_is_admin():
        return jsonify({"error": "Unauthorized"}), 401

    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    new_role = request.json.get("role")

    if new_role is None or new_role not in [0, 1]:
        return jsonify({"error": "Invalid role"}), 400

    user.role = new_role
    db.session.commit()

    return jsonify({"message": "User role updated successfully"}), 200


@users_blueprint.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    if not current_user_is_admin():
        return jsonify({"error": "Unauthorized"}), 401

    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "User deleted successfully"}), 200


@users_blueprint.route("/users/registration-stats/week-count", methods=["GET"])
def get_weekly_registration_stats():
    if not current_user_is_admin():
        return jsonify({"error": "Unauthorized"}), 401

    today = datetime.datetime.now().date()
    start_date = today - datetime.timedelta(days=6)
    end_date = today

    date_range = [start_date + datetime.timedelta(days=i) for i in range(7)]

    stats = (
        db.session.query(func.date(User.created_at), func.count(User.id))
        .filter(User.created_at >= start_date, User.created_at <= end_date)
        .group_by(func.date(User.created_at))
        .all()
    )

    result = [{"date": str(date), "count": 0} for date in date_range]
    date_count_map = {str(stat[0]): stat[1] for stat in stats}
    for item in result:
        if item["date"] in date_count_map:
            item["count"] = date_count_map[item["date"]]

    return jsonify(result), 200


@users_blueprint.route("/users/registration-stats/15-days-count", methods=["GET"])
def get_monthly_registration_stats():
    if not current_user_is_admin():
        return jsonify({"error": "Unauthorized"}), 401

    today = datetime.datetime.now().date()
    start_date = today - datetime.timedelta(days=14)
    end_date = today

    date_range = [
        start_date + datetime.timedelta(days=i)
        for i in range((end_date - start_date).days + 1)
    ]

    stats = (
        db.session.query(func.date(User.created_at), func.count(User.id))
        .filter(User.created_at >= start_date, User.created_at <= end_date)
        .group_by(func.date(User.created_at))
        .all()
    )

    result = [{"date": str(date), "count": 0} for date in date_range]
    date_count_map = {str(stat[0]): stat[1] for stat in stats}
    for item in result:
        if item["date"] in date_count_map:
            item["count"] = date_count_map[item["date"]]

    return jsonify(result), 200
