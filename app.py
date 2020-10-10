######################################################################################################
######################################################################################################
#                                    CLIMATE APP                                                     #
#                                Adriana Avalos Vargas                                               #
######################################################################################################
######################################################################################################


#Import general dependencies 
import pandas as pd 
import datetime
from datetime import timedelta  
#Import sql dependencies for python
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
#Import dependedencies to create app
from flask import Flask, jsonify, request


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Station = Base.classes.station
Measurements = Base.classes.measurement


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to the Hawaii's temperature API<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        #f"/api/v1.0/<start>"
    )


@app.route("/api/v1.0/precipitation")
def precipitations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """convert query results into a dictionary using date as key and prcp as vañue"""
    # results of the querry
    results = session.query(Measurements.date, Measurements.prcp).all()
    
    session.close()

    #Lets write the dictionary
    prec_dic = dict()

    #loop to make the dictionary
    for result in results :
        date_time = result[0] 
        #Lets define the keys of the dictionary
        if date_time not in prec_dic:
            prec_dic.update({date_time : result[1]})

       #json file from dictionary     
    return jsonify(prec_dic)


@app.route("/api/v1.0/stations")
def stations_1():
     #Create our session (link) from Python to the DB
     session = Session(engine)

     """Return a list of station  data """
     # Query all passengers
     results = session.query(Station.name, Station.station).all()

     session.close()

     # Create a dictionary from the row data and append to a list of all_passengers
     all_stations = []
     for name, station in results:
         station_dict = {}
         station_dict["name"] = name
         station_dict["station"] = station
         all_stations.append(station_dict)

     return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs1():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """convert query results into a dictionary using date as key and prcp as vañue"""
    #Lets get the last date
    last_dat_strg = session.query(Measurements.date).order_by(Measurements.date.desc()).first()

    #Lets convert to a date time
    time = last_dat_strg[0]
    last_date = datetime.datetime.strptime(time, '%Y-%m-%d').date()
    #Lest substract a year (365 días)
    year_ago = last_date - timedelta(365)
    year_ago_str = year_ago.strftime('%Y-%m-%d')

    #Previous year
    year_ago2 = last_date -timedelta(730)
    year_ago2_str = year_ago2.strftime('%Y-%m-%d')
    
    #Querry the most recent year
    temp_q = session.query(Measurements.station, Measurements.tobs).filter(Measurements.date >= year_ago_str)

    #Lets get the most productive stantion in such a year
    #Lets create a dummy variable
    value_comp = 0
    for temp in temp_q:
        #Extract the name of the station
        name_station = temp[0]
        #Make a query with a filter
        number_stations = session.query(Measurements.station).filter(Measurements.station == name_station).count()
        if number_stations > value_comp :
            station = name_station
            value_comp = number_stations

    # results of the querry
    
    results = session.query(Measurements.date, Measurements.tobs).filter(Measurements.station == station).filter(Measurements.date>= year_ago2_str).filter(Measurements.date<year_ago_str)

    session.close()

    # Create a dictionary from the row data and append to a list of all_passengers
    all_temperatures = []
    for date, tobs in results:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["tobs"] = tobs
        all_temperatures.append(temp_dict)

    return jsonify(all_temperatures)


@app.route("/api/v1.0/<start>")
def start():
    
    #Create our session (link) from Python to the DB
    session = Session(engine)

    """convert query results into a dictionary using date as key and prcp as vañue"""
    #Lets get the last date
    last_dat_strg = session.query(Measurements.date).order_by(Measurements.date.desc()).first()

    #Lets get the firs date
    firs_dat_strg = session.query(Measurements.date).order_by(Measurements.date).first()

    #Lets ask for a date
    print("If you want to know general fata about temperature in Hawaii from a given start day to the last observation")
    print(f"Please give a start date to query, it should be between {firs_dat_strg} and {last_dat_strg}")
    print("Which is the year of interest (4 numbers)?")
    year = request.args['year']
    print("Which is the month of interest?")
    month = request.args['month']
    print("Which is the day of interest?")
    year = request.args['day']

    #Lets make the start and end date
    start_date = f"{year}-{month}-{date}"
   
    #Lets make a query
    temp_query = session.query(func.min(Measurements.tobs).filter(Measurements.date >= start_date).label("min_temp"), 
                            func.max(Measurements.tobs).filter(Measurements.date >= start_date).label("max_temp"),
                            func.avg(Measurements.tobs).filter(Measurements.date >= start_date).label("avg_temp"))

    session.close()

    res = temp_query.one()
    temperatures = {"max_temp" : res.max_temp, "min_temp" : res.min_temp, "avg_temp": res.avg_temp }

  

    return jsonify(temperatures)

@app.route("/api/v1.0/<start>/<end>")
def start_end():
    
    #Create our session (link) from Python to the DB
    session = Session(engine)

    """convert query results into a dictionary using date as key and prcp as vañue"""
    #Lets get the last date
    last_dat_strg = session.query(Measurements.date).order_by(Measurements.date.desc()).first()

    #Lets get the firs date
    firs_dat_strg = session.query(Measurements.date).order_by(Measurements.date).first()

    #Lets ask for a date
    print(f"If yow want to know information about Hawaii's temperatures in a given period of time:")
    print(f"Please give a start date to query, it should be between {firs_dat_strg} and {last_dat_strg}")
    print("Which is the year of interest (4 numbers)?")
    year = request.args['year']
    print("Which is the month of interest?")
    month = request.args['month']
    print("Which is the day of interest?")
    year = request.args['day']

    #Lets ask for a date
    print(f"Please give an end date to query, it should be between {firs_dat_strg} and {last_dat_strg}")
    print("Which is the year of interest (4 numbers)?")
    year_e = request.args['year_e']
    print("Which is the month of interest?")
    month_e = request.args['month_e']
    print("Which is the day of interest?")
    year_e = request.args['day_e']

    #Lets make the start and end date
    start_date = f"{year}-{month}-{date}"
    end_date = f"{year_e}-{month_e}-{date_e}"

    #Lets make a query
    temp_query = session.query(func.min(Measurements.tobs).filter(Measurements.date >= start_date).filter(Measurements.date <= end_date).label("min_temp"), 
                            func.max(Measurements.tobs).filter(Measurements.date >= start_date).filter(Measurements.date <= end_date).label("max_temp"),
                            func.avg(Measurements.tobs).filter(Measurements.date >= start_date).filter(Measurements.date <= end_date).label("avg_temp"))

    session.close()

    res = temp_query.one()
    temperatures = {"max_temp" : res.max_temp, "min_temp" : res.min_temp, "avg_temp": res.avg_temp }

  

    return jsonify(temperatures)



if __name__ == '__main__':
    app.run(debug=True)

