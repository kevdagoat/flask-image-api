import os
import threading
from flask_cors import CORS
from flask import Flask, send_file, abort
from werkzeug.datastructures import FileStorage
from flask_restplus import Api, reqparse, Resource

from utils.imageprocessor import ImageProcessor
from utils.misc import load_config

app = Flask(__name__)
api = Api(app=app, version='1.0', title='ImageAPI', description='A Simple Image Storage API')
CORS(app)

# Load our config
processor = ImageProcessor(load_config("config.yml"))

# Create our file upload parser for the upload route
file_upload = reqparse.RequestParser()
file_upload.add_argument('image',
                         type=FileStorage,
                         location='files',
                         required=True,
                         help='Image'
                         )

# Define our routes
@api.route("/upload/<string:name>")
class UploadImage(Resource):
    @api.expect(file_upload)
    def post(self, name):
        """Upload image into processing queue"""
        # Parse our arguments
        args = file_upload.parse_args()
        # Queue in processing queue
        processor.queue_image(name, args['image'].read())
        # Return success
        return {"success": True, "message": "In queue"}, 200

@api.route("/thumbnail/<string:name>")
class ThumbnailImage(Resource):
    def get(self, name):
        """Serve thumbnail from filesystem"""
        # Find our thumbnail location for the given name
        f = processor.thumbnail_location(name)
        # Check if exists
        if os.path.isfile(f):
            # Send file as JPG
            return send_file(f, mimetype="image/jpeg")
        else:
            # Not found!
            return abort(404)

@api.route("/original/<string:name>")
class OriginalImage(Resource):
    def get(self, name):
        """Serve original from filesystem"""
        # Find our image path
        f = processor.original_location(name)
        # Check if exists
        if os.path.isfile(f):
            # Send it as JPG
            return send_file(f, mimetype="image/jpeg")
        else:
            # Not found!
            return abort(404)

# Define and start our image processing thread
processing = threading.Thread(name="Image Processing Thread", target=processor.conversion_thread, daemon=True)
processing.start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

        