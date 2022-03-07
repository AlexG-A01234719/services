import mysql.connector 
 
db_conn = mysql.connector.connect(host="localhost", user="root", password="r00tpassw0rd", database="events", auth_plugin='mysql_native_password') 
 
db_cursor = db_conn.cursor() 

db_cursor.execute(''' 
                  DROP TABLE food_item, drink_item 
                  ''') 
 
db_conn.commit() 
db_conn.close()