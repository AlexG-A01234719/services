from sqlalchemy import Column, Integer, String, DateTime 
from base import Base 
class Stats(Base): 
    """ Processing Statistics """ 
 
    __tablename__ = "stats" 
 
    id = Column(Integer, primary_key=True) 
    num_fi_entries = Column(Integer, nullable=False) 
    total_fi_calorie = Column(Integer, nullable=False) 
    num_di_entries = Column(Integer, nullable=True) 
    total_di_calorie = Column(Integer, nullable=True) 
    last_updated = Column(DateTime, nullable=False) 
 
    def __init__(self, num_fi_entries, total_fi_calorie, num_di_entries, total_di_calorie, last_updated): 
        """ Initializes a processing statistics objet """ 
        self.num_fi_entries = num_fi_entries 
        self.total_fi_calorie = total_fi_calorie 
        self.num_di_entries = num_di_entries 
        self.total_di_calorie = total_di_calorie 
        self.last_updated = last_updated 
 
    def to_dict(self): 
        """ Dictionary Representation of a statistics """ 
        dict = {} 
        dict['num_fi_entries'] = self.num_fi_entries 
        dict['total_fi_calorie'] = self.total_fi_calorie 
        dict['num_di_entries'] = self.num_di_entries 
        dict['total_di_calorie'] = self.total_di_calorie 
        dict['last_updated'] = self.last_updated.strftime("%Y-%m-%dT%H:%M:%S") 
 
        return dict