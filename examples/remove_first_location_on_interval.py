"""
This example shows usage of flask-geomapper that removes the earliest
  saved on the map on an interval. This is done so that you don't get 
  old data. Why to schedule location removals? If there are hundreds of
  millions of requests made, massive RAM will be used. 
  Using this method is highly recommended for production use cases.

COMPATIBLE VERSIONS:
  * ^1.0.0

OTHER REQUIREMENTS:
  apscheduler

NOTE: With schedules, you can't turn on Flask's debug mode reloader,
  as it then would load the app twice. If you wish to run this app in 
  debug mode, you must do `app.run(debug=True, use_reloader=False).
  More info: 
  https://stackoverflow.com/questions/14874782/apscheduler-in-flask-executes-twice

ALTERNATIVES: An alternative to apscheduler is "flask-apscheduler":
  https://viniciuschiele.github.io/flask-apscheduler
"""

import flask
from flask_geomapper import flask_geomapper
from apscheduler.schedulers.background import BackgroundScheduler

app = flask.Flask(__name__)
fg = flask_geomapper(app, debug=True)

scheduler = BackgroundScheduler(daemon=True) # init scheduler
scheduler.add_job(func=fg.pop_first_location, trigger="interval", seconds=60)
"""
^^^
Adds a job to be executed on a time interval. In our case, the function to 
be executed is `fg.pop_first_location` (first param) and the interval is 60
seconds (third param). 
`fg.pop_first_location` removes the first location stored in memory.
"""

scheduler.start() # start scheduler

@app.route("/")
def home():
    return flask.send_file(fg.get_img(), "image/png")

app.run(debug=True, use_reloader=False)