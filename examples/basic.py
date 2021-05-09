"""
This example shows a super basic usage of flask-geomapper. On running, 
  the server, `/` route will show you a map of request locations.

COMPATIBLE VERSIONS:
    * 1.0.0^
"""

import flask
from flask_geomapper import flask_geomapper

app = flask.Flask(__name__) # init flask app
fg = flask_geomapper(app, count_trigger=app.before_request, debug=True) 

"""
^^^
Initialize mapping tool. The parameters passed:
- Instance of `flask.Flask` is the first param.
- `count_trigger` is the event that should add a location. The default is 
    `flask.Flask.after_request`, but to see our location on the first req 
     for this guide we are using `before_request`. More info in 
     `examples/count_triggers.py`.
- `debug` makes it so that if the IP of the request is your own (represented 
    as "127.0.0.1"), your IP is retrieved from an external API. Not to be
    used in production.
"""

@app.route("/")
def show_map():
    # This route is to return the map of request locations
    return flask.send_file(fg.get_img(), mimetype="image/png")
    """
    ^^^
    `fg.get_img` returns an `io.BytesIO` object, which is sent from Flask. 
     NOTE: The object has an added function `save`, where you can save the image.
    """

app.run(debug=True, use_reloader=False)