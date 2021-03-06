import connexion
from connexion import NoContent
import datetime
import requests
import yaml
import logging
import logging.config
import uuid
import os

from flask_cors import CORS, cross_origin
from base import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from stats import Stats
from apscheduler.schedulers.background import BackgroundScheduler


url = 'http://localhost:8100'

if "TARGET_ENV" in os.environ and os.environ["TARGET_ENV"] == "test":
    print("In Test Environment")
    app_conf_file = "/config/app_conf.yml"
    log_conf_file = "/config/log_conf.yml"
else:
    print("In Dev Environment")
    app_conf_file = "app_conf.yml"
    log_conf_file = "log_conf.yml"
    
with open(app_conf_file, 'r') as f:
    app_config = yaml.safe_load(f.read())
    
# External Logging Configuration
with open(log_conf_file, 'r') as f:
    log_config = yaml.safe_load(f.read())
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

logger.info("App Conf File: %s" % app_conf_file)
logger.info("Log Conf File: %s" % log_conf_file)

DB_ENGINE = create_engine("sqlite:///%s" % app_config["datastore"]["filename"]) 
Base.metadata.bind = DB_ENGINE 
DB_SESSION = sessionmaker(bind=DB_ENGINE) 


import sqlite3 

if not os.path.exists(app_config["datastore"]["filename"]):
    conn = sqlite3.connect(app_config["datastore"]["filename"]) 
    
    c = conn.cursor() 
    c.execute(''' 
            CREATE TABLE stats 
            (id INTEGER PRIMARY KEY ASC,  
            num_fi_entries INTEGER, 
            total_fi_calorie INTEGER, 
            num_di_entries INTEGER, 
            total_di_calorie INTEGER, 
            last_updated VARCHAR(100) NOT NULL) 
            ''') 

    c.execute("""
            INSERT INTO stats(
            num_fi_entries,
            total_fi_calorie,
            num_di_entries,
            total_di_calorie,
            last_updated)
            VALUES(0,0,0,0, '1000-01-01 01:00:00');
            """)

    conn.commit() 
    conn.close() 


def populate_stats():
    """ Periodically updates stats """

    logger.info("periodic processing started")
    timestamp_now = datetime.datetime.now()
    timestamp_now_str = timestamp_now.strftime("%Y-%m-%dT%H:%M:%S")
    
    session = DB_SESSION() 

    results = session.query(Stats).order_by(Stats.last_updated.desc())
    
    results_list = [] 
    
    if results:
        for reading in results: 
            results_list.append(reading.to_dict()) 
    
    session.close()
    
    timestamp_updated = results_list[0]['last_updated']
    total_fi_calorie = results_list[0]['total_fi_calorie']
    total_di_calorie = results_list[0]['total_di_calorie']
    num_fi_entries = results_list[0]['num_fi_entries']
    num_di_entries = results_list[0]['num_di_entries']
    
    food_url = f"{app_config['eventstore']['url']}/food?start_timestamp={timestamp_updated}&end_timestamp={timestamp_now_str}"
    drink_url = f"{app_config['eventstore']['url']}/drink?start_timestamp={timestamp_updated}&end_timestamp={timestamp_now_str}"
    
    print(food_url)
    food_response = requests.get(food_url)
    food_data = food_response.json()
    if food_response.status_code != 200:
        logger.error("Food bad >:(")
    print(food_data)
    logger.info("Query for Food Item readings after %s returns %d results" % (timestamp_now, len(food_data))) 

    print(drink_url)
    drink_response = requests.get(drink_url)
    drink_data = drink_response.json()
    if drink_response.status_code != 200:
        logger.error("Drink bad >:(")
    print(drink_data)
    logger.info("Query for Drink Item readings after %s returns %d results" % (timestamp_now, len(drink_data))) 

    for item in food_data:
        logger.debug(f"event processed for Food Item with trace_id: {item['trace_id']}")
        total_fi_calorie += item['calorie']
    num_fi_entries += len(food_data)
        

    for item in drink_data:
        logger.debug(f"event processed for Drink Item with trace_id: {item['trace_id']}")
        total_di_calorie += item['calorie']
    num_di_entries += len(drink_data)
    
    session = DB_SESSION()

    bp = Stats(num_fi_entries,
               total_fi_calorie,
               num_di_entries,
               total_di_calorie,
               timestamp_now)
    
    session.add(bp)
    session.commit()
    session.close()

    logger.debug(f"Statistics updated: {num_fi_entries} Food Item entries, {total_fi_calorie} food calories, "
                 f"{num_di_entries} Drink Item entries, {total_di_calorie} drink calories, update time {timestamp_now}")
     
    logger.info("periodic processing ended") 
 
    return results_list, 200


def get_stats(): 
    """ Gets new food item after the timestamp """ 
    
    logger.info("request for statistics received")
 
    session = DB_SESSION() 

    results = session.query(Stats).order_by(Stats.last_updated.desc()) 
    
    results_list = [] 
    
    if results:
        for reading in results: 
            results_list.append(reading.to_dict()) 
    
    session.close()
    
    newest_list = results_list[0]
    logger.debug(f"Statistics contents{newest_list}")
    logger.info("statistics request has been fulfilled")
    
    return newest_list, 200 


def init_scheduler(): 
    sched = BackgroundScheduler(daemon=True) 
    sched.add_job(populate_stats,    
                  'interval', 
                  seconds=app_config['scheduler']['period_sec']) 
    sched.start()
    
    
app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yml", base_path="/processing", strict_validation=True, validate_responses=True)

if __name__ == "__main__": 
    # run our standalone gevent server 
    init_scheduler() 
    app.run(port=8100, use_reloader=False)