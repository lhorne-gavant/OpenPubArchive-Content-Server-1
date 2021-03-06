#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import opasConfig
import models

# import localsecrets
from localsecrets import PADS_TEST_ID, PADS_TEST_PW, PADS_BASED_CLIENT_IDS
base = "https://padstest.zedra.net/PEPSecure/api"

def pads_login(username=PADS_TEST_ID, password=PADS_TEST_PW):
    ret_val = False
    full_URL = base + f"/v1/Authenticate?UserName={username}&Password={password}"
    response = requests.get(full_URL)
    if response.ok == True:
        ret_val = response.json()
    return ret_val
    
def pads_session_check(session_id, doc_id, doc_year):
    ret_val = False
    ret_resp = None
    full_URL = base + f"/v1/Permits?SessionId={session_id}&DocId={doc_id}&DocYear={doc_year}"
    response = requests.get(full_URL)
    if response.ok == True:
        ret_resp = response.json()
        ret_val = ret_resp["Permit"]

    return ret_val, ret_resp      
        
def get_access_limitations(doc_id, classification, session_info, year=None, doi=None, documentListItem: models.DocumentListItem=None):
    """
    Based on the classification of the document (archive, current), and the users permissions
      in session_info, determine whether this user has access to the full-text of the document,
      and fill out 
    """
    if documentListItem is not None:
        ret_val = documentListItem
    else:
        ret_val = models.AccessLimitations()

    ret_val.doi = doi
    ret_val.accessLimitedPubLink = None
    ret_val.accessLimited = True # no access...default, may be changed below.
    
    if ret_val.doi is not None:
        publisherAccess = opasConfig.ACCESS_SUMMARY_PUBLISHER_INFO + opasConfig.ACCESS_SUMMARY_PUBLISHER_INFO_DOI_LINK % ret_val.doi
        # TODO: get the link we use to send users to publishers site when we don't have it, and no doi, and implement here.
        #       for now, just doi
        ret_val.accessLimitedPubLink = opasConfig.ACCESS_SUMMARY_PUBLISHER_INFO_DOI_LINK % ret_val.doi
    else:
        publisherAccess = ""
    
    if classification in (opasConfig.DOCUMENT_ACCESS_FREE):
        ret_val.accessLimitedDescription = opasConfig.ACCESSLIMITED_DESCRIPTION_FREE
        ret_val.accessLimited = False
        ret_val.accessLimitedCurrentContent = False
        #"This content is currently free to all users."
        ret_val.accessLimitedReason = opasConfig.ACCESSLIMITED_DESCRIPTION_FREE
        
    elif classification in (opasConfig.DOCUMENT_ACCESS_EMBARGOED): # PEPCurrent
        ret_val.accessLimitedDescription = opasConfig.ACCESS_SUMMARY_EMBARGOED
        ret_val.accessLimitedCurrentContent = True
        ret_val.accessLimitedReason = opasConfig.ACCESS_SUMMARY_DESCRIPTION + opasConfig.ACCESS_SUMMARY_EMBARGOED + publisherAccess # limited...get it elsewhere
        try:
            if session_info.authorized_pepcurrent:
                ret_val.accessLimited = False # you can access it
                ret_val.accessLimitedCurrentContent = True # true, this is current content,
                # "This current content is available for you to access"
                ret_val.accessLimitedReason = opasConfig.ACCESSLIMITED_DESCRIPTION_CURRENT_CONTENT_AVAILABLE 
        except:
            pass # could be a direct call without a session; returns unauthorized
            
    elif classification in (opasConfig.DOCUMENT_ACCESS_ARCHIVE):
        ret_val.accessLimitedDescription = opasConfig.ACCESS_SUMMARY_FORSUBSCRIBERS 
        ret_val.accessLimited = True
        ret_val.accessLimitedReason = opasConfig.ACCESS_SUMMARY_DESCRIPTION + opasConfig.ACCESS_SUMMARY_FORSUBSCRIBERS
        try:
            if session_info.authorized_peparchive:
                ret_val.accessLimited = False
                ret_val.accessLimitedCurrentContent = False
                # "This content is available for you to access"
                ret_val.accessLimitedReason = opasConfig.ACCESSLIMITED_DESCRIPTION_AVAILABLE 
        except:
            pass # could be a direct call without a session; returns unauthorized
    
    elif classification in (opasConfig.DOCUMENT_ACCESS_OFFSITE):
        ret_val.accessLimitedDescription = opasConfig.ACCESSLIMITED_DESCRIPTION_OFFSITE
        ret_val.accessLimited = True
        ret_val.accessLimitedCurrentContent = False
        #"This content is currently free to all users."
        ret_val.accessLimitedReason = opasConfig.ACCESS_SUMMARY_DESCRIPTION + opasConfig.ACCESS_SUMMARY_EMBARGOED + publisherAccess # limited...get it elsewhere

    # We COULD check the session_id in PADS here with the art_id and year, for EVERY return!
    #  would it be slow?  Certainly for more than a dozen records, might...this is just for one instance though.
    try:
        if session_info.api_client_session and session_info.api_client_id in PADS_BASED_CLIENT_IDS and ret_val.accessLimited == True:
            authorized, resp = pads_session_check(session_id=session_info.session_id,
                                                  doc_id=doc_id,
                                                  doc_year=year)
            
            if authorized:
                ret_val.accessLimitedCurrentContent = False
                # "This content is available for you to access"
                ret_val.accessLimitedDescription = opasConfig.ACCESSLIMITED_DESCRIPTION_AVAILABLE 
            if authorized:
                ret_val.accessLimited = False
                #documentListItem.accessLimitedCurrentContent = False
                # "This content is available for you to access"
                ret_val.accessLimitedReason = opasConfig.ACCESSLIMITED_DESCRIPTION_AVAILABLE 
            else:
                ret_val.accessLimitedReason = resp.ReasonStr # limited...get it elsewhere
    except:
        pass # can't be checked, will be unauthorized.
    
    return ret_val

