import sqlite3 
 
conn = sqlite3.connect('stats.sqlite') 
 
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