from google.cloud import storage
import uuid
import io
import numpy as np
from PIL import Image
import cv2


def generate_unique_filename(filename):
    unique_filename = str(uuid.uuid4().hex) + "_" + filename
    return unique_filename


def upload_image_to_gcs(file):
    client = storage.Client()
    bucket_name = "identified-images"
    bucket = client.get_bucket(bucket_name)

    filename = generate_unique_filename(file.filename)

    image = Image.open(file)
    image = image.resize((224, 224))

    image_bytes = io.BytesIO()
    image.save(image_bytes, format="JPEG")
    image_bytes.seek(0)

    blob = bucket.blob(filename)
    blob.upload_from_file(image_bytes, content_type=file.content_type)

    file_url = blob.public_url
    return file_url
