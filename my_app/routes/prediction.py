import jwt
from datetime import date
import cv2
import numpy as np
from flask import Blueprint, jsonify, request
from tensorflow.keras.models import load_model
from my_app import db
from my_app.models.history import History
from my_app.models.prediction import Prediction
from my_app.utils.gcs import upload_image_to_gcs
from my_app.config import SECRET_KEY
from PIL import Image

prediction_blueprint = Blueprint("prediction", __name__)

model_path = "./MobileNet.h5"
model = None


def load_custom_model():
    global model
    model = load_model(model_path)


@prediction_blueprint.route("/predict", methods=["POST"])
def predict():
    global model

    if model is None:
        load_custom_model()

    file = request.files["image"]
    image = Image.open(file)

    image = image.resize((224, 224))
    image = np.expand_dims(image, axis=0)
    image = image / 255.0

    pred = model.predict(image)

    sorted_indices = np.argsort(-pred[0])
    top_5_indices = sorted_indices[:5]

    top_predictions = []
    for i, index in enumerate(top_5_indices):
        confidence = round(100 * pred[0][index], 2)
        prediction = {"predicted_id": int(index + 1), "confidence": confidence}
        top_predictions.append(prediction)

    token = request.headers.get("Authorization")
    user_id = None

    try:
        if token:
            decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id = decoded.get("user_id")
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        pass

    if user_id is not None:
        file_url = upload_image_to_gcs(image)
        history = History(date=date.today(), user_id=user_id, url=file_url)
        db.session.add(history)
        db.session.commit()

        for i, prediction_data in enumerate(top_predictions[:3]):
            confidence = prediction_data["confidence"]
            bird_id = prediction_data["predicted_id"]

            prediction = Prediction(
                confidence=confidence, history_id=history.id, bird_id=bird_id
            )
            db.session.add(prediction)

        db.session.commit()

    return jsonify(top_predictions)
