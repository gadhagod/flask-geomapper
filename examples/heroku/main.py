"""
Find the deployed app at https://flask-geomapper.herokuapp.com.
"""

import flask
from flask_geomapper import flask_geomapper
from apscheduler.schedulers.background import BackgroundScheduler
from rockset import Client, Q
from os import getenv

app = flask.Flask(__name__)
fg = flask_geomapper(app)

token = getenv("RS2_TOKEN")

rs = Client(token, "https://api.rs2.usw2.rockset.com")
collection_name = "flask-locations"
collection = rs.Collection.retrieve(collection_name)

previous_locations = list(rs.sql(Q(f"select * from \"{collection_name}\"")))

if previous_locations != []: fg.add_locations(previous_locations, ip_key="_id")

scheduler = BackgroundScheduler(daemon=True)
scheduler.add_job(func=collection.add_docs, args=(fg.shape_to_docs(ip_key="_id"), ), trigger="interval", seconds=10)
scheduler.start()

@app.route("/")
def home():
    return flask.send_file(fg.get_img(), "image/png")

@app.route("/data")
def data():
    return f"""
    History: {fg.history}"""

if __name__ == "__main__": app.run()