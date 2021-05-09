"""
This example shows usage of flask-geomapper with Amazon S3. It will upload
the map to a given bucket when a request is made to `/`.

COMPATIBLE VERSIONS:
  * ^1.0.0

OTHER REQUIREMENTS:
  boto3
"""

import flask
from flask_geomapper import flask_geomapper
import boto3

app = flask.Flask(__name__)
fg = flask_geomapper(app, debug=True)

s3 = boto3.resource("s3")
bucket = s3.Bucket("my_bucket") # replace with bucket name

@app.route("/")
def upload_image():
    bucket.put_object(Body=fg.get_img(), ContentType="image/png", Key="MyKey") # put plot into S3
    return {"message": "Image saved to S3!"}

app.run(debug=True)