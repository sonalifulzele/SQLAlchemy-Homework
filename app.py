#################################################
# Import Libraries
#################################################

import pandas as pd
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

# Import Flask
from flask import Flask, redirect, jsonify

#################################################
# Database Setup
#################################################

# Create connection to the sqllite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# View all of the classes that automap found
print(Base.classes.keys())

# Save reference to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Home page
@app.route("/")
def home():
    return ("<br><br>Available routes<br><br>/api/v1.0/precipitation<br>/api/v1.0/stations<br>/api/v1.0/tobs<br>/api/v1.0/start<br>/api/v1.0/start/end<br>")

# Precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    prcp_query_results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()

    #Convert the query results to a Dictionary using `date` as the key and `prcp` as the value.
    prcp_data_list= []
    for date, prcp in prcp_query_results:
        prcp_dict={}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        prcp_data_list.append(prcp_dict)
    
    #Return the JSON representation of your dictionary.
    return jsonify(prcp_data_list)   

# Stations
@app.route("/api/v1.0/stations")
def stations():
    station_query_results = session.query(Station.station).all()
    session.close()

    # Convert list of tuples into normal list
    station_list = list(np.ravel(station_query_results))

    # Return a JSON list of stations from the dataset.
    return jsonify(station_list)

# Temperature Observed
@app.route("/api/v1.0/tobs")
def tobs():
    # query for the dates and temperature observations from a year from the last data point.
    last_date = session.query(func.max(Measurement.date)).all() 
    last_date = pd.to_datetime(last_date[0])
    year_before_last_date = (last_date - dt.timedelta(days=365))
    print(last_date,year_before_last_date )
    session.close()
    

    tobs_query_results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= '2016-08-23').all()
    session.close()

    # Convert list of tuples into normal list
    tobs_list = list(np.ravel(tobs_query_results))
    
    # Return a JSON list of Temperature Observations (tobs) for the previous year.
    return jsonify(tobs_list)

# Summary of data greater than date supplied
@app.route("/api/v1.0/<start>")
def startDate(start):
    #start_date = dt.datetime.strptime(start)
    print(start)
    start_query_results = session.query(func.min(Measurement.tobs),\
                                        func.max(Measurement.tobs),\
                                        func.avg(Measurement.tobs)).\
                                        filter(Measurement.date >= start).all()
    session.close() 

    # Convert list of tuples into normal list
    start_list = list(np.ravel(start_query_results))

    # Return a JSON list
    return jsonify(start_list)

# Summary of data for time period
@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start,end):
    print(start, end)
    timePeriod_query_results = session.query(func.min(Measurement.tobs),\
                                        func.max(Measurement.tobs),\
                                        func.avg(Measurement.tobs)).\
                                        filter(Measurement.date >= start).\
                                        filter(Measurement.date <= end).\
                                        all()
    session.close() 

    # Convert list of tuples into normal list
    timePeriod_list = list(np.ravel(timePeriod_query_results))

    # Return a JSON list
    return jsonify(timePeriod_list)


if __name__ == "__main__":
	app.run(debug=True)