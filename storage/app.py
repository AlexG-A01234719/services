import connexion
from connexion import NoContent
import datetime
import pymysql
import mysql.connector
import logging
import logging.config
import yaml
import uuid
import json

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from base import Base
from food_item import FoodItem
from drink_item import DrinkItem

from pykafka import KafkaClient
from pykafka.common import OffsetType
from threading import Thread 


with open('app_conf.yml', 'r') as f: 
    app_config = yaml.safe_load(f.read())
    
with open('log_conf.yml', 'r') as f: 
    log_config = yaml.safe_load(f.read()) 
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

DB_ENGINE = create_engine(f"mysql+pymysql://{app_config['datastore']['user']}:{app_config['datastore']['password']}@{app_config['datastore']['hostname']}:{app_config['datastore']['port']}/{app_config['datastore']['db']}")
Base.metadata.bind = DB_ENGINE
DB_SESSION = sessionmaker(bind=DB_ENGINE)

logger.info(f"Connected to DB. Hostname:{app_config['datastore']['hostname']}, Port:{app_config['datastore']['port']}")


def get_food_items(timestamp): 
    """ Gets new food item after the timestamp """ 
 
    session = DB_SESSION() 
 
    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ") 
   
 
    readings = session.query(FoodItem).filter(FoodItem.date_created >= timestamp_datetime) 
 
    results_list = [] 
 
    for reading in readings: 
        results_list.append(reading.to_dict()) 
 
    session.close() 
     
    logger.info("Query for Food Item readings after %s returns %d results" %  
                (timestamp, len(results_list))) 
 
    return results_list, 200

    
def get_drink_items(timestamp): 
    """ Gets new drink item after the timestamp """ 
 
    session = DB_SESSION() 
 
    timestamp_datetime = datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ") 
   
 
    readings = session.query(DrinkItem).filter(DrinkItem.date_created >= timestamp_datetime) 
 
    results_list = [] 
 
    for reading in readings: 
        results_list.append(reading.to_dict()) 
 
    session.close() 
     
    logger.info("Query for Drink Item readings after %s returns %d results" %  
                (timestamp, len(results_list))) 
 
    return results_list, 200
    

def process_messages(): 
    """ Process event messages """ 
    hostname = "%s:%d" % (app_config["events"]["hostname"],   
                          app_config["events"]["port"]) 
    client = KafkaClient(hosts=hostname) 
    topic = client.topics[str.encode(app_config["events"]["topic"])] 
     
    # Create a consume on a consumer group, that only reads new messages  
    # (uncommitted messages) when the service re-starts (i.e., it doesn't  
    # read all the old messages from the history in the message queue). 
    consumer = topic.get_simple_consumer(consumer_group=b'event_group', 
                                         reset_offset_on_start=False, 
                                         auto_offset_reset=OffsetType.LATEST) 
 
    # This is blocking - it will wait for a new message 
    for msg in consumer: 
        msg_str = msg.value.decode('utf-8') 
        msg = json.loads(msg_str) 
        logger.info("Message: %s" % msg) 
 
        payload = msg["payload"] 
                 
        if msg["type"] == "add_food": # Change this to your event type 
                session = DB_SESSION()
                
                bp = FoodItem(payload['food_id'],
                              payload['food_name'],
                              payload['calorie'],
                              payload['weight'],
                              payload['trace_id'])

                session.add(bp)

                session.commit()
                session.close()

                logger.debug(f"Received event add_food request with a trace id of {payload['trace_id']}")

            
        elif msg["type"] == "add_drink": # Change this to your event type 
                session = DB_SESSION()

                bp = DrinkItem(payload['drink_id'],
                               payload['drink_name'],
                               payload['calorie'],
                               payload['volume'],
                               payload['trace_id'])

                session.add(bp)

                session.commit()
                session.close()

                logger.debug(f"Received event add_drink request with a trace id of {payload['trace_id']}")

 
        # Commit the new message as being read 
        consumer.commit_offsets()
        
    
app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    t1 = Thread(target=process_messages) 
    t1.setDaemon(True) 
    t1.start()
    app.run(port=8090)