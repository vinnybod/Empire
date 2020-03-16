from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

engine = create_engine('sqlite:///data/empire.db', echo=True)

Session = scoped_session(sessionmaker(bind=engine))

Base = declarative_base()
Base.metadata.create_all(engine)
