from flask import Blueprint, jsonify, request
from my_app.models.bird import Bird
from sqlalchemy import or_
from my_app.utils.auth import current_user_is_admin
from my_app import db


birds_blueprint = Blueprint("birds", __name__)


@birds_blueprint.route("/birds", methods=["GET"])
def get_all_birds():
    per_page = 10

    page = request.args.get("page", default=1, type=int)

    birds = Bird.query.paginate(page=page, per_page=per_page)
    total_count = birds.total

    birds_json = [bird.to_json() for bird in birds.items]

    response = {
        "page": page,
        "per_page": per_page,
        "total_count": total_count,
        "birds": birds_json,
    }

    return jsonify(response), 200


@birds_blueprint.route("/all_birds", methods=["GET"])
def get_birds():
    if not current_user_is_admin():
        return jsonify({"error": "Unauthorized"}), 401

    birds = Bird.query.all()
    total_count = len(birds)

    birds_json = [bird.to_json() for bird in birds]

    response = {
        "total_count": total_count,
        "birds": birds_json,
    }

    return jsonify(response), 200


@birds_blueprint.route("/birds/<int:id>", methods=["GET"])
def get_bird_by_id(id):
    bird = Bird.query.get(id)

    if bird is None:
        return jsonify({"error": "Bird not found"}), 404

    bird_json = bird.to_json()
    return jsonify(bird_json), 200


@birds_blueprint.route("/birds/<string:bird_order>", methods=["GET"])
def get_birds_by_order(bird_order):
    per_page = 10
    page = request.args.get("page", default=1, type=int)

    birds = Bird.query.filter_by(bird_order=bird_order).paginate(
        page=page, per_page=per_page
    )
    total_count = birds.total

    birds_json = [bird.to_json() for bird in birds.items]

    response = {
        "birds": birds_json,
        "page": page,
        "per_page": per_page,
        "total_count": total_count,
    }

    return jsonify(response), 200


@birds_blueprint.route("/birds/search", methods=["GET"])
def search_birds():
    per_page = 10
    page = request.args.get("page", default=1, type=int)
    keyword = request.args.get("keyword", type=str)

    if keyword is None:
        return jsonify({"error": "Keyword is required"}), 400

    birds = Bird.query.filter(
        or_(
            Bird.common_name.ilike("%" + keyword + "%"),
            Bird.vietnamese_name.ilike("%" + keyword + "%"),
            Bird.scientific_name.ilike("%" + keyword + "%"),
        )
    ).paginate(page=page, per_page=per_page)

    total_count = birds.total
    birds_json = [bird.to_json() for bird in birds.items]

    response = {
        "page": page,
        "per_page": per_page,
        "total_count": total_count,
        "birds": birds_json,
    }

    return jsonify(response), 200


@birds_blueprint.route("/birds/<int:id>", methods=["PUT"])
def update_bird(id):
    if not current_user_is_admin():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    bird = Bird.query.get(id)

    if not bird:
        return jsonify({"error": "Bird not found"}), 404

    bird.common_name = data.get("common_name", bird.common_name)
    bird.vietnamese_name = data.get("vietnamese_name", bird.vietnamese_name)
    bird.scientific_name = data.get("scientific_name", bird.scientific_name)
    bird.bird_order = data.get("bird_order", bird.bird_order)
    bird.family = data.get("family", bird.family)
    bird.description = data.get("description", bird.description)
    bird.distribution = data.get("distribution", bird.distribution)
    bird.diet = data.get("diet", bird.diet)
    bird.conservation_status = data.get("conservation_status", bird.conservation_status)
    bird.height = data.get("height", bird.height)
    bird.weight = data.get("weight", bird.weight)

    db.session.commit()

    return jsonify({"message": "Bird updated successfully"}), 200
