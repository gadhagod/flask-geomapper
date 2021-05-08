"""
Find the deployed app at https://flask-geomapper.herokuapp.com.
Same as `examples/basic.py`.
"""

import flask
from flask_geomapper import flask_geomapper

app = flask.Flask(__name__) 
fg = flask_geomapper(app, count_trigger=app.before_request)

@app.route("/")
def show_map():
    print(flask.request.headers.get("X-Forwarded-For", flask.request.remote_addr))
    return flask.send_file(fg.get_img(), mimetype="image/png") 

@app.route("/test")
def tst():
    return("IP: {}".format(
        flask.request.headers.get("X-Forwarded-For", flask.request.remote_addr)
    ))

if __name__ == "__main__": app.run()