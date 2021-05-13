"""
This example shows how you can integrate a database into flask-geomapper. 
For this example, Rockset (rockset.com) is used, though any would work.
flask-geomapper supports document databases out of the box.

ADVATANGES:
    * Retain location data even if server restarts
    * Map data across different servers
    * Use external mapping tools

OTHER REQUIREMENTS:
    * rockset

COMPATIBLE VERSIONS:
    * ^3.0.0

NOTE: This example uses IPs as document IDs, so they cannot be `None`
"""

import flask
from flask_geomapper import flask_geomapper
from apscheduler.schedulers.background import BackgroundScheduler
from rockset import Client, Q
from os import getenv

app = flask.Flask(__name__)
fg = flask_geomapper(app, debug=True)

token = getenv("RS2_TOKEN") # or set token to a string with your API key

rs = Client(token, "https://api.rs2.usw2.rockset.com") # configure server based off your location (this one is us west)
collection_name = "flask-locations" # configure based off your collection name and workspace (if not in "commons")
collection = rs.Collection.retrieve(collection_name)

previous_locations = list(rs.sql(Q(f"select * from \"{collection_name}\""))) # retrieve previous locations from database

if previous_locations != []: fg.add_locations(previous_locations, ip_key="_id") # if there are any items in the database, add them to flask-geomapper

def add_docs():
    collection.add_docs(fg.shape_to_docs())

scheduler = BackgroundScheduler(daemon=True) # init scheduler
scheduler.add_job(func=collection.add_docs, args=(fg.shape_to_docs(ip_key="_id"), ), trigger="interval", seconds=10)
"""
^^^
Add documents to collection every ten seconds.
Only locations with an unrecorded IP are added, by setting the `ip_key` parameter of 
`fg.shape_to_docs` (`flask_geomapper.flask_geomapper().shape_to_docs`) to `_id`, the
unique document identifier for Rockset.
"""
scheduler.start()

@app.route("/")
def home():
    return flask.send_file(fg.get_img(), "image/png")

app.run(debug=True, use_reloader=False)