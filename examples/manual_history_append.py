"""
This examples shows how to manually add locations to the map.

COMPATIBLE VERSIONS:
    ^2.0.0
"""

import flask
from flask_geomapper import flask_geomapper

app = flask.Flask(__name__) # init flask app
fg = flask_geomapper(app, count_trigger=app.before_request, debug=True) 

@app.route("/")
def show_map():
    fg.add_locations([50], [50]) # Add a location with longitude 50 and latitude 50
    return flask.send_file(fg.get_img(), mimetype="image/png")

app.run(debug=True, use_reloader=False)