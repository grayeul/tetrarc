#!/usr/bin/env python3
# @file:  tetrarcDB.py
# @brief: Interface to sqlite db (for now) - for tetrarc (TEst TRAcking for Rocky Candidates)
import logging
import sqlite3
import time
import os
import re
import sys
from datetime import datetime,timezone,timedelta
import pdb
import json
import bcrypt
import uuid
import traceback
from sqlalchemy import create_engine, ForeignKey, UniqueConstraint, func
from sqlalchemy import Integer, Float, String, Column, Date,DateTime, JSON, CheckConstraint
from sqlalchemy import select, update, delete
from sqlalchemy.orm import Mapped, relationship, DeclarativeBase, mapped_column
from sqlalchemy import __version__ as sqlalchemyVers
if sqlalchemyVers[0] != '2':
    print("This code requires sqlalchemy v2 or greater")
    raise SystemExit
from sqlalchemy.orm import declarative_base
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship,sessionmaker,column_property
from sqlalchemy.ext.hybrid import hybrid_property
from collections import OrderedDict

_gArchList=['x86_64','aarch64','ppc64le','s390x']
_gStatusList=['pass','fail','partial']
# Define the key sqlalchemy classes for use with the tables defined in the README.

#Base = declarative_base()
class Base(DeclarativeBase):
    pass

#################################################################
def getNewAuthToken() -> str:
    "Gets a stringified UUID as a default new token"
    return str(uuid.uuid4())

#################################################################
class Users(Base):
    __tablename__='users'
    __table_args__=(UniqueConstraint('username',name='uniqUsername'),
                    UniqueConstraint('email',name='uniqEmail'),)
    fields='id,username,name,email,created,pending_approval,password,last_login,disabled'
    field_list=fields.split(',')
    id:         Mapped[int] = mapped_column(primary_key=True)
    username:   Mapped[str] = mapped_column(nullable=False,index=True)
    name:       Mapped[str] = mapped_column(nullable=False)
    email:      Mapped[str] = mapped_column(nullable=False)
    created:    Mapped[datetime] = mapped_column(default=func.now())
    pending_approval: Mapped[int] = mapped_column(default=1)
    password:   Mapped[str] = mapped_column(nullable=True,default=None)
    last_login: Mapped[datetime] = mapped_column(nullable=True,default=None)
    disabled:   Mapped[int] = mapped_column(default=0)
    def merge_from(self,other):
        for k in self.field_list:
           setattr(self,k,getattr(other,k))
    def toDict(self):
        rval={}
        for k in self.field_list:
            rval[k]=getattr(self,k)
        return rval
#################################################################
class UserSessions(Base):
    __tablename__='user_sessions'
    __table_args__=(UniqueConstraint('user_id',name='uniqUserId'),
                    UniqueConstraint('auth_token',name='uniqAuthToken'))
    fields='id,auth_token,user_id,created,valid_until'
    field_list=fields.split(',')
    id:         Mapped[int] = mapped_column(primary_key=True)
    auth_token: Mapped[str] = mapped_column(default=getNewAuthToken)
    user_id:    Mapped[int] = mapped_column(ForeignKey('users.id'),nullable=False)
    created:    Mapped[datetime] = mapped_column(default=func.now())
    valid_until:Mapped[datetime] = mapped_column(default=func.now())

    def merge_from(self,other):
        for k in self.field_list:
           setattr(self,k,getattr(other,k))
    def toDict(self):
        rval={}
        for k in self.field_list:
            rval[k]=getattr(self,k)
        return rval

#################################################################
class Roles(Base):
    __tablename__='roles'
    __table_args__=(UniqueConstraint('name',name='uniqName'),)
    fields='id,name,description'
    field_list=fields.split(',')
    id:         Mapped[int] = mapped_column(primary_key=True)
    name:       Mapped[str] = mapped_column(nullable=False)
    description:Mapped[str] = mapped_column(nullable=False)

    def merge_from(self,other):
        for k in self.field_list:
           setattr(self,k,getattr(other,k))
    def toDict(self):
        rval={}
        for k in self.field_list:
            rval[k]=getattr(self,k)
        return rval

#################################################################
class UserRoles(Base):
    __tablename__='user_roles'
    __table_args__=(UniqueConstraint('user_id','role_id',name='uniqPair'),)
    fields='id,user_id,role_id'
    field_list=fields.split(',')
    id:         Mapped[int] = mapped_column(primary_key=True)
    user_id:    Mapped[int] = mapped_column(ForeignKey('users.id'),nullable=False)
    role_id:    Mapped[int] = mapped_column(ForeignKey('roles.id'),nullable=False)

    def merge_from(self,other):
        for k in self.field_list:
           setattr(self,k,getattr(other,k))
    def toDict(self):
        rval={}
        for k in self.field_list:
            rval[k]=getattr(self,k)
        return rval
#################################################################
class BasicTests(Base):
    __tablename__='basic_tests'
    __table_args__=(UniqueConstraint('name',name='uniqName'),UniqueConstraint('shortname',name='uniqShortName'),)
    fields='id,name,shortname,test_group_id,testorder,description,created,created_by,'
    fields+='last_modified,last_modified_by,link_to_procedure,notes'
    field_list=fields.split(',')
    id:               Mapped[int] = mapped_column(primary_key=True)
    name:             Mapped[str] = mapped_column(nullable=False,index=True)
    shortname:        Mapped[str] = mapped_column(nullable=False,index=True)
    test_group_id:   Mapped[int] = mapped_column(ForeignKey('test_groups.id'),nullable=False)
    testorder:        Mapped[int] = mapped_column(default=0,nullable=False)
    description:      Mapped[str] = mapped_column(nullable=False)
    created:          Mapped[datetime] = mapped_column(default=func.now())
    created_by:       Mapped[int] = mapped_column(ForeignKey('users.id'),nullable=False)
    last_modified:    Mapped[datetime] = mapped_column(default=func.now())
    last_modified_by: Mapped[int] = mapped_column(ForeignKey('users.id'),nullable=False)
    link_to_procedure:Mapped[str] = mapped_column(default=None,nullable=True)
    notes:            Mapped[str] = mapped_column(default=None,nullable=True)

    def merge_from(self,other):
        for k in self.field_list:
           setattr(self,k,getattr(other,k))
    def toDict(self):
        rval={}
        for k in self.field_list:
            rval[k]=getattr(self,k)
        return rval

#################################################################
class TestGroups(Base):
    __tablename__='test_groups'
    __table_args__=(UniqueConstraint('name',name='uniqName'),)
    fields='id,num,name,description,notes'
    field_list=fields.split(',')
    id:         Mapped[int]       = mapped_column(primary_key=True)
    num:        Mapped[int]       = mapped_column(nullable=False)   # For sorting
    name:       Mapped[str]       = mapped_column(nullable=False)
    description:Mapped[str]       = mapped_column(nullable=False)
    notes:      Mapped[str]       = mapped_column(default=None,nullable=True)

    def merge_from(self,other):
        for k in self.field_list:
           setattr(self,k,getattr(other,k))
    def toDict(self):
        rval={}
        for k in self.field_list:
            rval[k]=getattr(self,k)
        return rval

#################################################################
class TestTypes(Base):
    __tablename__='test_types'
    fields='id,basic_test_id,arch,test_environ,claimant_id,notes'
    field_list=fields.split(',')
    id:             Mapped[int] = mapped_column(primary_key=True)
    basic_test_id: Mapped[int] = mapped_column(ForeignKey('basic_tests.id'),nullable=False)
    arch:           Mapped[str] = mapped_column(nullable=False)
    test_environ:   Mapped[str] = mapped_column(nullable=False)
    claimant_id:    Mapped[int] = mapped_column(ForeignKey('users.id'),nullable=True)
    notes:          Mapped[str] = mapped_column(default=None,nullable=True)
    #__table_args__=(UniqueConstraint('num',name='uniqNum'),UniqueConstraint('name',name='uniqName'),
    #                CheckConstraint(arch.in_(_gArchList),name='arch_check'))

    def merge_from(self,other):
        for k in self.field_list:
           setattr(self,k,getattr(other,k))
    def toDict(self):
        rval={}
        for k in self.field_list:
            rval[k]=getattr(self,k)
        return rval

#################################################################
class TestResults(Base):
    __tablename__='test_results'
    fields='id,test_type_id,user_id,status,submitted,comments'
    field_list=fields.split(',')
    id:              Mapped[int] = mapped_column(primary_key=True)
    test_type_id:   Mapped[int] = mapped_column(ForeignKey('test_types.id'),nullable=False)
    user_id:         Mapped[int] = mapped_column(ForeignKey('users.id'),nullable=False)
    status:          Mapped[str]  = mapped_column(nullable=False,index=True)
    submitted:       Mapped[datetime] = mapped_column(default=func.now(),index=True)
    comments:        Mapped[str]  = mapped_column(nullable=True)
    # Note that unfortunately, sqlite won't detect unique constraint violation if any of these fields are NULL :(
    __table_args__=(UniqueConstraint('test_type_id','user_id','submitted',name='uniqResults'),
                    CheckConstraint(status.in_(_gStatusList),name='status_check'))

    def merge_from(self,other):
        for k in self.field_list:
           setattr(self,k,getattr(other,k))
    def toDict(self):
        rval={}
        for k in self.field_list:
            rval[k]=getattr(self,k)
        return rval
#################################################################
class TestBooks(Base):
    __tablename__='test_books'
    __table_args__=(UniqueConstraint('name',name='uniqName'),)
    fields='id,name,start_date,target_end_date,status,description'
    field_list=fields.split(',')
    id:              Mapped[int] = mapped_column(primary_key=True)
    name:            Mapped[str] = mapped_column(nullable=False,index=True)
    start_date:      Mapped[datetime] = mapped_column(default=func.now())
    target_end_date: Mapped[datetime] = mapped_column(nullable=True)
    status:          Mapped[str] = mapped_column(nullable=False)
    description:     Mapped[str] = mapped_column(nullable=False)
    def merge_from(self,other):
        for k in self.field_list:
           setattr(self,k,getattr(other,k))
    def toDict(self):
        rval={}
        for k in self.field_list:
            rval[k]=getattr(self,k)
        return rval
#################################################################
class tetrarcDB:
    def __init__(self,dbfile=None,cfg={}):
        self.dbfile=dbfile
        self.cfg=cfg
        self.conn=None
        self.log=logging.getLogger("tetrarcdb")
        self.log.setLevel(self.cfg.get("loglevel","INFO"))
        try:
            conn_string = f'sqlite:///{self.dbfile}?charset=utf8'
            self.engine = create_engine(conn_string)
        except:
            self.log.exception(f"Exception trying to connect to {self.dbfile}",exc_info=True)

        # Enable foreign_key checking and WAL mode
        from sqlalchemy import event
        @event.listens_for(self.engine, 'connect')
        def set_foreign_keys(dbapi_connection, connection_record):
            dbapi_connection.execute('PRAGMA foreign_keys=ON;')
            dbapi_connection.execute('PRAGMA journal_mode=WAL;')

        Base.metadata.create_all(self.engine)
        self.roleLookup=self.getRolesByUserId()
    def getTableData(self,infotype:str) -> dict:
        #self.log.info(f"Dumping {infotype} data:")
        dbclass= eval(infotype[0].upper()+infotype[1:])
        Session=sessionmaker()
        Session.configure(bind=self.engine)
        rval={}
        with Session() as sess:
            try:
                s1=sess.query(dbclass).all()
                olist=[s.toDict() for s in s1]
                return olist
            except:
                self.log.exception("Exception getting classes",exc_info=True)
        return rval
    def getTableInstanceStmt(self,table_name:str) -> str:
        """
        This function takes a table_name arg, and returns a python object definition to be used in ingestData()
        Example:  for table_name='users'  -- return  'Users(username=item[0])'  which can be eval'ed by calling function
        """
        table_name=table_name.lower()
        if table_name == 'users':
            return 'Users(username=item[0],name=item[1],email=item[2])'
        if table_name == 'roles':
            return 'Roles(name=item[0],description=item[1])'
        if table_name == 'test_books':
            return 'TestBooks(name=item[0],start_date=datetime.strptime(item[1],"%Y-%m-%d"),target_end_date=datetime.strptime(item[2],"%Y-%m-%d"),status=item[3],description=item[4])'
        if table_name == 'test_groups':
            return 'TestGroups(name=item[0],num=1,description=item[1])'
        if table_name == 'test_types':
            return 'TestTypes(basic_test_id=int(item[0]),arch=item[1],test_environ=item[3])'
        if table_name == 'basic_tests':
            rval='BasicTests(name=item[0],shortname=item[1],test_group_id=item[2],'
            rval+= 'testorder=item[3],description=item[4],created_by=1,last_modified_by=1,'
            rval+= 'link_to_procedure=item[5])'
            return rval
        return "Not a valid table (yet)"
    def ingestTabData(self,tabdata:list,table_name:str) -> int:
        "Input is a list of tabdata, each item having a set of fields for the specified table_name. Returns a count of ingested records"
        dbbatch=[]
        for item in tabdata:
             if len(item)>2 and item[2] == 'None':
                 item[2]=None
             instInfo=self.getTableInstanceStmt(table_name)
             try:
                 instValue=eval(instInfo)
                 dbbatch.append(instValue)
             except:
                 self.log.exception(f"Got an exception with {instInfo}, ignoring this line")
        Session=sessionmaker()
        Session.configure(bind=self.engine)
        rval=0
        with Session() as sess:
            for x in dbbatch:
                sess.add(x)
                self.log.debug(f"Adding {x}")
                rval+=1
            try:
               sess.commit()
            except sqlite3.IntegrityError:
                self.log.exception("Duplicate Entry ignored")
        return rval
    def getRolesByUserId(self) -> dict:
        " Return a dictionary keyed by user_id"
        return {}
        data=self.getTableData("user_roles")
        Session=sessionmaker()
        Session.configure(bind=self.engine)
        rval={}
        with Session() as sess:
            try:
                s1=sess.execute(select(UserRoles,Users,Roles).where(
                    UserRoles.user_id==Users.id)).all()
                qlist=[(s[0].toDict(),s[1],s[2]) for s in s1]
            except:
                self.log.exception(f"Got an exception in getRolesByUserId()")
        rval={}
        for ld in data:
            num=ld['num']
            rval[num]=ld
        return rval

    def addUser(self,userInfo:dict) -> int:
        "Takes userInfo dict and inserts into users table, returning stored id"
        Session=sessionmaker()
        Session.configure(bind=self.engine)
        rval=0
        # Generate the password hash
        raw_pw=userInfo["raw_password"]
        pwhash=bcrypt.hashpw(raw_pw.encode('latin1'),bcrypt.gensalt(rounds=15))
        with Session() as sess:
            user=Users(username=userInfo["username"],
                   name=userInfo["name"],
                   email=userInfo["email"],
                   password=pwhash)

            sess.add(user)
            try:
                sess.commit()
                rval=user.id
            except:
                self.log.exception("Exception adding new user")
        return rval
    def getUserRolesById(self,user_id:int) -> list[str]:
        "Looks up a user by id, and returns a list of roles that user has"
        Session=sessionmaker()
        Session.configure(bind=self.engine)
        rval=[]
        with Session() as sess:
            stmt= select(Roles.name).select_from(Roles).join(
                   UserRoles,Roles.id == UserRoles.role_id).where(
                       UserRoles.user_id==user_id)
            s1=sess.execute(stmt ).all()
            if s1 and len(s1) > 0:
                rval=[x[0] for x in s1]
        return rval
    def getUserByUsername(self,username:str) -> dict:
        "Looks up a user by username, and returns the dict for that user"
        Session=sessionmaker()
        Session.configure(bind=self.engine)
        rval=None
        with Session() as sess:
            s1=sess.execute(select(Users).where(Users.username==username)).first()
            if s1 and len(s1) == 1:
                rval=s1[0].toDict()
        return rval
    def getUserById(self,id:int) -> dict:
        "Looks up a user by db id, and returns the dict for that user"
        Session=sessionmaker()
        Session.configure(bind=self.engine)
        rval=None
        with Session() as sess:
            s1=sess.execute(select(Users).where(Users.id==id)).first()
            if s1 and len(s1) == 1:
                rval=s1[0].toDict()
        return rval

    def newUserSession(self,user_id:int) -> dict:
        "Create a new session for the given user_id, and return sess info as a dict"
        Session=sessionmaker()
        Session.configure(bind=self.engine)
        rval=None
        now = datetime.now(tz=timezone.utc)
        with Session() as sess:
            user_sess=UserSessions(user_id=user_id,
                   created=now,
                   valid_until=now + timedelta(days=1)
                   )

            sess.add(user_sess)
            try:
                sess.commit()
                rval=user_sess.toDict()
            except:
                self.log.exception("Exception creating new session")
        return rval

    def updateUserSession(self,sess_id:int,new_valid_until:datetime) -> None:
        "Update session with the given id with the new valid_until"
        Session=sessionmaker()
        Session.configure(bind=self.engine)
        rval=None
        with Session() as sess:
            sess.execute(update(UserSessions)
                .where(UserSessions.id == sess_id)
                .values(valid_until = new_valid_until)
                )
            try:
                sess.commit()
            except:
                self.log.exception("Exception updating session")
        return rval

    def getUserSessionByAuthToken(self,auth_token:str) -> dict|None:
        "Looks up a session by auth_token, and returns the dict for that user, or None"
        Session=sessionmaker()
        Session.configure(bind=self.engine)
        rval=None
        with Session() as sess:
            s1=sess.execute(select(UserSessions).where(UserSessions.auth_token==auth_token)).first()
            if s1 and len(s1) == 1:
                rval=s1[0].toDict()
                # Put timezone at UTC
                rval['valid_until']=rval['valid_until'].replace(tzinfo=timezone.utc)
        return rval

    def deleteUserSessionByAuthToken(self,auth_token:str) -> None:
        "Looks up a session by auth_token, deletes it if it exists"
        Session=sessionmaker()
        Session.configure(bind=self.engine)
        rval=None
        self.log.info(f"Trying to delete user session: {auth_token}")
        with Session() as sess:
            sess.execute(delete(UserSessions).where(UserSessions.auth_token==auth_token))
            sess.commit()
        return rval

    def deleteUserSessionsByUserId(self,user_id:int) -> None:
        "Clears all sessions associated with given user_id"
        Session=sessionmaker()
        Session.configure(bind=self.engine)
        rval=None
        self.log.info(f"Trying to delete user {user_id} sessions")
        with Session() as sess:
            sess.execute(delete(UserSessions).where(UserSessions.user_id==user_id))
            sess.commit()
        return rval

    def getAllTableEntries(self,TableName:str) -> list[str]:
        Session=sessionmaker()
        Session.configure(bind=self.engine)
        rval=None
        self.log.info(f"Trying to get All {TableName} entries")
        with Session() as sess:
            s1=eval(f"sess.query({TableName}).all()")
            if s1:
               rval=[x.toDict() for x in s1]
        return rval
    def getTestBooks(self) -> list[str]:
        return self.getAllTableEntries('TestBooks')
    def getTestGroups(self) -> list[str]:
        return self.getAllTableEntries('TestGroups')
    def getBasicTests(self) -> list[str]:
        return self.getAllTableEntries('BasicTests')
    def getBasicTestById(self,id) -> dict:
        Session=sessionmaker()
        Session.configure(bind=self.engine)
        with Session() as sess:
            statement = select(BasicTests).filter_by(id=int(id))
            s1 = sess.scalars(statement).first()
            if s1:
               rval=s1.toDict()
        return rval
        
    def getGroupId(self,testgroup) -> int:
        rval=0
        Session=sessionmaker()
        Session.configure(bind=self.engine)
        with Session() as sess:
            statement = select(TestGroups).filter_by(name=testgroup)
            s1 = sess.scalars(statement).all()
            if s1:
               rval=s1[0].id
        return rval
    def getTestsForGroup(self,testgroup) -> list[dict]:
        rval=[{"name":"onetest","description":"This is test 1"},
              {"name":"test#2","description":"this is number 2"}]
        rval=[]
        tgid=self.getGroupId(testgroup)
        Session=sessionmaker()
        Session.configure(bind=self.engine)
        self.log.info(f"Retrieving tests for group {testgroup}")
        with Session() as sess:
            statement = select(BasicTests).filter_by(test_group_id=tgid)
            s1 = sess.scalars(statement).all()
            #s1=eval(f"sess.query(BasicTests).all()")
            if s1:
               rval=[x.toDict() for x in s1]
        return rval
    def getUserRolesById(self,user_id:int) -> list[str]:
        "Looks up a user by id, and returns a list of roles that user has"
        Session=sessionmaker()
        Session.configure(bind=self.engine)
        rval=[]
        with Session() as sess:
            stmt= select(Roles.name).select_from(Roles).join(
                   UserRoles,Roles.id == UserRoles.role_id).where(
                       UserRoles.user_id==user_id)
            s1=sess.execute(stmt ).all()
            if s1 and len(s1) > 0:
                rval=[x[0] for x in s1]
        return rval
        
    def getUserByUsername(self,username:str) -> dict:
        "Looks up a user by username, and returns the dict for that user"
        Session=sessionmaker()
        Session.configure(bind=self.engine)
        rval=None
        with Session() as sess:
            s1=sess.execute(select(Users).where(Users.username==username)).first()
            if s1 and len(s1) == 1:
                rval=s1[0].toDict()
        return rval

