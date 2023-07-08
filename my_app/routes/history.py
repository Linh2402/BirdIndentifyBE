from flask import Blueprint, jsonify, request
import jwt
from my_app import db
from my_app.models.history import History
from my_app.models.prediction import Prediction
from my_app.config import SECRET_KEY
from sqlalchemy import func
import datetime
from my_app.utils.auth import current_user_is_admin

history_blueprint = Blueprint("history", __name__)


@history_blueprint.route("/history", methods=["GET"])
def get_history():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Token not provided"}), 401

    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = decoded.get("user_id")
        history = History.query.filter_by(user_id=user_id).all()
        history_json = [h.to_json() for h in history]

        for h in history_json:
            predictions = Prediction.query.filter_by(history_id=h["id"]).all()
            predictions_json = [p.to_json() for p in predictions]
            h["predictions"] = predictions_json

        return jsonify(history_json), 200
    except jwt.exceptions.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401


@history_blueprint.route("/histories", methods=["GET"])
def get_all_history():
    if not current_user_is_admin():
        return jsonify({"error": "Unauthorized"}), 401

    history_entries = History.query.all()
    history_json = [entry.to_json() for entry in history_entries]

    return jsonify(history_json), 200


@history_blueprint.route("/history/<int:history_id>", methods=["DELETE"])
def delete_history(history_id):
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Token not provided"}), 401

    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id = decoded.get("user_id")
        history = History.query.filter_by(id=history_id, user_id=user_id).first()
        if history is None:
            return jsonify({"error": "History not found"}), 404

        history.delete_history()

        return jsonify({"message": "History deleted successfully"}), 200
    except jwt.exceptions.InvalidTokenError:
        return jsonify({"error": "Invalid token"}), 401


@history_blueprint.route("/history/week-count", methods=["GET"])
def get_weekly_history_count():
    if not current_user_is_admin():
        return jsonify({"error": "Unauthorized"}), 401

    today = datetime.datetime.now().date()
    start_date = today - datetime.timedelta(days=6)
    end_date = today

    date_range = [start_date + datetime.timedelta(days=i) for i in range(7)]

    stats = (
        db.session.query(func.date(History.date), func.count(History.id))
        .filter(History.date >= start_date, History.date <= end_date)
        .group_by(func.date(History.date))
        .all()
    )

    result = [{"date": str(date), "count": 0} for date in date_range]
    date_count_map = {str(stat[0]): stat[1] for stat in stats}
    for item in result:
        if item["date"] in date_count_map:
            item["count"] = date_count_map[item["date"]]

    return jsonify(result), 200


@history_blueprint.route("/history/15-days-count", methods=["GET"])
def get_15_days_history_count():
    if not current_user_is_admin():
        return jsonify({"error": "Unauthorized"}), 401

    today = datetime.datetime.now().date()
    start_date = today - datetime.timedelta(days=14)
    end_date = today

    date_range = [
        start_date + datetime.timedelta(days=i)
        for i in range((end_date - start_date).days + 1)
    ]

    monthly_count = (
        db.session.query(func.date(History.date), func.count(History.id))
        .filter(History.date >= start_date, History.date <= end_date)
        .group_by(func.date(History.date))
        .all()
    )

    result = [{"date": str(date), "count": 0} for date in date_range]
    date_count_map = {str(stat[0]): stat[1] for stat in monthly_count}
    for item in result:
        if item["date"] in date_count_map:
            item["count"] = date_count_map[item["date"]]

    return jsonify(result), 200
