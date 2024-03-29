import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify
import datetime as dt

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False}, echo=True)
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station
session = Session(engine)

app = Flask(__name__)

# Flask Routes

@app.route("/")
def welcome():
    #List all available api routes.
    return (
        f"Welcome!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/(start)<br/>"
        f"/api/v1.0/(start)/(end)<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    max_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    max_date = max_date[0]
    year_ago = dt.datetime.strptime(max_date, "%Y-%m-%d") - dt.timedelta(days=366)
    results_precipitation = session.query(measurement.date, measurement.prcp).filter(measurement.date >= year_ago).all()
    precipitation_dict = dict(results_precipitation)
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations(): 
    results_stations =  session.query(measurement.station).group_by(measurement.station).all()
    stations_list = list(np.ravel(results_stations))
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs(): 
    max_date = session.query(measurement.date).order_by(measurement.date.desc()).first()
    max_date = max_date[0]
    year_ago = dt.datetime.strptime(max_date, "%Y-%m-%d") - dt.timedelta(days=366)
    results_tobs = session.query(measurement.date, measurement.tobs).filter(measurement.date >= year_ago).all()
    tobs_list = list(results_tobs)
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def start(start=None):
    #Return a JSON list of tmin, tmax, tavg for the dates greater than or equal to the date provided
    from_start = session.query(measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start).group_by(measurement.date).all()
    from_start_list=list(from_start)
    return jsonify(from_start_list)    

@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
    #Return a JSON list of tmin, tmax, tavg for the dates in range of start date and end date inclusive
    between_dates = session.query(measurement.date, func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start).filter(measurement.date <= end).group_by(measurement.date).all()
    between_dates_list=list(between_dates)
    return jsonify(between_dates_list)

if __name__ == '__main__':
    app.run(debug=True)