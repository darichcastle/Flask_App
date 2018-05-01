from sqlalchemy import *
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
 
engine = create_engine('sqlite:///tutorial.db', echo=True)
Base = declarative_base()
 

class User(Base):
    """"""
    __tablename__ = "users"
 
    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)
    staterestore = Column(Integer)
    idleft=Column(Integer)
    name = Column(String)
 
    #----------------------------------------------------------------------
    def __init__(self, username, password, staterestore,idleft,first,last):
        """"""
        self.username = username
        self.password = password
        self.staterestore = staterestore
        self.idleft = idleft
        self.name = first + " " + last
 
# create tables
Base.metadata.create_all(engine)