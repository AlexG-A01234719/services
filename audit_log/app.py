import connexion
import swagger_ui_bundle
import pykafka
import yaml
import logging
import logging.config
import json

from pykafka import KafkaClient


with open('app_conf.yml', 'r') as f: 
    app_config = yaml.safe_load(f.read())
    
with open('log_conf.yml', 'r') as f: 
    log_config = yaml.safe_load(f.read()) 
    logging.config.dictConfig(log_config)

logger = logging.getLogger('basicLogger')


def get_food_item(index): 
    """ Get Food Item in History """ 
    hostname = "%s:%d" % (app_config["events"]["hostname"],  
                          app_config["events"]["port"]) 
    client = KafkaClient(hosts=hostname) 
    topic = client.topics[str.encode(app_config["events"]["topic"])] 
 
    # Here we reset the offset on start so that we retrieve 
    # messages at the beginning of the message queue.  
    # To prevent the for loop from blocking, we set the timeout to 
    # 100ms. There is a risk that this loop never stops if the 
    # index is large and messages are constantly being received! 
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
 
    # Here we reset the offset on start so that we retrieve 
    # messages at the beginning of the message queue.  
    # To prevent the for loop from blocking, we set the timeout to 
    # 100ms. There is a risk that this loop never stops if the 
    # index is large and messages are constantly being received! 
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
 
            # Find the event at the index you want and  
            # return code 200 
            # i.e., return event, 200 
            
        if index < len(drink_list):
            event = drink_list[index]
            logger.info(f"Found Drink Item at index {index} with Drink ID {event['drink_id']}")
            return event, 200
        
    except: 
        logger.error("No more messages found") 
     
    logger.error("Could not find Drink Item at index %d" % index) 
    return {"message": "Not Found"}, 404 


app = connexion.FlaskApp(__name__, specification_dir='')
app.add_api("openapi.yml", strict_validation=True, validate_responses=True)

if __name__ == "__main__":
    app.run(port=8110)