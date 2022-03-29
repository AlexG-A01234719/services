import connexion
import swagger_ui_bundle
import pykafka
import yaml
import logging
import logging.config
import json
import os

from flask_cors import CORS, cross_origin
from pykafka import KafkaClient


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


def get_food_item(index): 
    """ Get Food Item in History """ 
    hostname = "%s:%d" % (app_config["events"]["hostname"],  
                          app_config["events"]["port"]) 
    client = KafkaClient(hosts=hostname) 
    topic = client.topics[str.encode(app_config["events"]["topic"])] 
 
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,  
                                         consumer_timeout_ms=1000) 
 
    logger.info("Retrieving Food Item at index %d" % index) 
    try: 
        food_list = []
        for msg in consumer: 
            msg_str = msg.value.decode('utf-8') 
            msg = json.loads(msg_str) 
            
            if msg['type'] == "add_food":
                food_list.append(msg['payload'])
 
            # Find the event at the index you want and  
            # return code 200 
            # i.e., return event, 200 
                       
        if index < len(food_list):
            event = food_list[index]
            logger.info(f"Found Food Item at index {index} with Food ID {event['food_id']}")
            return event, 200
        
    except: 
        logger.error("No more messages found") 
     
    logger.error("Could not find Food Item at index %d" % index) 
    return { "message": "Not Found"}, 404 


def get_drink_item(index): 
    """ Get Drink Item in History """ 
    hostname = "%s:%d" % (app_config["events"]["hostname"],  
                          app_config["events"]["port"]) 
    client = KafkaClient(hosts=hostname) 
    topic = client.topics[str.encode(app_config["events"]["topic"])] 
 
    consumer = topic.get_simple_consumer(reset_offset_on_start=True,  
                                         consumer_timeout_ms=1000) 
 
    logger.info("Retrieving Drink Item at index %d" % index) 
    try:
        drink_list = []
        for msg in consumer: 
            msg_str = msg.value.decode('utf-8') 
            msg = json.loads(msg_str) 
            
            if msg['type'] == "add_drink":
                drink_list.append(msg['payload'])
 
        if index < len(drink_list):
            event = drink_list[index]
            logger.info(f"Found Drink Item at index {index} with Drink ID {event['drink_id']}")
            return event, 200
        
    except: 
        logger.error("No more messages found") 
     
    logger.error("Could not find Drink Item at index %d" % index) 
    return {"message": "Not Found"}, 404 


app = connexion.FlaskApp(__name__, specification_dir='')
CORS(app.app)
if "TARGET_ENV" not in os.environ or os.environ["TARGET_ENV"] != "test":
    CORS(app.app)
    app.app.config['CORS_HEADERS'] = 'Content-Type'
app.add_api("openapi.yml", base_path="/audit_log", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8110)