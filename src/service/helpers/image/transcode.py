import io
import logging

import PIL.Image

logging.getLogger("PIL").setLevel(logging.ERROR)


def transcode_to_jpeg(file_object: io.BytesIO) -> io.BytesIO:
    jpeg_image_bytes = io.BytesIO()
    PIL.Image.open(file_object).convert("RGB").save(jpeg_image_bytes, format="JPEG")
    jpeg_image_bytes.seek(0)
    return io.BytesIO(jpeg_image_bytes.getvalue())
