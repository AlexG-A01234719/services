from sqlalchemy import Column, Float, Integer, String, DateTime
from base import Base
import datetime


class DrinkItem(Base):
    """ Drink Item """

    __tablename__ = "drink_item"

    id = Column(Integer, primary_key=True)
    drink_id = Column(String(10), nullable=False)
    drink_name = Column(String(250), nullable=False)
    calorie = Column(Integer, nullable=False)
    volume = Column(Float, nullable=True)
    trace_id = Column(String, nullable=False)
    date_created = Column(DateTime, nullable=False)


    def __init__(self, drink_id, drink_name, calorie, volume, trace_id):
        """ Initializes a drink item """
        self.drink_id = drink_id
        self.drink_name = drink_name
        self.calorie = calorie
        self.volume = volume
        self.date_created = datetime.datetime.now() # Sets the date/time record is created
        self.trace_id = trace_id


    def to_dict(self):
        """ Dictionary Representation of a drink item """
        dict = {}
        dict['drink_id'] = self.drink_id
        dict['drink_name'] = self.drink_name
        dict['calorie'] = self.calorie
        dict['volume'] = self.volume
        dict['date_created'] = self.date_created
        dict['trace_id'] = self.trace_id

        return dict
