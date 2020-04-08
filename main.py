import os
import threading
from flask_cors import CORS
from flask import Flask, send_file, abort
from werkzeug.datastructures import FileStorage
from flask_restplus import Api, reqparse, Resource

from utils.imageprocessor import ImageProcessor

app = Flask(__name__)
api = Api(app=app)
CORS(app)

processor = ImageProcessor()
processor.set_image_path(os.path.join(os.getcwd(), "images"))

file_upload = reqparse.RequestParser()
file_upload.add_argument('image',
                         type=FileStorage,
                         location='files',
                         required=True,
                         help='Image'
                         )

@api.route("/upload/<string:name>")
class UploadImage(Resource):
    @api.expect(file_upload)
    def post(self, name):
        """Upload image into processing queue"""
        args = file_upload.parse_args()
        processor.queue_image(name, args['image'].read())
        return {"success": True, "message": "In queue"}, 200

@api.route("/thumbnail/<string:name>")
class ThumbnailImage(Resource):
    def get(self, name):
        """Serve thumbnail from filesystem"""
        f = processor.thumbnail_location(name)
        if os.path.isfile(f):
            return send_file(f, mimetype="image/jpeg")
        else:
            return abort(500)

@api.route("/original/<string:name>")
class OriginalImage(Resource):
    def get(self, name):
        """Serve original from filesystem"""
        f = processor.original_location(name)
        if os.path.isfile(f):
            return send_file(f, mimetype="image/jpeg")
        else:
            return abort(500)

processing = threading.Thread(name="Image Processing Thread", target=processor.conversion_thread, daemon=True)
processing.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

        