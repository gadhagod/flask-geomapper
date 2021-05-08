"""
This example shows how to ignore routes and status codes from
flask-geomapper. 
`/ignore` and 404s does not count any locations
"""

import flask
from flask_geomapper import flask_geomapper

app = flask.Flask(__name__)
fg = flask_geomapper(app, exclude_routes=["/ignore"], exclude_status_codes=[404], debug=True)

@app.route("/")
def show_map():
    return flask.send_file(fg.get_img(), mimetype="image/png")

@app.route("/ignore")
def ignore_this():
    return {"message": "This request is ignored from flask-geomapper"}

app.run(debug=True)