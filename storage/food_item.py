from sqlalchemy import Column, Float, Integer, String, DateTime
from base import Base
import datetime


class FoodItem(Base):
    """ Food Item """

    __tablename__ = "food_item"

    id = Column(Integer, primary_key=True)
    food_id = Column(String(10), nullable=False)
    food_name = Column(String(250), nullable=False)
    calorie = Column(Integer, nullable=False)
    weight = Column(Float, nullable=True)
    trace_id = Column(String, nullable=False)
    date_created = Column(DateTime, nullable=False)


    def __init__(self, food_id, food_name, calorie, weight, trace_id):
        """ Initializes a food item """
        self.food_id = food_id
        self.food_name = food_name
        self.calorie = calorie
        self.weight = weight
        self.date_created = datetime.datetime.now() # Sets the date/time record is created
        self.trace_id = trace_id


    def to_dict(self):
        """ Dictionary Representation of a food item """
        dict = {}
        dict['food_id'] = self.food_id
        dict['food_name'] = self.food_name
        dict['calorie'] = self.calorie
        dict['weight'] = self.weight
        dict['date_created'] = self.date_created
        dict['trace_id'] = self.trace_id

        return dict
