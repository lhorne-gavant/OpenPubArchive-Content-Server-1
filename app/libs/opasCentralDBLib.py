#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
opasCentralDBLib

This library is supports the main functionality of the OPAS Central Database

The database has use and usage information.

OPASCENTRAL TABLES (and Views) CURRENTLY USED:
   vw_stat_most_viewed (depends on vw_stat_docviews_crosstab,
                                   table articles)

   vw_stat_docviews_crosstab (depends on api_docviews,
                                         vw_stat_docviews_lastweek,
                                         vw_stat_docviews_lastmonth,
                                         vw_stat_docviews_lastsixmonths,
                                         vw_stat_docviews_lastcalyear,
                                         vw_stat_docviews_last12months
                                         )

    vw_stat_cited (depends on fullbiblioxml - table copied from PEP XML Processing db pepa1db
                              vw_stat_cited_in_last_5_years,
                              vw_stat_cited_in_last_10_years,
                              vw_stat_cited_in_last_20_years,
                              vw_stat_cited_in_all_years
                  )                                        
    
    vw_api_productbase (this is the ISSN table from pepa1vdb used during processing)
    
    vw_latest_session_activity (list of sessions with date from table api_session_endpoints)

"""
#2019.0708.1 - Python 3.7 compatible.  Work in progress.
#2019.1110.1 - Updates for database view/table naming cleanup
#2020.0426.1 - Updates to ensure doc tests working, a couple of parameters changed names
#2020.0530.1 - Fixed doc tests for termindex, they were looking at number of terms rather than term counts

__author__      = "Neil R. Shapiro"
__copyright__   = "Copyright 2020, Psychoanalytic Electronic Publishing"
__license__     = "Apache 2.0"
__version__     = "2020.0530.1"
__status__      = "Development"

import sys
import re
# import os.path
from contextlib import closing

sys.path.append('../libs')
sys.path.append('../config')

import opasConfig
from opasConfig import norm_val # use short form everywhere

import localsecrets
# from localsecrets import DBHOST, DBUSER, DBPW, DBNAME

import logging
logger = logging.getLogger(__name__)

from datetime import datetime # , timedelta
import time

# import secrets
# from pydantic import BaseModel
from passlib.context import CryptContext
# from pydantic import ValidationError

import pymysql
import jwt
import json

#import opasAuthBasic
from localsecrets import url_pads, SECRET_KEY
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

import requests
import xml.etree.ElementTree as ET

import models

# All opasCentral Database Models here
import modelsOpasCentralPydantic
from modelsOpasCentralPydantic import User, UserInDB
#from models import SessionInfo

DEFAULTSESSIONLENGTH = 1800 # seconds (timeout)
API_STATUS_SUCCESS = "Success"
API_ENDPOINT_METHOD_GET = "get"
API_ENDPOINT_METHOD_PUT = "put"
API_ENDPOINT_METHOD_POST = "post"
API_ENDPOINT_METHOD_DELETE = "delete"

# ###############################################################
# API SYMBOLIC ENDPOINTS MUST MATCH API_ENDPOINTS TABLE IN DB!!!!
# ###############################################################
API_LOGIN = 1	        # /Login/
API_LOGIN_STATUS = 2	#/License/Status/Login/
API_LOGOUT = 3      	# /Logout/
API_ALERTS = 6
API_REPORTS = 7
API_OPENAPISPEC = 8     # /Api/Openapispec
API_LIVEDOC = 9         # /Api/Livedoc
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
API_DOCUMENTS_PDFORIG = 33	#/Documents/Downloads/PDFORIG/{documentID}/
API_DOCUMENTS_EPUB = 35	#/Documents/Downloads/PDF/{documentID}/
API_DOCUMENTS_HTML = 36	#/Documents/Downloads/HTML/{documentID}/
API_DOCUMENTS_IMAGE = 37	#/Documents/Downloads/Images/{imageID}/
API_DATABASE_SEARCHANALYSIS_FOR_TERMS = 40	#/Database/SearchAnalysis/{searchTerms}/
API_DATABASE_SEARCH = 41	#/Database/Search/
API_DATABASE_WHATSNEW = 42	#/Database/WhatsNew/
API_DATABASE_MOSTCITED = 43	#/Database/MostCited/
API_DATABASE_MOSTDOWNLOADED = 44	#/Database/MostDownloaded/
API_DATABASE_SEARCHANALYSIS = 45	#/Database/SearchAnalysis/
API_DATABASE_ADVANCEDSEARCH = 46	
API_DATABASE_TERMCOUNTS = 47
API_DATABASE_GLOSSARY_SEARCH = 48	#/Database/Search/
API_DATABASE_EXTENDEDSEARCH = 49
API_DATABASE_SEARCHTERMLIST = 50
API_DATABASE_CLIENT_CONFIGURATION = 51 # /Client/Configuration



#def verifyAccessToken(session_id, username, access_token):
    #return pwd_context.verify(session_id+username, access_token)
    
def verify_password(plain_password, hashed_password):
    """
    >>> verify_password("secret", get_password_hash("secret"))
    True

    >>> verify_password("temporaryLover", '$2b$12$dy27eHxQoeekTMQIlofzvekWPr1rgrGp1fmXbWcQwCQynFkqvDH62')
    True
    
    >>> verify_password("temporaryLover", '$2b$12$0VH2W6CPxJdARmEcVQ7S9.FWk.xC41KdwN1e5XS2wuhbPYNRCFrmy')
    True
    
    >>> verify_password("pakistan", '$2b$12$VRLAkonDGCEuavaSotvbhOf.bVV0GDNysja.cHBFrrYHZw3e2vV7C')
    True

    >>> verify_password("pakistan", '$2b$12$z7F1BD8NhgcuBq090omf1.PfmP6obAaFN0QGyU1n/Gqv2oUvU9CGy')
    False

    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """
    Returns the hashed password that's stored
    >>> get_password_hash("doogie")
    '...'
    """
    return pwd_context.hash(password)

class SourceInfoDB(object):
    def __init__(self):
        self.sourceData = {}
        ocd = opasCentralDB()
        recs = ocd.get_productbase_data()
        for n in recs:
            try:
                self.sourceData[n["pepsrccode"]] = n
            except KeyError as e:
                print ("Missing Source Code Value in %s" % n)

    def lookupSourceCode(self, sourceCode):
        """
        Returns the dictionary entry for the source code or None
          if it doesn't exist.
        """
        dbEntry = self.sourceData.get(sourceCode, None)
        retVal = dbEntry
        return retVal

class opasCentralDB(object):
    """
    This object should be used and then discarded on an endpoint by endpoint basis in any
      multiuser mode.
      
    Therefore, keeping session info in the object is ok,
    
    >>> import secrets
    >>> ocd = opasCentralDB()
    >>> random_session_id = secrets.token_urlsafe(16)
    >>> success, session_info = ocd.save_session(session_id=random_session_id)
    >>> session_info.authenticated
    False
    >>> ocd.record_session_endpoint(session_info=session_info, api_endpoint_id=API_AUTHORS_INDEX, item_of_interest="IJP.001.0001A", status_message="Testing")
    1
    >>> ocd.end_session(session_info.session_id)
    True

    # don't delete, do it manually
    > ocd.delete_session(session_id=random_session_id)
    True
    """
    def __init__(self, session_id=None, access_token=None, token_expires_time=None, username="NotLoggedIn", user=None):
        self.db = None
        self.connected = False
        self.authenticated = False
        self.session_id = session_id
        self.access_token = access_token
        self.user = None
        self.sessionInfo = None
        
    def open_connection(self, caller_name=""):
        """
        Opens a connection if it's not already open.
        
        If already open, no changes.
        >>> ocd = opasCentralDB()
        >>> ocd.open_connection("my name")
        True
        >>> ocd.close_connection("my name")
        """
        try:
            status = self.db.open
            self.connected = True
            # this is normal, why log it?
            # logger.debug(f"Database connection was already opened ({caller_name})")
        except:
            # not open reopen it.
            status = False
        
        if status == False:
            try:
                tunneling = None
                if localsecrets.SSH_HOST is not None:
                    from sshtunnel import SSHTunnelForwarder
                    self.tunnel = SSHTunnelForwarder(
                                                      (localsecrets.SSH_HOST,
                                                       localsecrets.SSH_PORT),
                                                       ssh_username=localsecrets.SSH_USER,
                                                       ssh_pkey=localsecrets.SSH_MYPKEY,
                                                       remote_bind_address=(localsecrets.DBHOST,
                                                                            localsecrets.DBPORT))
                    self.tunnel.start()
                    self.db = pymysql.connect(host='127.0.0.1',
                                           user=localsecrets.DBUSER,
                                           passwd=localsecrets.DBPW,
                                           db=localsecrets.DBNAME,
                                           port=self.tunnel.local_bind_port)
                    tunneling = self.tunnel.local_bind_port
                else:
                    #  not tunneled
                    self.db = pymysql.connect(host=localsecrets.DBHOST, port=localsecrets.DBPORT, user=localsecrets.DBUSER, password=localsecrets.DBPW, database=localsecrets.DBNAME)

                logger.debug(f"Database opened by ({caller_name}) Specs: {localsecrets.DBNAME} for host {localsecrets.DBHOST},  user {localsecrets.DBUSER} port {localsecrets.DBPORT} tunnel {tunneling}")
                self.connected = True
            except Exception as e:
                err_str = f"Cannot connect to database {localsecrets.DBNAME} for host {localsecrets.DBHOST},  user {localsecrets.DBUSER} port {localsecrets.DBPORT} ({e})"
                print(err_str)
                logger.error(err_str)
                self.connected = False
                self.db = None

        return self.connected

    def close_connection(self, caller_name=""):
        if self.db is not None:
            try:
                if self.db.open:
                    self.db.close()
                    self.db = None
                    logger.debug(f"Database closed by ({caller_name})")
                    if localsecrets.CONFIG == "AWSTestAccountTunnel":
                        self.tunnel.stop()
                        logger.debug(f"Database tunnel stopped.")
                else:
                    logger.debug(f"Database close request, but not open ({caller_name})")
                    
            except Exception as e:
                logger.error(f"caller: {caller_name} the db is not open ({e})")

        # make sure to mark the connection false in any case
        self.connected = False           

    def end_session(self, session_id, session_end=datetime.utcfromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')):
        """
        End the session
        
        Tested in main instance docstring
        """
        ret_val = None
        self.open_connection(caller_name="end_session") # make sure connection is open
        if self.db is not None:
            cursor = self.db.cursor()
            sql = """UPDATE api_sessions
                     SET session_end = %s
                     WHERE session_id = %s
                  """
            success = cursor.execute(sql,
                                     (session_end,
                                      session_id
                                      )                                     
                                    )
            self.db.commit()
            cursor.close()
            if success:
                ret_val = True
            else:
                logger.warning(f"Could not record close session per token={sessionToken} in DB")
                ret_val = False

        self.close_connection(caller_name="end_session") # make sure connection is closed
        return ret_val

    def get_productbase_data(self):
        """
        Load the journal book and video product data
        """
        ret_val = {}
        self.open_connection(caller_name="get_productbase_data") # make sure connection is open
        if self.db is not None:
            curs = self.db.cursor(pymysql.cursors.DictCursor)
            sql = "SELECT * from vw_api_sourceinfodb where active=1;"
            row_count = curs.execute(sql)
            if row_count:
                sourceData = curs.fetchall()
                ret_val = sourceData
        else:
            logger.fatal("Connection not available to database.")
        self.close_connection(caller_name="get_productbase_data") # make sure connection is closed
        return ret_val
        
    def get_article_year(self, doc_id):
        """
        Load the article data for a document id
        """
        ret_val = None
        self.open_connection(caller_name="get_productbase_data") # make sure connection is open
        if self.db is not None:
            curs = self.db.cursor(pymysql.cursors.DictCursor)
            sql = f"SELECT art_year from api_articles where art_id='{doc_id}';"
            row_count = curs.execute(sql)
            if row_count:
                sourceData = curs.fetchall()
                ret_val = sourceData[0]["art_year"]
        else:
            logger.fatal("Connection not available to database.")

        self.close_connection(caller_name="get_productbase_data") # make sure connection is closed
        return ret_val
        
    def get_most_viewed_crosstab(self):
        """
         Using the opascentral api_docviews table data, as dynamically statistically aggregated into
           the view vw_stat_most_viewed return the most downloaded (viewed) documents
           
         Supports the updates to Solr via solrXMLPEPWebload, used for view count queries.
            
        """
        ret_val = None
        row_count = 0
        # always make sure we have the right input value
        self.open_connection(caller_name="get_most_viewed_crosstab") # make sure connection is open
        
        if self.db is not None:
            cursor = self.db.cursor(pymysql.cursors.DictCursor)
            sql = """SELECT DISTINCTROW * FROM vw_stat_docviews_crosstab"""
            row_count = cursor.execute(sql)
            if row_count:
                ret_val = cursor.fetchall()
            cursor.close()
        else:
            logger.fatal("Connection not available to database.")
        
        self.close_connection(caller_name="get_most_downloaded_crosstab") # make sure connection is closed
        return row_count, ret_val

    def get_select_count(self, sqlSelect: str):
        """
        Generic retrieval from database, just the count
        
        >>> ocd = opasCentralDB()
        >>> count = ocd.get_select_count(sqlSelect="SELECT * from vw_reports_user_searches WHERE user_id = 12;")
        >>> count > 1000
        True
        
        """
        self.open_connection(caller_name="get_select_count") # make sure connection is open
        ret_val = None

        sqlSelect = re.sub("SELECT .+? FROM", "SELECT COUNT(*) FROM", sqlSelect, count=1, flags=re.IGNORECASE)
        try:
            if self.db is not None:
                curs = self.db.cursor(pymysql.cursors.Cursor)
                curs.execute(sqlSelect)
                row = curs.fetchall()
                ret_val = row[0][0]
        except Exception as e:
            logger.warning("Can't retrieve count.")
            ret_val = 0
            
        self.close_connection(caller_name="get_select_count") # make sure connection is closed

        # return session model object
        return ret_val # None or Session Object

               
    def get_select_as_list_of_dicts(self, sqlSelect: str):
        """
        Generic retrieval from database, into dict
        
        >>> ocd = opasCentralDB()
        >>> records = ocd.get_select_as_list_of_dicts(sqlSelect="SELECT * from vw_reports_session_activity WHERE user_id = 10;")
        >>> len(records) > 1
        True

        """
        self.open_connection(caller_name="get_selection_as_list_of_dicts") # make sure connection is open
        ret_val = None
        if self.db is not None:
            curs = self.db.cursor(pymysql.cursors.DictCursor)
            curs.execute(sqlSelect)
            ret_val = [models.ReportListItem(row=row) for row in curs.fetchall()]
            
        self.close_connection(caller_name="get_selection_as_list_of_dicts") # make sure connection is closed

        # return session model object
        return ret_val # None or Session Object

    def get_session_from_db(self, session_id):
        """
        Get the session record info for session sessionID
        
        Tested in main instance docstring
        """
        from models import SessionInfo # do this here to avoid circularity
        self.open_connection(caller_name="get_session_from_db") # make sure connection is open
        ret_val = None
        if self.db is not None:
            curs = self.db.cursor(pymysql.cursors.DictCursor)
            # now insert the session
            sql = f"SELECT * FROM api_sessions WHERE session_id = '{session_id}'";
            res = curs.execute(sql)
            if res == 1:
                session = curs.fetchone()
                # sessionRecord
                ret_val = SessionInfo(**session)
                if ret_val.access_token == "None":
                    ret_val.access_token = None
                
            else:
                ret_val = None
            
        self.close_connection(caller_name="get_session_from_db") # make sure connection is closed

        # return session model object
        return ret_val # None or Session Object

    def get_mysql_version(self):
        """
        Get the mysql version number
        
        >>> ocd = opasCentralDB()
        >>> ocd.get_mysql_version()
        'Vers: ...'
        """
        ret_val = "Unknown"
        self.open_connection(caller_name="update_session") # make sure connection is open
        if self.db is not None:
            curs = self.db.cursor()
            sql = "SELECT VERSION();"
            success = curs.execute(sql)
            if success:
                ret_val = "Vers: " + curs.fetchone()[0]
                curs.close()
            else:
                ret_val = None
        else:
            logger.fatal("Connection not available to database.")

        self.close_connection(caller_name="update_session") # make sure connection is closed
        return ret_val
    
    def update_session(self, session_id, userID=None, access_token=None, userIP=None, connected_via=None, session_end=None):
        """
        Update the extra fields in the session record
        """
        ret_val = None
        self.open_connection(caller_name="update_session") # make sure connection is open
        setClause = "SET "
        added = 0
        if access_token is not None:
            setClause += f" access_token = '{access_token}'"
            added += 1
        if userID is not None:
            if added > 0:
                setClause += ", "
            setClause += f" user_id = '{userID}'"
            added += 1
        if userIP is not None:
            if added > 0:
                setClause += ", "
            setClause += f" user_ip = '{userIP}'"
            added += 1
        if connected_via is not None:
            if added > 0:
                setClause += ", "
            setClause += f" connected_via = '{connected_via}'"
            added += 1
        if session_end is not None:
            if added > 0:
                setClause += ", "
            setClause += " session_end = '{}'".format(session_end) 
            added += 1

        if added > 0:
            if self.db is not None:
                try:
                    cursor = self.db.cursor()
                    sql = """UPDATE api_sessions
                             {}
                             WHERE session_id = %s
                          """.format(setClause)
                    success = cursor.execute(sql, (session_id))
                except pymysql.InternalError as error:
                    code, message = error.args
                    print (">>>>>>>>>>>>> %s %s", code, message)
                    logger.error(code, message)
                else:
                    self.db.commit()
                
                cursor.close()
                if success:
                    ret_val = True
                    logger.debug(f"Updated session record for session: {session_id}")
                else:
                    ret_val = False
                    logger.warning(f"Could not record close session per sessionID {session_id} in DB")

        self.close_connection(caller_name="update_session") # make sure connection is closed
        return ret_val

    def delete_session(self, session_id):
        """
        Remove the session record, mostly for testing purposes.
        
        """
        ret_val = False
        #session = None
        if session_id is None:
            err_msg = "No session ID specified"
            logger.error(err_msg)
        else:
            if not self.open_connection(caller_name="delete_session"): # make sure connection opens
                logger.error("Delete session could not open database")
            else: # its open
                if self.db is not None:  # don't need this check, but leave it.
                    cursor = self.db.cursor()
       
                    # now delete the session
                    sql = """DELETE FROM api_sessions
                             WHERE session_id = '%s'""" % session_id
                    
                    if cursor.execute(sql):
                        ret_val = self.db.commit()

                    cursor.close()
                    self.sessionInfo = None
                    self.close_connection(caller_name="delete_session") # make sure connection is closed
                else:
                    logger.fatal("Connection not available to database.")

        return ret_val # return true or false, success or failure
        
    def save_session(self, session_id, 
                         expiresTime=None, 
                         username="NotLoggedIn", 
                         userID=0,  # can save us a lookup ... #TODO
                         userIP=None,
                         connected_via=None,
                         referrer=None,
                         apiClientID=0,
                         apiClientSession=False, 
                         accessToken=None,
                         keepActive=False,
                         authorized_peparchive=False,
                         authorized_pepcurrent=False,
                         ):
        """
        Save the session info to the database
        
        Tested in main instance docstring
        """
        ret_val = False
        session_info = None
        if session_id is None:
            logger.error("SaveSession: No session ID specified")
        else:
            if not self.open_connection(caller_name="save_session"): # make sure connection opens
                logger.error("Save session could not open database")
            else: # its open
                session_start=datetime.utcfromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
                session_admin = False
                if self.db is not None:  # don't need this check, but leave it.
                    cursor = self.db.cursor()
                    if username != "NotLoggedIn":
                        user = self.get_user(username=username)
                        if user:
                            userID = user.user_id
                            authenticated = True
                            session_admin = user.admin
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
                                                      session_expires_time,
                                                      access_token, 
                                                      authenticated,
                                                      admin,
                                                      api_client_id,
                                                      api_client_session,
                                                      authorized_peparchive,
                                                      authorized_pepcurrent
                                              )
                                              VALUES 
                                                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) """
                    try:
                        success = cursor.execute(sql, 
                                                 (session_id, 
                                                  userID, 
                                                  username,
                                                  userIP,
                                                  connected_via,
                                                  referrer,
                                                  session_start, 
                                                  expiresTime,
                                                  accessToken,
                                                  authenticated,
                                                  session_admin, 
                                                  apiClientID,
                                                  apiClientSession, 
                                                  authorized_peparchive,
                                                  authorized_pepcurrent
                                                  )
                                                 )
                    except Exception as e:
                        success = False
                        logger.error(f"Save: {e}")
                       
                    if success:
                        # msg = f"Session {session_id} Record Saved"
                        #print (msg)
                        ret_val = True
                    else:
                        msg = f"save_session {session_id} Record Could not be Saved"
                        logger.warning(msg)
                        ret_val = False
                    
                    self.db.commit()
                    cursor.close()
                    session_info = self.get_session_from_db(session_id)
                    self.sessionInfo = session_info
                    self.close_connection(caller_name="save_session") # make sure connection is closed
    
        # return session model object
        return ret_val, session_info #True or False, and SessionInfo Object

    def close_inactive_sessions(self, inactive_time=opasConfig.SESSION_INACTIVE_LIMIT):
        """
        Close any sessions where they've been inactive for inactive_time minutes
        """
        ret_val = None
        self.open_connection(caller_name="close_expired_sessions") # make sure connection is open

        if self.db is not None:
            try:
                cursor = self.db.cursor()
                sql = f""" UPDATE api_sessions
                          SET session_end = NOW()
                          WHERE session_id IN
                          (SELECT
                            vw_latest_session_activity.session_id
                             FROM
                             vw_latest_session_activity
                             WHERE latest_activity < DATE_SUB(NOW(), INTERVAL {inactive_time} MINUTE))        
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
                ret_val = True
                print (f"Closed {success} expired sessions")
            else:
                ret_val = False
                print ("Closed expired sessions did not work")
                logger.warning("Could not retire sessions in DB")

        self.close_connection(caller_name="close_expired_sessions") # make sure connection is closed
        return ret_val

    def count_open_sessions(self):
        """
        Get a count of any open sessions
        
        >>> ocd = opasCentralDB()
        >>> session_count = ocd.count_open_sessions()

        """
        ret_val = 0
        self.open_connection(caller_name="count_open_sessions") # make sure connection is open

        if self.db is not None:
            try:
                cursor = self.db.cursor()
                sql = """SELECT COUNT(*)
                         FROM api_sessions
                         WHERE session_end is NULL
                      """
                success = cursor.execute(sql)
                    
            except pymysql.InternalError as error:
                code, message = error.args
                print (f">>>>>>>>>>>>> {code} {message}")
                logger.error(code, message)
            else:
                if success:
                    result = cursor.fetchone()
                    ret_val = result[0]
                else:
                    retVal = 0
            
            cursor.close()

        self.close_connection(caller_name="count_open_sessions") # make sure connection is closed
        return ret_val
    
    def close_expired_sessions(self):
        """
        Close any sessions past the set expiration time set in the record
        
        >>> ocd = opasCentralDB()
        >>> session_count = ocd.close_expired_sessions()
        Closed ... expired sessions
        """
        ret_val = 0
        self.open_connection(caller_name="close_expired_sessions") # make sure connection is open

        if self.db is not None:
            try:
                cursor = self.db.cursor()
                sql = """UPDATE api_sessions
                         SET session_end = NOW()
                         WHERE session_expires_time < NOW()
                         AND session_end is NULL
                      """
                success = cursor.execute(sql)
                if success:
                    ret_val = cursor.fetchone()
                    
            except pymysql.InternalError as error:
                code, message = error.args
                print (f">>>>>>>>>>>>> {code} {message}")
                logger.error(code, message)
            else:
                self.db.commit()
            
            cursor.close()
            ret_val = int(success)
            print (f"Closed {ret_val} expired sessions")

        self.close_connection(caller_name="close_expired_sessions") # make sure connection is closed
        return ret_val
    
    def record_session_endpoint(self,
                                session_info=None,
                                api_endpoint_id=0,
                                params=None,
                                item_of_interest=None,
                                return_status_code=0,
                                api_endpoint_method="get", 
                                status_message=None):
        """
        Track endpoint calls
        2020-08-25: Added api_endpoint_method
        
        Tested in main instance docstring
        """
        ret_val = None
        if not self.open_connection(caller_name="record_session_endpoint"): # make sure connection is open
            logger.error("record_session_endpoint could not open database")
        else:
            try:
                session_id = session_info.session_id         
            except:
                if self.session_id is None:
                    # no session open!
                    logger.debug("No session is open")
                    return ret_val
                else:
                    session_id = self.session_id
                
            if self.db is not None:  # shouldn't need this test
                cursor = self.db.cursor()
                # TODO: I removed returnStatusCode from here. Remove it from the DB
                sql = """INSERT INTO 
                            api_session_endpoints(session_id, 
                                                  api_endpoint_id,
                                                  params, 
                                                  item_of_interest, 
                                                  return_status_code,
                                                  api_method,
                                                  return_added_status_message
                                                 )
                                                 VALUES 
                                                 (%s, %s, %s, %s, %s, %s, %s)"""
                                                 
        
                ret_val = cursor.execute(sql, (
                                                  session_id, 
                                                  api_endpoint_id, 
                                                  params,
                                                  item_of_interest,
                                                  return_status_code,
                                                  api_endpoint_method, 
                                                  status_message
                                                 ))
                self.db.commit()
                cursor.close()
            
            self.close_connection(caller_name="record_session_endpoint") # make sure connection is closed

        return ret_val

    def get_subscription_access(self, basecode, product_id):
        """
        given a user's subscription product_ids, look up basecode to see if
          that subscription includes access.
        """
        ret_val = 0
        self.open_connection(caller_name="get_subscription_access") # make sure connection is open
        if self.db is not None:
            try:
                curs = self.db.cursor(pymysql.cursors.DictCursor)

                sqlCount = "SELECT count(*) as productvalidity FROM vw_api_products WHERE basecode = %s and product_id = %s"
                data = (basecode, product_id) 
                result = curs.execute(sqlCount, data)
                try:
                    if result:
                        datarow = curs.fetchone()
                        ret_val = datarow['productvalidity']
                    else:
                        ret_val = 0
                except Exception as e:
                    logger.debug(f"{e}")
                    ret_val = 0
                    
            except Exception as e:
                msg = f"Error querying vw_api_products: {e}"
                logger.error(msg)
            else:
                curs.close()
            
        self.close_connection(caller_name="get_subscription_access") # make sure connection is closed

        # return session model object
        logger.debug(f"productCheck for {basecode}/{product_id} results in {ret_val}")
        return ret_val

    def authenticate_user_product_request(self, user_id, basecode, year):
        """
        see if the user has access to this product and year
        
        >>> ocd = opasCentralDB()
        >>> ocd.authenticate_user_product_request(10, "IJP", 2016) # but not logged in
        False
        """
        ret_val = False
        user_products = []
        self.open_connection(caller_name="authenticate_user_product_request") # make sure connection is open
            
        if self.db is not None:
            #  is the product free?
            #    -- need to do a query against the product database directly to answer
            # 
            try:
                curs = self.db.cursor(pymysql.cursors.DictCursor)

                sqlProducts = """SELECT *, YEAR(NOW())-embargo_length as first_year_embargoed FROM vw_api_user_subscriptions_with_basecodes
                                    WHERE user_id = %s and basecode = %s"""
                             
                success = curs.execute(sqlProducts, (user_id, basecode))
                if success:
                    user_products = curs.fetchall()
                
                    
            except Exception as e:
                logger.error(f"Error querying vw_api_products: {e}")
            else:
                curs.close()
                
            for n in user_products:
                # First Priority: If it's free, grant access
                if n["free_access"]:
                    # catch special free document years for logged in users, without being in free
                    ret_val = True # it's ok
                    break

                # Second Priority: If it's in the product year range, grant access
                if n["range_limited"]:
                    if n["range_start_year"] <= year and n["range_end_year"] >= year: # it's in the range
                        ret_val = True # grant product acccess
                        break                    
                else: # This is only if it's NOT range limited, because if it's range limited, 
                      # you don't want to do any other checks, since one of the below would pass

                    # Third Priority: If it's either in the embargo, but product is for embargos, or 
                    if n["embargo_inverted"]: # we want the embargo period
                        if n["first_year_embargoed"] <= year: # it's in the embargo
                            ret_val = True # grant product acccess
                            break
                    # Third Priority: It's not in the embargo, so the product is applicable
                    else: # we don't allow embargoed years
                        if n["first_year_embargoed"] > year: # it's not in the embargo
                            ret_val = True # grant product acccess
                            break
                
        self.close_connection(caller_name="authenticate_user_product_request") # make sure connection is closed
        # returns True if user is granted access
        return ret_val

    def get_sources(self, source_code=None, src_type=None, limit=None, offset=0):
        """
        Return a list of sources
          - for a specific source_code
          - OR for a specific source type (e.g. journal, book)
          - OR if source and src_type are not specified, bring back them all
          
        >>> ocd = opasCentralDB()
        >>> sources = ocd.get_sources(source_code='IJP')

        """
        self.open_connection(caller_name="get_sources") # make sure connection is open
        total_count = 0
        ret_val = None
        limit_clause = ""
        if limit is not None:
            limit_clause = f"LIMIT {limit}"
            if offset != 0:
                limit_clause += f" OFFSET {offset}"

        if self.db is not None:
            try:
                curs = self.db.cursor(pymysql.cursors.DictCursor)
                if source_code is not None:
                    sqlAll = "FROM vw_api_productbase WHERE active = 1 and basecode = '%s'" % source_code
                elif src_type is not None:
                    sqlAll = "FROM vw_api_productbase WHERE active = 1 and product_type = '%s'" % src_type
                else:  # bring them all back
                    sqlAll = "FROM vw_api_productbase WHERE active = 1 and product_type <> 'bookseriessub'"

                sql = f"SELECT * {sqlAll} ORDER BY title {limit_clause}"
                res = curs.execute(sql)
                    
            except Exception as e:
                msg = f"Error querying vw_api_productbase: {e}"
                logger.error(msg)
                # print (msg)
            else:
                if res:
                    ret_val = curs.fetchall()
                    if limit_clause is not None:
                        # do another query to count possil
                        curs2 = self.db.cursor()
                        sqlCount = "SELECT COUNT(*) " + sqlAll
                        count_cur = curs2.execute(sqlCount)
                        try:
                            total_count = curs2.fetchone()[0]
                        except:
                            total_count  = 0
                        curs2.close()
                        curs.close()
                    else:
                        total_count = len(ret_val)
                else:
                    ret_val = None
            
        self.close_connection(caller_name="get_sources") # make sure connection is closed

        # return session model object
        return total_count, ret_val # None or Session Object

    def save_client_config(self, client_id, client_configuration: models.ClientConfig, session_id, replace=False):
        """
        Save a client configuration.  Data format is up to the client.
        
        Returns True of False

        >>> ocd = opasCentralDB()
        >>> model = models.ClientConfig(configName="test", configSettings={"A":"123", "B":"1234"})
        >>> ocd.save_client_config(client_id="test", client_configuration=model, session_id="test123", replace=True)
        (200, 'OK')
        """
        msg = "OK"
        if replace:
            sql_action = "REPLACE"
            ret_val = 200
        else:
            sql_action = "INSERT"
            ret_val = 201
        try:
            session_id = session_id
        except Exception as e:
            # no session open!
            logger.debug("No session is open / Not authorized")
            ret_val = 401 # not authorized
        else:
            self.open_connection(caller_name="record_client_config") # make sure connection is open
            try:
                try:
                    config_json = json.dumps(client_configuration.configSettings)
                except Exception as e:
                    logger.warning(f"Error converting configuration to json {e}.")
                    return ret_val
    
                with closing(self.db.cursor(pymysql.cursors.DictCursor)) as curs:
                    sql = f"""{sql_action} INTO 
                                api_client_configs(client_id,
                                                   config_name, 
                                                   config_settings, 
                                                   session_id
                                                  )
                                                  VALUES 
                                                   (%s, %s, %s, %s)"""
                    
                    eval = curs.execute(sql,
                                        (client_id,
                                         client_configuration.configName,
                                         config_json, 
                                         session_id
                                        )
                                       )
                    self.db.commit()
    
            except Exception as e:
                if sql_action == "REPLACE":
                    msg = f"Error updating (replacing) client config: {e}"
                    logger.error(msg)
                    ret_val = 400
                else: # insert
                    msg = f"Error saving client config: {e}"
                    logger.error(msg)
                    ret_val = 409
    
            self.close_connection(caller_name="record_client_config") # make sure connection is closed

        return (ret_val, msg)

    def get_client_config(self, client_id, client_config_name):
        """
        
        >>> ocd = opasCentralDB()
        >>> ocd.get_client_config(2, "demo")
        
        """
        ret_val = None
        self.open_connection(caller_name="get_client_config") # make sure connection is open
    
        with closing(self.db.cursor(pymysql.cursors.DictCursor)) as curs:
            sql = f"""SELECT *
                      FROM api_client_configs
                      WHERE client_id = '{client_id}'
                      AND config_name = '{client_config_name}'"""

            res = curs.execute(sql)
            if res >= 1:
                clientConfig = curs.fetchone()
                ret_val = modelsOpasCentralPydantic.ClientConfigs(**clientConfig)
            else:
                ret_val = None

        self.close_connection(caller_name="get_client_config") # make sure connection is closed
        if ret_val is not None:
            # convert to return model
            ret_val = models.ClientConfig(clientID = ret_val.client_id,
                                          configName = ret_val.config_name,
                                          configSettings=json.loads(ret_val.config_settings))
    
        return ret_val

    def del_client_config(self, client_id, client_config_name):
        """
        
        >>> ocd = opasCentralDB()
        >>> ocd.del_client_config(2, "demo")
        
        """
        ret_val = None
        saved = self.get_client_config(client_id, client_config_name)
        # open after fetching, since db is closed by call.
        self.open_connection(caller_name="del_client_config") # make sure connection is open
    
        if saved is not None:
            sql = f"""DELETE FROM api_client_configs
                      WHERE client_id = '{client_id}'
                      AND config_name = '{client_config_name}'"""
    
            with closing(self.db.cursor(pymysql.cursors.DictCursor)) as curs:
                res = curs.execute(sql)
                if res >= 1:
                    ret_val = saved
                    self.db.commit()
                else:
                    ret_val = None
            
        self.close_connection(caller_name="del_client_config") # make sure connection is closed

        return ret_val

    def record_document_view(self, document_id, session_info=None, view_type="Abstract"):
        """
        Add a record to the api_doc_views table for specified view_type (Abstract, Document, PDF, PDFOriginal, or EPub)

        Tested in main instance docstring
        
        """
        ret_val = None
        self.open_connection(caller_name="record_document_view") # make sure connection is open
        try:
            session_id = session_info.session_id
            user_id =  session_info.user_id
        except:
            # no session open!
            logger.debug("No session is open")
            return ret_val
        try:
            if view_type.lower() != "abstract" and view_type.lower() != "image/jpeg":
                try:
                    cursor = self.db.cursor()
                    sql = """INSERT INTO 
                                api_docviews(user_id, 
                                              document_id, 
                                              session_id, 
                                              type, 
                                              datetimechar
                                             )
                                             VALUES 
                                              (%s, %s, %s, %s, %s)"""
                    
                    ret_val = cursor.execute(sql,
                                            (user_id,
                                             document_id,
                                             session_id, 
                                             view_type, 
                                             datetime.utcfromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
                                             )
                                            )
                    self.db.commit()
                    cursor.close()
        
                except Exception as e:
                    logger.warning(f"Error saving document view: {e}")
                    
        except Exception as e:
            logger.warning(f"Error checking document view type: {e}")

        self.close_connection(caller_name="record_document_view") # make sure connection is closed

        return ret_val

    def get_user(self, username = None, user_id = None):
        """
        If user exists (via username or user_id) and has an active subscription
          Returns userSubscriptions object and saves it to the ocd object properties.
          
        Note: a user cannot login without an active subscription. 

        Specify either username or userID, not both.
        
        >>> ocd = opasCentralDB()
        >>> ocd.get_user("demo")
        
        """
        try:
            db_opened = not self.db.open
        except:
            self.open_connection(caller_name="get_user") # make sure connection is open
            db_opened=True
    
        curs = self.db.cursor(pymysql.cursors.DictCursor)
        if username is not None:
            sql = f"""SELECT *
                     FROM vw_api_user
                     WHERE username = '{username}'
                     and enabled = 1"""
        elif user_id is not None:
            sql = f"""SELECT *
                     FROM api_user
                     WHERE user_id = '{user_id}'
                     and enabled = 1"""

        if sql is None:
            logger.error("get_user: No user info supplied to search by")
            ret_val = None
        else:
            res = curs.execute(sql)
            if res >= 1:
                user = curs.fetchone()
                ret_val = modelsOpasCentralPydantic.UserInDB(**user)
            else:
                ret_val = None

        if db_opened: # if we opened it, close it.
            self.close_connection(caller_name="get_user") # make sure connection is closed

        return ret_val
    
    def verify_admin(self, session_info):
        """
        Find if this is an admin, and return user info for them.
        Returns a user object
        
        >>> ocd = opasCentralDB()
        >>> ocd.verify_admin(ocd.sessionInfo)
        False
        """
        ret_val = False
        try:
            logged_in_user = jwt.decode(session_info.access_token, localsecrets.SECRET_KEY)
            ret_val = logged_in_user["admin"]
        except:
            err_msg = f"Not logged in or error getting admin status"
            logger.error(err_msg)
            
        return ret_val   
       
    #----------------------------------------------------------------------------------------
    def do_action_query(self, querytxt, queryparams, contextStr=None):
    
        ret_val = None
        localDisconnectNeeded = False
        if self.connected != True:
            self.open_connection(caller_name="action_query") # make sure connection is open
            localDisconnectNeeded = True
            
        dbc = self.db.cursor(pymysql.cursors.DictCursor)
        try:
            ret_val = dbc.execute(querytxt, queryparams)
        except self.db.DataError as e:
            logger.error(f"Art: {contextStr}. DB Data Error {e} ({querytxt})")
            raise self.db.DataError(e)
        except self.db.OperationalError as e:
            logger.error(f"Art: {contextStr}. DB Operation Error {e} ({querytxt})")
            raise self.db.OperationalError(e)
        except self.db.IntegrityError as e:
            logger.error(f"Art: {contextStr}. DB Integrity Error {e} ({querytxt})")
            raise self.db.IntegrityError(e)
        except self.db.InternalError as e:
            logger.error(f"Art: {contextStr}. DB Internal Error {e} ({querytxt})")
            raise self.db.InternalError(e)
            # raise RuntimeError, gErrorLog.logSevere("Art: %s.  DB Intr. Error (%s)" % (contextStr, querytxt))
        except self.db.ProgrammingError as e:
            logger.error(f"DB Programming Error {e} ({querytxt})")
            raise self.db.ProgrammingError(e)
        except self.db.NotSupportedError as e:
            logger.error(f"DB Feature Not Supported Error {e} ({querytxt})")
            raise self.db.NotSupportedError(e)
        except Exception as e:
            logger.error(f"error: %s" % (e))
            raise Exception(e)
    
        # close cursor
        dbc.close()
        
        if localDisconnectNeeded == True:
            # if so, commit any changesand close.  Otherwise, it's up to caller.
            self.db.commit()
            self.close_connection(caller_name="action_query") # make sure connection is open
        
        return ret_val

    #----------------------------------------------------------------------------------------
    def create_user(self,
                    session_info,
                    username,
                    password,
                    full_name=None, 
                    company=None,
                    email=None,
                    user_agrees_tracking=0,
                    user_agrees_cookies=0,
                    view_parent_user_reports=0, 
                    email_optin='n',
                    hide_activity='n',
                    view_parent_reports='n'
                    ):
        """
        Create a new user!
        
        >>> ocd = opasCentralDB()
        >>> ocd.create_user("nobody2", "nothing", "TemporaryDeveloper", "temporaryLover", "USGS", "nobody@usgs.com")
          
        """
        ret_val = None
        self.open_connection(caller_name="create_user") # make sure connection is open
        curs = self.db.cursor(pymysql.cursors.DictCursor)
        if self.verify_admin(session_info):
            # see if user exists:
            user = self.get_user(username)
            if user is None: # good to go
                user = UserInDB()
                user.username = username
                user.full_name = full_name
                user.user_agrees_to_tracking = int(user_agrees_tracking)
                user.user_agrees_to_cookies = int(user_agrees_cookies)
                user.view_parent_user_reports = int(view_parent_user_reports)
                user.password = get_password_hash(password)
                if company is not None:
                    user.company = pymysql.escape_string(company)
                else:
                    user.company = None
                user.enabled = int(1)
                user.email_address = email
                user.modified_by_user_id = session_info.user_id
                user.added_by_user_id = session_info.user_id
                
                sql = """INSERT INTO api_user 
                         (
                            username,
                            email_address,
                            enabled,
                            company,
                            full_name,
                            password,
                            user_agrees_to_tracking,
                            user_agrees_to_cookies,
                            view_parent_user_reports,
                            modified_by_user_id,
                            added_by_user_id,
                            added_date,
                            last_update
                            )
                        VALUES ('%s', '%s', '%s', '%s', '%s', '%s', %d, %d, %d, %d, %d, '%s', '%s')
                      """ % \
                          ( pymysql.escape_string(user.username),
                            user.email_address,
                            user.enabled,
                            user.company,
                            user.full_name, 
                            user.password,
                            user.user_agrees_to_tracking, 
                            user.user_agrees_to_cookies, 
                            user.view_parent_user_reports, 
                            user.modified_by_user_id,
                            user.added_by_user_id,
                            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                          )
                if curs.execute(sql):
                    msg = f"Created user {user.username}"
                    print (msg)
                    self.db.commit()
                else:
                    err = f"Could not create user {user.username}"
                    logger.error(err)
                    print (err)
    
                curs.close()
                ret_val = User(**user.dict())
            else:
                err = f"Username {user.username} already in database."
                logger.error(err)
                print (err)
    
        self.close_connection(caller_name="create_user") # make sure connection is closed
        return ret_val

    #----------------------------------------------------------------------------------------
    def admin_change_user_password(self,
                                   session_info,
                                   username,
                                   old_password,
                                   new_password
                    ):
        """
        Change user's password
        
        >>> ocd = opasCentralDB()
          
        """
        ret_val = None
        self.open_connection(caller_name="change_user_password") # make sure connection is open
        curs = self.db.cursor(pymysql.cursors.DictCursor)
        if self.verify_admin(session_info):
            # see if user exists:
            user = self.get_user(username)
            if user is not None: # good to go
                # *********************************************************
                # since only admin function, don't need old password
                #   if verify_password(old_password, user.password):
                # *********************************************************
                new_hashed_password = get_password_hash(new_password)
                user.modified_by_user_id = session_info.user_id
                sql = """UPDATE api_user
                         SET password = %s,
                             modified_by_user_id = %s,
                             last_update = %s
                         WHERE user_id =%s
                      """
                
                chgs = ( new_hashed_password,
                            session_info.user_id,
                            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            user.user_id
                        )
                if curs.execute(sql, chgs):
                    msg = f"Updated user {user.username}"
                    user.password = new_hashed_password
                    print (msg)
                    self.db.commit()
                else:
                    err = f"Could not update user {user.username}"
                    logger.error(err)
                    print (err)
    
                curs.close()
                ret_val = User(**user.dict())
            else:
                err = f"Username {user.username} not found."
                logger.error(err)
                print (err)
    
        self.close_connection(caller_name="change_user_password") # make sure connection is closed
        return ret_val
        
    #----------------------------------------------------------------------------------------
    def admin_subscribe_user(self,
                             session_info,
                             username,
                             start_date,
                             end_date,
                             product_code,
                             product_parent_code,
                             max_concurrency=0,
                             perpetual=0
                    ):
        """
        Add a subscription
        
        >>> ocd = opasCentralDB()
          
        """
        ret_val = None
        self.open_connection(caller_name="admin_subscribe_user") # make sure connection is open
        curs = self.db.cursor(pymysql.cursors.DictCursor)
        curs2 = self.db.cursor(pymysql.cursors.DictCursor)
        if self.verify_admin(session_info):
            # see if user exists:
            user = self.get_user(username)
            if user is not None: # good to go
                # lookup product id
                product_sql = """
                              SELECT child_product_id, parent_product_id
                              FROM vw_products_flattened
                              WHERE child_basecode = %s
                              AND parent_basecode = %s;
                              """

                sbscrpt_sql = """
                              INSERT INTO api_subscriptions (
                                user_id,
                                product_id,
                                start_date,
                                end_date,
                                max_concurrency,
                                perpetual,
                                modified_by_user_id
                              )
                              VALUES (%s, %s, %s, %s, %s, %s, %s);
                              """

                if curs.execute(product_sql, (product_code, product_parent_code)):
                    product = curs.fetchone()
                    if curs2.execute(sbscrpt_sql, (user.user_id,
                                                   product.get("child_product_id", None), 
                                                   start_date,
                                                   end_date,
                                                   max_concurrency,
                                                   perpetual,
                                                   session_info.user_id
                                                   )):
                        self.db.commit()
                        msg = f"Added subscription to {product_parent_code}/{product_code}"
                        print (msg)
                    else:
                        err = f"Could not add subscription to {product_parent_code}/{product_code}"
                        logger.error(err)
                        print (err)
                else:
                    err = f"Could not find product {product_parent_code}/{product_code}"
                    logger.error(err)
                    print (err)

                curs.close()
                curs2.close()
                ret_val = User(**user.dict())
            else:
                err = f"Username {username} not found."
                logger.error(err)
                print (err)
    
        self.close_connection(caller_name="change_user_password") # make sure connection is closed
        return ret_val
    
    def authenticate_user(self, username: str, password: str):
        """
        Authenticate a user. 
        If they exist in the database, then return user info as
           (True, user)
        Else returns (False, None)
        
        >>> ocd = opasCentralDB()
        >>> status, userInfo = ocd.authenticate_user("TemporaryDeveloper", "temporaryLover")  # Need to disable this account when system is online!
        >>> status
        True
        """
        #print (f"Authenticating user: {username}")
        self.open_connection(caller_name="authenticate_user") # make sure connection is open
        user = self.get_user(username)  # returns a UserInDB object
        if not user:
            msg = f"User: {username} turned away"
            logger.warning(msg)
            #print(msg)
            ret_val = (False, None)
        elif not verify_password(password, user.password):
            msg = f"User: {username} turned away with incorrect password"
            logger.warning(msg)
            #print(msg)
            ret_val = (False, None)
        else:
            self.user = user
            msg = f"Authenticated (with active subscription) user: {username}, sessionID: {self.session_id}"
            logger.info(msg)
            #print(msg)
            ret_val = (True, user)

        if ret_val == (False, None):
            # try PaDSlogin
            user = self.auth_via_pads(username, password)
            if user is None:
                # Not a PaDS account
                ret_val = (False, None)
            else:
                ret_val = (True, user)
                
        # start session for the new user

        self.close_connection(caller_name="authenticate_user") # make sure connection is closed
        return ret_val

    def authenticate_referrer(self, referrer: str):
        """
        Authenticate a referrer (e.g., from PaDS). 
        
        >>> ocd = opasCentralDB()
        >>> refToCheck = "http://www.psychoanalystdatabase.com/PEPWeb/PEPWeb{}Gateway.asp".format(13)
        >>> status, userInfo = ocd.authenticate_referrer(refToCheck)  # Need to disable this account when system is online!
        >>> status
        True

        """
        ret_val = (False, None)
        logger.debug(f"Authenticating user by referrer: {referrer}")
        try:
            db_opened = not self.db.open
        except:
            self.open_connection(caller_name="authenticate_referrer") # make sure connection is open
            db_opened=True
    
        curs = self.db.cursor(pymysql.cursors.DictCursor)
        if referrer is not None:
            sql = """SELECT *
                     FROM vw_user_referred
                     WHERE referrer_url = %s
                     AND enabled = 1
                     """ 

            res = curs.execute(sql, referrer)
            if res == 1:
                refUser = curs.fetchone()
                user = modelsOpasCentralPydantic.UserSubscriptions(**refUser)
                self.user = user
                msg = f"Authenticated (with active subscription) referrer: {referrer}"
                logger.info(msg)
                # print (msg)
                ret_val = (True, user)
            else:
                ret_val = (False, None)
                msg = f"Referrer: {referrer} turned away"
                logger.warning(msg)
                print (msg)

        if db_opened: # if we opened it, close it.
            self.close_connection(caller_name="authenticate_referrer") # make sure connection is closed

        return ret_val

    def auth_via_pads(self, username, password):
        """
        Check to see if username password is in PaDS
        
        """
        authenticate_more = f"""<?xml version="1.0" encoding="utf-8"?>
                                <soap12:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap12="http://www.w3.org/2003/05/soap-envelope">
                                  <soap12:Body>
                                    <AuthenticateUserAndReturnExtraInfo xmlns="http://localhost/PEPProduct/PEPProduct">
                                        <UserName>{username}</UserName>
                                        <Password>{password}</Password>
                                    </AuthenticateUserAndReturnExtraInfo>                
                                  </soap12:Body>
                              </soap12:Envelope>
        """

        ret_val = None
        headers = {'content-type': 'text/xml'}
        ns = {"pepprod": "http://localhost/PEPProduct/PEPProduct"}
        soap_message = authenticate_more
        response = requests.post(url_pads, data=soap_message, headers=headers)
        #print (response.content)
        root = ET.fromstring(response.content)
        # parse XML return
        authenticate_user_and_return_extra_info_result_node = root.find('.//pepprod:AuthenticateUserAndReturnExtraInfoResult', ns)
        product_code_node = root.find('.//pepprod:ProductCode', ns)
        gateway_id_node = root.find('.//pepprod:GatewayId', ns)
        subscriber_name_node = root.find('.//pepprod:SubscriberName', ns)
        subscriber_email_address_node = root.find('.//pepprod:SubscriberEmailAddress', ns)
        # assign data
        authenticate_user_and_return_extra_info_result = authenticate_user_and_return_extra_info_result_node.text
        if authenticate_user_and_return_extra_info_result != "false":
            product_code = product_code_node.text
            gateway_id = gateway_id_node.text
            subscriber_name = subscriber_name_node.text
            subscriber_email_address = subscriber_email_address_node.text
            
            refToCheck = f"http://www.psychoanalystdatabase.com/PEPWeb/PEPWeb{gatewayID}Gateway.asp"
            possible_user = self.authenticate_referrer(refToCheck)
            # would need to add new extended info here
            if possible_user is not None:
                ret_val = possible_user
                ret_val = {
                            "authenticated" : authenticate_user_and_return_extra_info_result,
                            "username" : subscriber_name,
                            "userEmail" : subscriber_email_address,
                            "gatewayID" : gateway_id,
                            "productCode" : product_code
                        }
            else:
                ret_val = None
        
        # print (ret_val)
    
        return ret_val

    
#================================================================================================================================

if __name__ == "__main__":
    print (40*"*", "opasCentralDBLib Tests", 40*"*")
    print (f"Running in Python {sys.version_info[0]}.{sys.version_info[1]}")
   
    logger = logging.getLogger(__name__)
    # extra logging for standalong mode 
    # logger.setLevel(logging.DEBUG)
    # create console handler and set level to debug
    ch = logging.StreamHandler()
    # ch.setLevel(logging.DEBUG)
    # create formatter
    formatter = logging.Formatter('%(asctime)s %(name)s %(lineno)d - %(levelname)s %(message)s')    
    # add formatter to ch
    ch.setFormatter(formatter)
    # add ch to logger
    logger.addHandler(ch)
    
    ocd = opasCentralDB()
    sourceDB = SourceInfoDB()
    code = sourceDB.lookupSourceCode("ANIJP-EL")
    # check this user permissions 
    basecodes = ocd.authenticate_user_product_request(30065, "IJP", 2016)
    basecodes = ocd.authenticate_user_product_request(116848, "IJP", 2016)
    basecodes = ocd.authenticate_user_product_request(10, "IJP", 2016)
    #ocd.get_dict_of_products()
    #ocd.get_subscription_access("IJP", 421)
    #ocd.get_subscription_access("BIPPI", 421)
    #docstring tests
    import doctest
    doctest.testmod(optionflags=doctest.ELLIPSIS|doctest.NORMALIZE_WHITESPACE)
    #doctest.testmod()    
    print ("Fini. Tests complete.")