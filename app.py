from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy import create_engine, inspect
import numpy as np 
import datetime as dt

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
session = Session(engine)

Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Routes
#################################################

# Home Route
@app.route("/")
def welcome():
    return (
        f"Welcome to the climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start/<start><br/>"
        f"/api/v1.0/start_end/<start>/<end><br/>"
    )

# Precipitation Route
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data as json"""
    precip_results = session.query(Measurement.date, Measurement.prcp).\
    group_by(Measurement.date).\
    order_by(Measurement.date).all()

    session.close()
    
    return jsonify(precip_results)

# Stations Route
@app.route("/api/v1.0/stations")
def stations():
    """Return the station data as json"""
    station_results = session.query(Station.name).all()
    
    session.close()
    
    return jsonify(station_results)

# Temperature Route
@app.route("/api/v1.0/tobs")
def temperature():
    """Return the tobs data as json"""
    date = dt.datetime(2016, 8, 23)

    temperatures = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.date > date).\
    filter(Measurement.station == "USC00519397").\
    group_by(Measurement.date).\
    order_by(Measurement.date).all()

    session.close()

    return jsonify(temperatures)

# Start Date Route
@app.route("/api/v1.0/start/<start>")
def start_date_route(start):
    """Fetch the temperature data for the stations start date that matches
       the path variable supplied by the user, or a 404 if not."""

    # start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    summary = session.query(Measurement.station,func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
    filter(Measurement.date >= start).\
    group_by(Measurement.date).\
    order_by(Measurement.date).all()
    
    session.close()

    start = []
    for station, min_tob, max_tob, avg_tob in summary:
        start_dict = {}
        start_dict['Station'] = station
        start_dict['Min Temp'] = min_tob
        start_dict['Max Temp'] = max_tob
        start_dict['Avg Temp'] = avg_tob
        start.append(start_dict)
    return jsonify(start)


# Start and End Date Route
@app.route("/api/v1.0/start_end/<start>/<end>")
def start_end_route(start, end):
    """Fetch the temperature data for the station's start and end date that matches
       the path variable supplied by the user, or a 404 if not."""

    # start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    # end_date = dt.datetime.strptime(end, "%Y-%m-%d")
    start_end_summary = session.query(Measurement.station, func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
    filter(Measurement.date >= start).\
    filter(Measurement.date<= end).\
    group_by(Measurement.date).\
    order_by(Measurement.date).all()
    
    session.close()

    start_end = []
    for station, min_tob, max_tob, avg_tob in start_end_summary:
        start_end_dict = {}
        start_end_dict['Station'] = station
        start_end_dict['Min Temp'] = min_tob
        start_end_dict['Max Temp'] = max_tob
        start_end_dict['Avg Temp'] = avg_tob
        start_end.append(start_end_dict)
    
    return jsonify(start_end)    

    return jsonify({"error": f"Date {start} not found."}), 404


if __name__ == "__main__":
    app.run(debug=True)