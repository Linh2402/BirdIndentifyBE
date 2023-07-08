from google.cloud import storage
import uuid
import cv2
import numpy as np


def generate_unique_filename(filename):
    unique_filename = str(uuid.uuid4().hex) + "_" + filename
    return unique_filename


def upload_image_to_gcs(image):
    client = storage.Client()
    bucket_name = "identified-images"
    bucket = client.get_bucket(bucket_name)

    filename = generate_unique_filename("image.jpg")
    image_np = np.array(image)
    image_bytes = image_np.tobytes()

    blob = bucket.blob(filename)
    blob.upload_from_string(image_bytes, content_type="image/jpeg")

    file_url = blob.public_url
    return file_url
