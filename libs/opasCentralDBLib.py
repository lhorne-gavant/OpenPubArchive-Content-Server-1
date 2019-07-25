#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
opasCentralDBLib

This library is supports the main functionality of the OPAS Central Database

The database has use and usage information.

2019.0708.1 - Python 3.7 compatible.  Work in progress.

"""
__author__      = "Neil R. Shapiro"
__copyright__   = "Copyright 2019, Psychoanalytic Electronic Publishing"
__license__     = "Apache 2.0"
__version__     = "2019.0619.1"
__status__      = "Development"

import sys
sys.path.append('../libs')
sys.path.append('../config')

import opasConfig
import localsecrets
from localsecrets import DBHOST, DBUSER, DBPW, DBNAME

import os.path
import re
import logging
logger = logging.getLogger(__name__)

from datetime import datetime, timedelta
import time

import secrets
from pydantic import BaseModel
from passlib.context import CryptContext
from pydantic import ValidationError

import pymysql

#import opasAuthBasic
from localsecrets import SECRET_KEY, ALGORITHM, urlPaDS, soapTest
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

import requests
import xml.etree.ElementTree as ET

# All opasCentral Database Models here
import modelsOpasCentralPydantic
from modelsOpasCentralPydantic import User, UserInDB
#from models import SessionInfo

DEFAULTSESSIONLENGTH = 1800 # seconds (timeout)

API_LOGIN = 1	        # /Login/
API_LOGIN_STATUS = 2	#/License/Status/Login/
API_LOGOUT = 3      	# /Logout/
API_ALERTS = 6
API_REPORTS = 7
API_METADATA_BANNERS = 10	#/Metadata/Banners/
API_METADATA_BANNERS_FOR_PEPCODE = 11	#/Metadata/Banners/{pepcode}/
API_METADATA_SOURCEINFO = 12	#/Metadata/{sourceType}/
API_METADATA_SOURCEINFO_FOR_PEPCODE = 13	#/Metadata/{sourceType}/{pepCode}/
API_METADATA_VOLUME_INDEX = 14	#/Metadata/Volumes/{pepCode}/
API_METADATA_CONTENTS = 15	#/Metadata/Contents/{pepCode}/
API_METADATA_CONTENTS_FOR_VOL = 16	#/Metadata/Contents/{pepCode}/{pepVol}/
API_METADATA_BOOKS = 17	#/Metadata/Contents/Books/{bookBaseDocumentID}/
API_AUTHORS_INDEX = 20	#/Authors/Index/{authNamePartial}/
API_AUTHORS_PUBLICATIONS = 21	#/Authors/Publications/{authNamePartial}/
API_DOCUMENTS_ABSTRACTS = 30	#/Documents/Abstracts/{documentID}/
API_DOCUMENTS = 31	#/Documents/{documentID}/
API_DOCUMENTS_PDF = 32	#/Documents/Downloads/PDF/{documentID}/
API_DOCUMENTS_EPUB = 33	#/Documents/Downloads/PDF/{documentID}/
API_DOCUMENTS_IMAGE = 34	#/Documents/Downloads/Images/{imageID}/
API_DATABASE_SEARCHANALYSIS_FOR_TERMS = 40	#/Database/SearchAnalysis/{searchTerms}/
API_DATABASE_SEARCH = 41	#/Database/Search/
API_DATABASE_WHATSNEW = 42	#/Database/WhatsNew/
API_DATABASE_MOSTCITED = 43	#/Database/MostCited/
API_DATABASE_MOSTDOWNLOADED = 44	#/Database/MostDownloaded/
API_DATABASE_SEARCHANALYSIS = 45	#/Database/SearchAnalysis/

def verifyAccessToken(sessionID, username, accessToken):
    return pwd_context.verify(sessionID+username, accessToken)
    
def verifyPassword(plain_password, hashed_password):
    """
    >>> verifyPassword("secret", getPasswordHash("secret"))
    
    """
    return pwd_context.verify(plain_password, hashed_password)

def getPasswordHash(password):
    """
    (Test disabled, since tested via verify_password docstring)
    >> getPasswordHash("test 1 2 3 ")
    
    >>> getPasswordHash("temporaryLover")
    
    """
    return pwd_context.hash(password)

class opasCentralDB(object):
    """
    This object should be used and then discarded on an endpoint by endpoint basis in any
      multiuser mode.
      
    Therefore, keeping session info in the object is ok,
    
    >>> ocd = opasCentralDB()
    >>> randomSessionID = secrets.token_urlsafe(16)
    >>> success, sessionInfo = ocd.saveSession(sessionID=randomSessionID)
    >>> sessionInfo.authenticated
    False
    >>> sessionInfo = ocd.getSession(sessionID=randomSessionID)
    >>> sessionInfo.authenticated
    False
    >>> ocd.recordSessionEndpoint(sessionID=randomSessionID, apiEndpointID=API_AUTHORS_INDEX, documentID="IJP.001.0001A", statusMessage="Testing")
    1
    >>> ocd.updateDocumentViewCount("IJP.001.0001A")
    1
    >>> ocd.endSession(sessionInfo.session_id)
    True
    # don't delete, do it manually
    > ocd.deleteSession(sessionID=randomSessionID)
    True
    """
    def __init__(self, sessionID=None, accessToken=None, tokenExpiresTime=None, userName="NotLoggedIn", user=None):
        self.db = None
        self.connected = False
        self.authenticated = False
        self.sessionID = sessionID
        self.accessToken = accessToken
        self.tokenExpiresTime = tokenExpiresTime
        self.user = None
        self.sessionInfo = None
        
    def openConnection(self, callerName=""):
        """
        Opens a connection if it's not already open.
        
        If already open, no changes.
        
        """
        try:
            status = self.db.open
            self.connected = True
            if opasConfig.CONSOLE_DB_DEBUG_MESSAGES_ON:
                print ("Database connection was already opened {}".format("(" + callerName + ")"))
            
        except:
            # not open reopen it.
            status = False
        
        if status == False:
            try:
                self.db = pymysql.connect(host=DBHOST, user=DBUSER, password=DBPW, database=DBNAME)
                self.connected = True
                if opasConfig.CONSOLE_DB_DEBUG_MESSAGES_ON:
                    print ("Database connection opened {}".format("(" + callerName + ")"))
            except:
                errMsg = "Cannot connect to database {} for host {} and user {}".format(DBNAME, DBHOST, DBUSER)
                logger.error(errMsg)
                if opasConfig.CONSOLE_DB_DEBUG_MESSAGES_ON:
                    print (errMsg)
                self.connected = False
                self.db = None

        return self.connected

    def closeConnection(self, callerName=""):
        try:
            if self.db.open:
                self.db.close()
                if opasConfig.CONSOLE_DB_DEBUG_MESSAGES_ON:
                    print ("Database connection closed {}".format("(" + callerName + ")"))
                self.db = None
        except:
            errMsg = "closeConnection: The db is not open {}".format("(" + callerName + ")")
            if opasConfig.CONSOLE_DB_DEBUG_MESSAGES_ON:
                print (errMsg)
            logger.error(errMsg)

        # make sure to mark the connection false in any case
        self.connected = False           

    def endSession(self, sessionID, sessionEnd=datetime.utcfromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')):
        """
        End the session
        
        Tested in main instance docstring
        """
        retVal = None
        self.openConnection(callerName="endSession") # make sure connection is open
        if self.db != None:
            cursor = self.db.cursor()
            sql = """UPDATE api_sessions
                     SET session_end = %s
                     WHERE session_id = %s
                  """
            success = cursor.execute(sql,
                                        (sessionEnd,
                                         sessionID
                                         )                                     
                                    )
            self.db.commit()
            cursor.close()
            if success:
                retVal = True
            else:
                logger.warning("Could not record close session per token={} in DB".format(sessionToken))
                retVal = False

        self.closeConnection(callerName="endSession") # make sure connection is closed
        return retVal
        
       
    def getSessionFromDB(self, sessionID):
        """
        Get the session record info for session sessionID
        
        Tested in main instance docstring
        """
        from models import SessionInfo
        self.openConnection(callerName="getSession") # make sure connection is open
        retVal = None
        if self.db != None:
            curs = self.db.cursor(pymysql.cursors.DictCursor)
            # now insert the session
            sql = "SELECT * FROM api_sessions WHERE session_id = '{}'".format(sessionID);
            res = curs.execute(sql)
            if res == 1:
                session = curs.fetchone()
                # sessionRecord
                retVal = SessionInfo(**session)
                if retVal.access_token == "None":
                    retVal.access_token = None
                
            else:
                retVal = None
            
        self.closeConnection(callerName="getSession") # make sure connection is closed

        # return session model object
        return retVal # None or Session Object

    def updateSession(self, sessionID, userID=None, accessToken=None, userIP=None, connectedVia=None, sessionEnd=None):
        """
        Update the extra fields in the session record
        """
        retVal = None
        self.openConnection(callerName="updateSession") # make sure connection is open
        setClause = "SET "
        added = 0
        if accessToken != None:
            setClause += " access_token = '{}'".format(accessToken) 
            added += 1
        if userID != None:
            if added > 0:
                setClause += ", "
            setClause += " user_id = '{}'".format(userID) 
            added += 1
        if userIP != None:
            if added > 0:
                setClause += ", "
            setClause += " user_ip = '{}'".format(userIP) 
            added += 1
        if connectedVia != None:
            if added > 0:
                setClause += ", "
            setClause += " connected_via = '{}'".format(connectedVia) 
            added += 1
        if sessionEnd != None:
            if added > 0:
                setClause += ", "
            setClause += " session_end = '{}'".format(sessionEnd) 
            added += 1

        if added > 0:
            if self.db != None:
                try:
                    cursor = self.db.cursor()
                    sql = """UPDATE api_sessions
                             {}
                             WHERE session_id = %s
                          """.format(setClause)
                    success = cursor.execute(sql, (sessionID))
                except pymysql.InternalError as error:
                    code, message = error.args
                    print (">>>>>>>>>>>>> %s %s", code, message)
                    logger.error(code, message)
                else:
                    self.db.commit()
                
                cursor.close()
                if success:
                    retVal = True
                    print ("Updated session record for session: {}".format(sessionID))
                else:
                    retVal = False
                    print ("Session close/update did not work for sessionID: {}".format(sessionID))
                    logger.warning("Could not record close session per token={} in DB".format(sessionID))

        self.closeConnection(callerName="updateSession") # make sure connection is closed
        return retVal
    def deleteSession(self, sessionID):
        """
        Remove the session record, mostly for testing purposes.
        
        """
        retVal = False
        session = None
        if sessionID is None:
            errMsg = "No session ID specified"
            logger.error(errMsg)
            if opasConfig.CONSOLE_DB_DEBUG_MESSAGES_ON:
                print (errMsg)
        else:
            if not self.openConnection(callerName="deleteSession"): # make sure connection opens
                errMsg = "Delete session could not open database"
                logger.error(errMsg)
                if opasConfig.CONSOLE_DB_DEBUG_MESSAGES_ON:
                    print (errMsg)
            else: # its open
                if self.db != None:  # don't need this check, but leave it.
                    cursor = self.db.cursor()
       
                    # now delete the session
                    sql = """DELETE FROM api_sessions
                             WHERE session_id = '%s'""" % sessionID
                    
                    success = cursor.execute(sql)
                    retVal = self.db.commit()
                    cursor.close()
                    self.sessionInfo = None
                    self.closeConnection(callerName="deleteSession") # make sure connection is closed

        return retVal # return true or false, success or failure
        
    def saveSession(self, sessionID, 
                    expiresTime=None, 
                    username="NotLoggedIn", 
                    userID=0,  # can save us a lookup ... #TODO
                    userIP=None,
                    connectedVia=None,
                    referrer=None,
                    apiClientID=0, 
                    accessToken=None,
                    keepActive=False):
        """
        Save the session info to the database
        
        Tested in main instance docstring
        """
        retVal = False
        sessionInfo = None
        if sessionID is None:
            errMsg = "SaveSession: No session ID specified"
            logger.error(errMsg)
            if opasConfig.CONSOLE_DB_DEBUG_MESSAGES_ON:
                print (errMsg)
        else:
            if not self.openConnection(callerName="saveSession"): # make sure connection opens
                errMsg = "Save session could not open database"
                logger.error(errMsg)
                if opasConfig.CONSOLE_DB_DEBUG_MESSAGES_ON:
                    print (errMsg)
            else: # its open
                sessionStart=datetime.utcfromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
                if self.db != None:  # don't need this check, but leave it.
                    cursor = self.db.cursor()
                    if username != "NotLoggedIn":
                        user = self.getUser(username=username)
                        if user:
                            userID = user.user_id
                            authenticated = True
                            #if expiresTime == None:
                                #from opasCentralDBLib import getMaxAge
                                #maxAge = getMaxAge(keepActive)
                                #expiresTime = datetime.utcfromtimestamp(time.time() + maxAge).strftime('%Y-%m-%d %H:%M:%S')
                        else:
                            userID = opasConfig.USER_NOT_LOGGED_IN_ID
                            authenticated = False
                    else:
                        userID = opasConfig.USER_NOT_LOGGED_IN_ID
                        authenticated = False
        
                    # now insert the session
                    sql = """INSERT INTO api_sessions(session_id,
                                                      user_id, 
                                                      username,
                                                      user_ip,
                                                      connected_via,
                                                      referrer,
                                                      session_start, 
                                                      access_token, 
                                                      authenticated,
                                                      api_client_id
                                              )
                                              VALUES 
                                                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """
                    
                    success = cursor.execute(sql, 
                                             (sessionID, 
                                              userID, 
                                              username,
                                              userIP,
                                              connectedVia,
                                              referrer,
                                              sessionStart, 
                                              accessToken,
                                              authenticated,
                                              apiClientID
                                              )
                                             )
                    if success:
                        msg = "saveSession: Session {} Record Saved".format(sessionID)
                        print (msg)
                    else:
                        msg = "saveSession {} Record Could not be Saved".format(sessionID)
                        print (msg)
                        logger.warning(msg)
                    
                    retVal = self.db.commit()
                    cursor.close()
                    sessionInfo = self.getSessionFromDB(sessionID)
                    self.sessionInfo = sessionInfo
                    self.closeConnection(callerName="saveSession") # make sure connection is closed
    
        # return session model object
        return retVal, sessionInfo #True or False, and SessionInfo Object

    def closeExpiredSessions(self, expireTime=30):
        """
        Retire any expire sessions
        """
        retVal = None
        self.openConnection(callerName="closeExpiredSessions") # make sure connection is open
        setClause = "SET "
        added = 0
        if self.db != None:
            try:
                cursor = self.db.cursor()
                sql = """ UPDATE api_sessions
                          SET session_end = NOW()
                          WHERE session_id IN
                          (SELECT
                            vw_latest_session_activity.session_id
                             FROM
                             vw_latest_session_activity
                             WHERE latest_activity < DATE_SUB(NOW(), INTERVAL {} MINUTE))        
                      """.format(expireTime)
                success = cursor.execute(sql)
            except pymysql.InternalError as error:
                code, message = error.args
                print (">>>>>>>>>>>>> %s %s", code, message)
                logger.error(code, message)
            else:
                self.db.commit()
            
            cursor.close()
            if success:
                retVal = True
                print ("Closed {} expired sessions".format(int(success)))
            else:
                retVal = False
                print ("Closed expired sessions did not work")
                logger.warning("Could not retire sessions in DB")

        self.closeConnection(callerName="closeExpiredSessions") # make sure connection is closed
        return retVal

    def retireExpiredSessions(self):
        """
        Retire any expire sessions
        """
        retVal = None
        self.openConnection(callerName="retireExpiredSessions") # make sure connection is open
        setClause = "SET "
        added = 0
        if self.db != None:
            try:
                cursor = self.db.cursor()
                sql = """UPDATE api_sessions
                         SET session_end = NOW()
                         WHERE session_expires_time < NOW()
                         AND session_end is NULL
                      """
                success = cursor.execute(sql)
            except pymysql.InternalError as error:
                code, message = error.args
                print (">>>>>>>>>>>>> %s %s", code, message)
                logger.error(code, message)
            else:
                self.db.commit()
            
            cursor.close()
            if success:
                retVal = True
                print ("Retired {} expired sessions".format(int(success)))
            else:
                retVal = False
                print ("Retired expired sessions did not work")
                logger.warning("Could not retire sessions in DB")

        self.closeConnection(callerName="retireExpiredSessions") # make sure connection is closed
        return retVal
    
    def recordSessionEndpoint(self, sessionID=None, apiEndpointID=0, params=None, documentID=None, returnStatusCode=0, statusMessage=None):
        """
        Track endpoint calls
        
        Tested in main instance docstring
        """
        retVal = None
        if not self.openConnection(callerName="recordSessionEndpoint"): # make sure connection is open
            errMsg = "Save session could not open database"
            logger.error(errMsg)
            if opasConfig.CONSOLE_DB_DEBUG_MESSAGES_ON:
                print (errMsg)
        else:
            if sessionID is None:
                if self.sessionID == None:
                    # no session open!
                    logger.warning("recordSessionEndpoint: No session is open")
                    return retVal
                else:
                    sessionID = self.sessionID
    
            if self.db != None:  # shouldn't need this test
                cursor = self.db.cursor()
                # TODO: I removed returnStatusCode from here. Remove it from the DB
                sql = """INSERT INTO 
                            api_session_endpoints(session_id, 
                                                  api_endpoint_id,
                                                  params, 
                                                  documentid, 
                                                  return_status_code,
                                                  return_added_status_message
                                                 )
                                                 VALUES 
                                                 (%s, %s, %s, %s, %s, %s)"""
                                                 
        
                retVal = cursor.execute(sql, (
                                                  sessionID, 
                                                  apiEndpointID, 
                                                  params,
                                                  documentID,
                                                  returnStatusCode,
                                                  statusMessage
                                                 ))
                self.db.commit()
                cursor.close()
            
            self.closeConnection(callerName="recordSessionEndpoint") # make sure connection is closed

        return retVal

    def getSources(self, source=None, sourceType=None, limit=None, offset=0):
        """
        >>> ocd = opasCentralDB()
        >>> sources = ocd.getSources()

        """
        self.openConnection(callerName="getSources") # make sure connection is open
        totalCount = 0
        retVal = None
        limitClause = ""
        if limit is not None:
            limitClause = "LIMIT {}".format(limit)
            if offset != 0:
                limitClause += "OFFSET {}".format(offset)

        if self.db != None:
            try:
                curs = self.db.cursor(pymysql.cursors.DictCursor)
                if source is not None:
                    sqlAll = "FROM vw_opas_sources WHERE active = 1 and src_code = '%s'" % source
                    sql = "SELECT * " + sqlAll + "ORDER BY title {}".format(limitClause)
                    res = curs.execute(sql)
                elif sourceType is not None:
                    sqlAll = "FROM vw_opas_sources WHERE active = 1 and src_type = '%s' and (src_type_qualifier <> 'multivolumesubbook' or src_type_qualifier IS NULL)" % sourceType
                    sql = "SELECT * " + sqlAll + "ORDER BY title {}".format(limitClause)
                    res = curs.execute(sql)
                else:  # bring them all back
                    sqlAll = "FROM vw_opas_sources active = 1 and (src_type_qualifier <> 'multivolumesubbook' or src_type_qualifier IS NULL)"
                    sql = "SELECT * " + sqlAll + "ORDER BY title {}".format(limitClause)
                    res = curs.execute(sql)
                    
            except Exception as e:
                msg = "getSources Error querying vw_opas_sources: {}".format(e)
                logger.error(msg)
                print (msg)
            else:
                if res:
                    retVal = curs.fetchall()
                    if limitClause != None:
                        # do another query to count possil
                        curs2 = self.db.cursor()
                        sqlCount = "SELECT COUNT(*) " + sqlAll
                        countCur = curs2.execute(sqlCount)
                        try:
                            totalCount = curs2.fetchone()[0]
                        except:
                            totalCount  = 0
                        curs2.close()
                        curs.close()
                    else:
                        totalCount = len(retVal)
                else:
                    retVal = None
            
        self.closeConnection(callerName="getSources") # make sure connection is closed

        # return session model object
        return totalCount, retVal # None or Session Object

    def updateDocumentViewCount(self, articleID, account="NotLoggedIn", title=None, viewType="Online"):
        """
        Add a record to the doc_viewcounts table for specified viewtype

        Tested in main instance docstring
        """
        retVal = None
        self.openConnection(callerName="updateDocumentViewcount") # make sure connection is open

        try:
            cursor = self.db.cursor()
            sql = """INSERT INTO 
                        doc_viewcounts(account, 
                                        locator, 
                                        title, 
                                        type, 
                                        datetimechar
                                      )
                                      VALUES 
                                        ('%s', '%s', '%s', '%s', '%s')"""
            
            retVal = cursor.execute(sql,
                                    (account,
                                     articleID, 
                                     title, 
                                     viewType, 
                                     datetime.utcfromtimestamp(time.time()).strftime('%Y-%m-%dT%H:%M:%SZ')
                                     )
                                    )
            self.db.commit()
            cursor.close()

        except Exception as e:
            logger.warning("recordSessionEndpoint: {}".format(e))
            

        self.closeConnection(callerName="updateDocumentViewcount") # make sure connection is closed

        return retVal
            
    def getUser(self, username = None, userID = None):
        """
        If user exists (via username or userID) and has an active subscription
          Returns userSubscriptions object and saves it to the ocd object properties.
          
        Note: a user cannot login without an active subscription. 

        Specify either username or userID, not both.
        
        >>> ocd = opasCentralDB()
        >>> ocd.getUser("demo")
        
        """
        try:
            dbOpened = not self.db.open
        except:
            self.openConnection(callerName="getUser") # make sure connection is open
            dbOpened=True
    
        curs = self.db.cursor(pymysql.cursors.DictCursor)
        if username is not None:
            sql = """SELECT *
                     FROM user_active_subscriptions
                     WHERE username = '{}'""" .format(username)
        elif userID is not None:
            sql = """SELECT *
                     FROM user_active_subscriptions
                     WHERE user_id = '{}'""" .format(userID)

        if sql is None:
            logger.error("getUser: No user info supplied to search by")
            retVal = None
        else:
            res = curs.execute(sql)
            if res == 1:
                user = curs.fetchone()
                retVal = modelsOpasCentralPydantic.UserSubscriptions(**user)
            else:
                retVal = None

        if dbOpened: # if we opened it, close it.
            self.closeConnection(callerName="getUser") # make sure connection is closed

        return retVal
    
    def verifyAdmin(self, username, password):
        """
        Find if this is an admin, and return user info for them.
        Returns a user object
        
        >>> ocd = opasCentralDB()
        >>> ocd.verifyAdmin("TemporaryDeveloper", "temporaryLover")
        
        """
        retVal =  None
        admin = self.getUser(username)
        try:
            if admin.enabled and admin.admin:
                if verifyPassword(password, admin.password):
                    retVal = admin
        except:
            errMsg = "Cannot find admin user {}".format(username)
            logger.error(errMsg)
            if opasConfig.CONSOLE_DB_DEBUG_MESSAGES_ON:
                print (errMsg)
    
        return retVal   
    
    def createUser(self, username, password, adminUsername, adminPassword, company=None, email=None):
        """
        Create a new user!
        
        >>> ocd = opasCentralDB()
        >>> ocd.createUser("nobody2", "nothing", "TemporaryDeveloper", "temporaryLover", "USGS", "nobody@usgs.com")
          
        """
        retVal = None
        self.openConnection(callerName="createUser") # make sure connection is open
        curs = self.db.cursor(pymysql.cursors.DictCursor)
    
        admin = self.verifyAdmin(adminUsername, adminPassword)
        if admin is not None:
            # see if user exists:
            user = self.getUser(username)
            if user is None: # good to go
                user = UserInDB()
                user.username = username
                user.password = getPasswordHash(password)
                user.company = company
                user.enabled = True
                user.email_address = email
                user.modified_by_user_id = admin.user_id
                user.enabled = True
                
                sql = """INSERT INTO user 
                         (
                            username,
                            email_address,
                            enabled,
                            company,
                            password,
                            modified_by_user_id,
                            added_date,
                            last_update
                            )
                        VALUES ('%s', '%s', %s, '%s', '%s', '%s', '%s', '%s')
                      """ % \
                          ( pymysql.escape_string(user.username),
                            user.email_address,
                            user.enabled,
                            pymysql.escape_string(user.company),
                            getPasswordHash(user.password),
                            admin.user_id,
                            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                          )
                if curs.execute(sql):
                    msg = "Created user {}".format(user.username)
                    print (msg)
                    self.db.commit()
                else:
                    err = "Could not create user {}".format(user.username)
                    logger.error(err)
                    print (err)
    
                curs.close()
                retVal = User(**user.dict())
            else:
                err = "Username {} already in database.".format(user.username)
                logger.error(err)
                print (err)
    
        self.closeConnection(callerName="createUser") # make sure connection is closed
        return retVal
        
    
    def authenticateUser(self, username: str, password: str):
        """
        Authenticate a user. 
        If they exist in the database, then return user info as
           (True, user)
        Else returns (False, None)
        
        >>> ocd = opasCentralDB()
        >>> status, userInfo = ocd.authenticateUser("TemporaryDeveloper", "temporaryLover")  # Need to disable this account when system is online!
        >>> status
        True
        """
        print ("Authenticating user: {}".format(username))
        self.openConnection(callerName="authenticateUser") # make sure connection is open
        user = self.getUser(username)  # returns a UserInDB object
        if not user:
            msg = "User: {} turned away".format(username)
            logger.warning(msg)
            print (msg)
            retVal = (False, None)
        elif not verifyPassword(password, user.password):
            msg = "User: {} turned away with incorrect password".format(username)
            logger.warning(msg)
            print (msg)
            retVal = (False, None)
        else:
            self.user = user
            msg = "Authenticated (with active subscription) user: {}, sessionID: {}".format(username, self.sessionID)
            logger.info(msg)
            print (msg)
            retVal = (True, user)

        if retVal == (False, None):
            # try PaDSlogin
            user = self.authViaPaDS(username, password)
            if user == None:
                # Not a PaDS account
                retVal = (False, None)
            else:
                retVal = (True, user)
                
        # start session for the new user

        if dbOpened: # if we opened it, close it.
            self.closeConnection(callerName="authenticateReferrer") # make sure connection is closed

        self.closeConnection(callerName="authenticateUser") # make sure connection is closed
        return retVal

    def authenticateReferrer(self, referrer: str):
        """
        Authenticate a referrer (e.g., from PaDS). 
        
        >>> ocd = opasCentralDB()
        >>> refToCheck = "http://www.psychoanalystdatabase.com/PEPWeb/PEPWeb{}Gateway.asp".format(13)
        >>> status, userInfo = ocd.authenticateReferrer(refToCheck)  # Need to disable this account when system is online!
        >>> status
        True

        """
        retVal = (False, None)
        print ("Authenticating user by referrer: {}".format(referrer))
        try:
            dbOpened = not self.db.open
        except:
            self.openConnection(callerName="authenticateReferrer") # make sure connection is open
            dbOpened=True
    
        curs = self.db.cursor(pymysql.cursors.DictCursor)
        if referrer is not None:
            sql = """SELECT *
                     FROM vw_referrer_users
                     WHERE referrer_url = %s
                     AND enabled = 1
                     """ 

            res = curs.execute(sql, referrer)
            if res == 1:
                refUser = curs.fetchone()
                user = modelsOpasCentralPydantic.UserSubscriptions(**refUser)
                self.user = user
                msg = "Authenticated (with active subscription) referrer: {}".format(referrer)
                logger.info(msg)
                print (msg)
                retVal = (True, user)
            else:
                retVal = (False, None)
                msg = "Referrer: {} turned away".format(referrer)
                logger.warning(msg)
                print (msg)

        if dbOpened: # if we opened it, close it.
            self.closeConnection(callerName="authenticateReferrer") # make sure connection is closed

        return retVal

    def authViaPaDS(self, username, password):
        """
        Check to see if username password is in PaDS
        
        """
        authenticateMore = """<?xml version="1.0" encoding="utf-8"?>
                                <soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
                                  <soap12:Body>
                                    <AuthenticateUserAndReturnExtraInfo xmlns="http://localhost/PEPProduct/PEPProduct">
                                        <UserName>{}</UserName>
                                        <Password>{}</Password>
                                    </AuthenticateUserAndReturnExtraInfo>                
                                  </soap12:Body>
                              </soap12:Envelope>
        """

        retVal = None
        headers = {'content-type': 'text/xml'}
        ns = {"pepprod": "http://localhost/PEPProduct/PEPProduct"}
        soapMessage = authenticateMore.format(username, password)
        response = requests.post(urlPaDS, data=soapMessage, headers=headers)
        #print (response.content)
        root = ET.fromstring(response.content)
        # parse XML return
        AuthenticateUserAndReturnExtraInfoResultNode = root.find('.//pepprod:AuthenticateUserAndReturnExtraInfoResult', ns)
        productCodeNode = root.find('.//pepprod:ProductCode', ns)
        GatewayIdNode = root.find('.//pepprod:GatewayId', ns)
        SubscriberNameNode = root.find('.//pepprod:SubscriberName', ns)
        SubscriberEmailAddressNode = root.find('.//pepprod:SubscriberEmailAddress', ns)
        # assign data
        AuthenticateUserAndReturnExtraInfoResult = AuthenticateUserAndReturnExtraInfoResultNode.text
        if AuthenticateUserAndReturnExtraInfoResult:
            productCode = productCodeNode.text
            gatewayID = GatewayIdNode.text
            SubscriberName = SubscriberNameNode.text
            SubscriberEmailAddress = SubscriberEmailAddressNode.text
            
            refToCheck = "http://www.psychoanalystdatabase.com/PEPWeb/PEPWeb{}Gateway.asp".format(gatewayID)
            possibleUser = self.authenticateReferrer(refToCheck)
            # would need to add new extended info here
            if possibleUser is not None:
                retVal = possibleUser
                retVal = {
                            "authenticated" : AuthenticateUserAndReturnExtraInfoResult,
                            "userName" : SubscriberName,
                            "userEmail" : SubscriberEmailAddress,
                            "gatewayID" : gatewayID,
                            "productCode" : productCode
                        }
            else:
                retVal = None
        
        print (retVal)
    
        return retVal

    
#================================================================================================================================

if __name__ == "__main__":
    print (40*"*", "opasCentralDBLib Tests", 40*"*")
    print ("Running in Python %s" % sys.version_info[0])
    
    #sessionID = secrets.token_urlsafe(16)
    #ocd = opasCentralDB(sessionID, 
                        #secrets.token_urlsafe(16), 
                        #datetime.utcfromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S'),
                        #userName = "gvpi")

    #session = ocd.startSession(sessionID)
    #ocd.recordSessionEndpoint(apiEndpointID=API_AUTHORS_INDEX, documentID="IJP.001.0001A", statusMessage="Testing")
    #ocd.updateDocumentViewCount("IJP.001.0001A")
    #session = ocd.endSession(sessionID)
    #ocd.closeConnection()
    
    #ocd.connected
    
    ocd = opasCentralDB()
    refToCheck = "http://www.psychoanalystdatabase.com/PEPWeb/PEPWeb{}Gateway.asp".format(13)
    ocd.authenticateReferrer(refToCheck)
    sys.exit()
    
    #docstring tests
    import doctest
    doctest.testmod()    
    print ("Tests complete.")