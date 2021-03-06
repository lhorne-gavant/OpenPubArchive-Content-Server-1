#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Third-party imports...
#from nose.tools import assert_true

#  This test module is in development...

# expects to be run from the app folder.

import sys
import os.path

folder = os.path.basename(os.path.dirname(os.path.abspath(__file__)))
if folder == "tests": # testing from within WingIDE, default folder is tests
    sys.path.append('../libs')
    sys.path.append('../config')
    sys.path.append('../../app')
else: # python running from should be within folder app
    sys.path.append('./libs')
    sys.path.append('./config')


from starlette.testclient import TestClient

import unittest
from localsecrets import TESTUSER, TESTPW, SECRET_KEY, ALGORITHM
import jwt
from datetime import datetime

from unitTestConfig import base_api, base_plus_endpoint_encoded
from main import app

client = TestClient(app)

class TestAPIAuthors(unittest.TestCase):
    """
    Tests
    
    Note: tests are performed in alphabetical order, hence the function naming
          with forced order in the names.
    
    """   

    def test_index_authornamepartial(self):
        """
        Get Author Index For Matching Author Names
        /v1/Authors/Index/{authorNamePartial}/
        """
        response = client.get(base_api + '/v1/Authors/Index/Tuckett/')
        # Confirm that the request-response cycle completed successfully.
        assert(response.ok == True)
        r = response.json()
        # Expect:
        #    {'authorIndex': 
        #           {'responseInfo': {'count': 1, 'limit': 15, 'offset': 0, 'fullCountComplete': True, 'listType': 'authorindex', 'scopeQuery': 'Terms: tuckett', 
        #                             'request': 'http://127.0.0.1:9100/v1/Authors/Index/Tuckett/', 'solrParams': {'terms_fl': 'art_author_id', 'terms_prefix': 'tuckett', 
        #                             'terms_sort': 'index', 'terms_limit': 15, 'fl': '*,score', 'version': 2.2, 'wt': 'xml'}, 'timeStamp': '2019-10-28T13:54:36Z'}, 
        #            'responseSet': [{'authorID': 'tuckett, david', 'publicationsURL': '/v1/Authors/Publications/tuckett, david/', 'publicationsCount': 63}]}}
        assert(r['authorIndex']['responseSet'][0]['publicationsURL'][0:33] == '/v1/Authors/Publications/tuckett,')
       
        response = client.get(base_api + '/v1/Authors/Index/Maslo/')
        # Confirm that the request-response cycle completed successfully.
        assert(response.ok == True)
        r = response.json()
        # Expected:
        #  {'authorIndex': {'responseInfo': {'count': 2, 'limit': 15, 'offset': 0, 'fullCountComplete': True, 'listType': 'authorindex', 'scopeQuery': 'Terms: maslo', 
        #                                    'request': 'http://127.0.0.1:9100/v1/Authors/Index/Maslo/', 'solrParams': {'terms_fl': 'art_author_id', 'terms_prefix': 'maslo', 'terms_sort': 'index', 'terms_limit': 15, 'fl': '*,score', 'version': 2.2, 'wt': 'xml'}, 'timeStamp': '2019-10-28T15:15:03Z'}, 
        #                   'responseSet': [{'authorID': 'maslow, a. h.', 'publicationsURL': '/v1/Authors/Publications/maslow, a. h./', 'publicationsCount': 1}, 
        #                                   {'authorID': 'maslow, abraham h.', 'publicationsURL': '/v1/Authors/Publications/maslow, abraham h./', 'publicationsCount': 2}]}}
        assert(r['authorIndex']['responseSet'][0]['publicationsURL'] == '/v1/Authors/Publications/maslow, a. h./')

    def test_publications_authornames(self):
        """
        Get Author Pubs For Matching Author Names
        /v1​/Authors​/Publications​/{authorNamePartial}​/
        """
        response = client.get(base_api + '/v2/Authors/Publications/maslow, a.*/')
        # Confirm that the request-response cycle completed successfully.
        assert(response.ok == True)
        r = response.json()
        assert(r['authorPubList']['responseInfo']['fullCount'] == 3)
        
        # Doesn't return an error, returns 0 matches.
        response = client.get(base_api + '/v2/Authors/Publications/Flintstone, Fred.*/')
        # Confirm that the request-response cycle completed successfully.
        assert(response.ok == True)
        r = response.json() 
        assert(r['authorPubList']['responseInfo']['fullCount'] == 0)
        
        # try a regex wildcard search (regex wildcards permitted anywhere EXCEPT the end of the name, since that's done automatically)
        response = client.get(base_api + '/v2/Authors/Publications/tu[ckl].*tt/')
        # Confirm that the request-response cycle completed successfully.
        assert(response.ok == True)
        r = response.json()
        assert(r['authorPubList']['responseInfo']['fullCount'] >= 60)
        
        
if __name__ == '__main__':
    unittest.main()
    print ("Tests Complete.")