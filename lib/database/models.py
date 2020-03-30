import time

from sqlalchemy import Column, Integer, Sequence, String, Boolean, BLOB, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    username = Column(String(50), nullable=False)
    password = Column(String(255), nullable=False)
    api_token = Column(String(50))
    last_logon_time = Column(String(50))  # DateTime
    enabled = Column(Boolean, nullable=False)
    admin = Column(Boolean, nullable=False)

    def __repr__(self):
        return "<User(username='%s')>" % (
            self.username)


class Listener(Base):
    __tablename__ = 'listeners'
    id = Column(Integer, Sequence("listener_id_seq"), primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    module = Column(String(255), nullable=False)
    listener_type = Column(String(255), nullable=False)
    listener_category = Column(String(255), nullable=False)
    enabled = Column(Boolean, nullable=False)
    options = Column(BLOB, nullable=True)

    def __repr__(self):
        return "<Listener(name='%s')>" % (
            self.name)


class Agent(Base):
    __tablename__ = 'agents'
    id = Column(Integer, Sequence("agent_id_seq"), primary_key=True)
    name = Column(String(255), nullable=False)
    listener = Column(String(255), nullable=False) # join?
    session_id = Column(String(255), nullable=True)
    language = Column(String(255), nullable=True)
    language_version = Column(String(255), nullable=True)
    delay = Column(Integer) #todo min value?
    jitter = Column(Integer) #todo wtf is real
    external_ip = Column(String(255), nullable=True)
    internal_ip = Column(String(255), nullable=True)
    username = Column(String(255), nullable=True)
    high_integrity = Column(Integer) #min value?
    process_name = Column(String(255), nullable=True)
    process_id = Column(String(255), nullable=True)
    hostname = Column(String(255), nullable=True)
    os_details = Column(String(255), nullable=True)
    session_key = Column(String(255), nullable=True)
    nonce = Column(String(255), nullable=True)
    checkin_time = Column(String(255), nullable=True)
    lastseen_time = Column(String(255), nullable=True)
    parent = Column(String(255), nullable=True) #join?
    children = Column(String(255), nullable=True) #join?
    servers = Column(String(255), nullable=True)
    profile = Column(String(255), nullable=True)
    functions = Column(String(255), nullable=True)
    kill_date = Column(String(255), nullable=True)
    working_hours = Column(String(255), nullable=True)
    lost_limit = Column(Integer)
    taskings = relationship("Tasking")
    results = relationship("Result")

    @hybrid_property
    def stale(self):
        interval_max = (self.delay + self.delay * self.jitter) + 30
        agent_time = time.mktime(time.strptime(self.lastseen_time, "%Y-%m-%d %H:%M:%S"))
        stale = agent_time < time.mktime(time.localtime()) - interval_max

        return stale

    def __repr__(self):
        return "<Agent(name='%s')>" % (
            self.name)


class Config(Base):
    __tablename__ = 'config'
    staging_key = Column(String(255), nullable=False, primary_key=True)  # TODO Revisit max length
    install_path = Column(String(255), nullable=False)
    ip_whitelist = Column(String(255), nullable=False)
    ip_blacklist = Column(String(255), nullable=False)
    autorun_command = Column(String(255), nullable=False)
    autorun_data = Column(String(255), nullable=False)
    rootuser = Boolean()
    obfuscate = Column(Integer, nullable=False)
    obfuscate_command = Column(String(255), nullable=False)

    def __repr__(self):
        return "<Config(staging_key='%s')>" % (
            self.staging_key)


class Credential(Base):
    __tablename__ = 'credentials'
    id = Column(Integer, Sequence("credential_id_seq"), primary_key=True)
    credtype = Column(String(255), nullable=True)
    domain = Column(String(255), nullable=True)
    username = Column(String(255), nullable=True)
    password = Column(String(255), nullable=True)
    host = Column(String(255), nullable=True)
    os = Column(String(255), nullable=True)
    sid = Column(String(255), nullable=True)
    notes = Column(String(255), nullable=True)

    def __repr__(self):
        return "<Credential(id='%s')>" % (
            self.id)


class Tasking(Base):
    __tablename__ = 'taskings'
    id = Column(Integer, Sequence("tasking_id_seq"), primary_key=True)
    agent = Column(String(255), ForeignKey('agents.id'), primary_key=True)
    data = Column(String, nullable=True)
    user_id = Column(String(255), ForeignKey('users.id'), nullable=True)
    time_stamp = Column(String(255))  # TODO Dates?

    def __repr__(self):
        return "<Tasking(id='%s')>" % (
            self.id)


class Result(Base):
    __tablename__ = 'results'
    id = Column(Integer, Sequence("result_id_seq"), primary_key=True)
    agent = Column(String(255), ForeignKey('agents.id'), primary_key=True)
    data = Column(String, nullable=True)
    user_id = Column(String(255))

    def __repr__(self):
        return "<Result(id='%s')>" % (
            self.id)


class Reporting(Base):
    __tablename__ = 'reporting'
    id = Column(Integer, Sequence("reporting_id_seq"), primary_key=True)
    name = Column(String, nullable=False)
    event_type = Column(String)
    message = Column(String)
    time_stamp = Column(String)
    taskID = Column(Integer, ForeignKey('results.id'))  # Should be task_id. might be result.id

    def __repr__(self):
        return "<Reporting(id='%s')>" % (
            self.id)


# TODO there's probably a better way to lay this one out
class Function(Base):
    __tablename__ = "functions"
    id = Column(Integer, Sequence("functions_id_seq"), primary_key=True)
    Invoke_Empire = Column(String)
    Invoke_Mimikatz = Column(String)

    def __repr__(self):
        return "<Function(id='%s')>" % (
            self.id)
