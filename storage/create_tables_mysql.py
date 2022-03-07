import mysql.connector
import yaml

with open('app_conf.yml', 'r') as f: 
    app_config = yaml.safe_load(f.read())
 
db_conn = mysql.connector.connect(host=app_config['datastore']['hostname'], user=app_config['datastore']['user'], password=app_config['datastore']['password'], database=app_config['datastore']['db'], auth_plugin='mysql_native_password')

c = db_conn.cursor()
c.execute('''
          CREATE TABLE food_item
          (id INT NOT NULL AUTO_INCREMENT,
           food_id VARCHAR(10) NOT NULL, 
           food_name VARCHAR(250) NOT NULL,
           calorie INTEGER NOT NULL,
           weight FLOAT,
           date_created VARCHAR(100) NOT NULL,
           trace_id VARCHAR(100) NOT NULL,
           CONSTRAINT food_item_pk PRIMARY KEY (id))
          ''')

c.execute('''
          CREATE TABLE drink_item
          (id INT NOT NULL AUTO_INCREMENT,
           drink_id VARCHAR(10) NOT NULL, 
           drink_name VARCHAR(250) NOT NULL,
           calorie INTEGER NOT NULL,
           volume FLOAT,
           date_created VARCHAR(100) NOT NULL,
           trace_id VARCHAR(100) NOT NULL,
           CONSTRAINT drink_item_pk PRIMARY KEY (id))
          ''')

db_conn.commit()
db_conn.close()
