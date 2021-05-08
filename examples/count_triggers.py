"""
This example shows how you can change the trigger event that counts
locations. The default is `flask.Flask().after_request`, but that
can be changed based on your use case. The trigger does not need
to be a flask function.
This is also shown in `examples/basic.py`.
"""

import flask
from flask_geomapper import flask_geomapper

app = flask.Flask(__name__)
fg = flask_geomapper(app, count_trigger=app.before_request, debug=True)
"""
^^^
Saves location before a request.
"""

@app.route("/")
def show_map():
    return flask.send_file(fg.get_img(), mimetype="image/png")

app.run(debug=True)