import connexion
from connexion import NoContent
import datetime
import json
import requests
import yaml
import logging
import logging.config
import uuid
import time

from pykafka import KafkaClient

url = 'http://localhost:8090'

with open('app_conf.yml', 'r') as f: 
    app_config = yaml.safe_load(f.read())
    
with open('log_conf.yml', 'r') as f: 
    log_config = yaml.safe_load(f.read()) 
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')

while current_retry < app_config["events"]["max_retries"]:
    try:
        hostname = "%s:%d" % (app_config["events"]["hostname"],   
                            app_config["events"]["port"]) 
        client = KafkaClient(hosts=hostname)
        topic = client.topics[str.encode(app_config["events"]["topic"])]
        current_retry = app_config["events"]["max_retries"]
    except:
        logger.error("Connection to Kafka failed!")
        time.sleep(app_config["events"]["sleep"])
        current_retry += 1


def add_food(body):
    """ Adds a food item """
    producer = topic.get_sync_producer() 
    trace_id = str(uuid.uuid1())
    body['trace_id'] = trace_id
    msg = { "type": "add_food",  
            "datetime" :    
            datetime.datetime.now().strftime( 
                "%Y-%m-%dT%H:%M:%S"),  
            "payload": body } 
    msg_str = json.dumps(msg) 
    producer.produce(msg_str.encode('utf-8')) 
    
    logger.info(f"Food item added with {trace_id}")
    
    return NoContent, 201

    
def add_drink(body):
    """ Adds a drink item """
    client = KafkaClient(hosts=f"{app_config['events']['hostname']}:{app_config['events']['port']}") 
    topic = client.topics[str.encode(app_config['events']['topic'])] 
    producer = topic.get_sync_producer() 
    trace_id = str(uuid.uuid1())
    body['trace_id'] = trace_id
    msg = { "type": "add_drink",  
            "datetime" :    
            datetime.datetime.now().strftime( 
                "%Y-%m-%dT%H:%M:%S"),  
            "payload": body } 
    msg_str = json.dumps(msg) 
    producer.produce(msg_str.encode('utf-8'))
    
    logger.info(f"Drink item added with {trace_id}")

    
    return NoContent, 201


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8080)