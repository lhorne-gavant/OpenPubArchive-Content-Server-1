#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Third-party imports...
#from nose.tools import assert_true

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

import unittest
import requests
from requests.utils import requote_uri
# import urllib

from unitTestConfig import base_api, base_plus_endpoint_encoded
import opasAPISupportLib

class TestSearchAnalysis(unittest.TestCase):
    """
    Tests use 'out of circulation' journals to try and create counts that persist over time
       even as the database is updated
    """
    def test_v1_searchanalysis(self):
        full_URL = base_plus_endpoint_encoded('/v1/Database/SearchAnalysis/?author=greenfield')
        response = requests.get(full_URL)
        assert(response.ok == True)
        r = response.json()
        print (r)
        response_info = r["termIndex"]["responseInfo"]
        response_set = r["termIndex"]["responseSet"] 
        assert(response_set[0]["termCount"] >= 6)
        print (response_set)
        # Confirm that the request-response cycle completed successfully.       

    def test_v2_searchanalysis(self):
        full_URL = base_plus_endpoint_encoded('/v2/Database/SearchAnalysis/?author=rangell&fulltext1=transference&soucecode=AOP')
        response = requests.get(full_URL)
        assert(response.ok == True)
        r = response.json()
        print (r)
        response_info = r["termIndex"]["responseInfo"]
        response_set = r["termIndex"]["responseSet"] 
        print (f"Term: {response_set[0]['term']} Count: {response_set[0]['termCount']}")
        assert(response_set[0]["termCount"] >= 38847)
        assert(response_set[1]["termCount"] >= 132)
        print (response_set)
        # Confirm that the request-response cycle completed successfully.       

    def test_v2_searchanalysis_author_and_journalcode(self):
        full_URL = base_plus_endpoint_encoded('/v2/Database/SearchAnalysis/?author=tuckett&sourcecode=AOP')
        response = requests.get(full_URL)
        assert(response.ok == True)
        r = response.json()
        response_info = r["termIndex"]["responseInfo"]
        response_set = r["termIndex"]["responseSet"]
        print (f"Term: {response_set[0]['term']} Count: {response_set[0]['termCount']}")
        print (f"Term: {response_set[1]['term']} Count: {response_set[1]['termCount']}")
        term0 = r["termIndex"]["responseSet"][0]["term"]
        assert(term0 == '(AOP) (in source)')
        assert(r["termIndex"]["responseSet"][0]["termCount"] == 631)
        term1 = r["termIndex"]["responseSet"][1]["term"]
        assert(term1 == '(art_authors_text:(tuckett) || art_authors_citation:(tuckett))')
        assert(r["termIndex"]["responseSet"][1]["termCount"] >= 59)

    def test_v2_searchanalysis_author_and_journalcode_and_paratext(self):
        full_URL = base_plus_endpoint_encoded('/v2/Database/SearchAnalysis/?sourcecode=BAP&paratext=freud%20psychoanalysis')
        response = requests.get(full_URL)
        r = response.json()
        assert(response.ok == True)
        #print (r)
        response_info = r["termIndex"]["responseInfo"]
        response_set = r["termIndex"]["responseSet"]
        print (f"Term: {response_set[0]['term']} Count: {response_set[0]['termCount']}")
        print (f"Term: {response_set[1]['term']} Count: {response_set[1]['termCount']}")
        term0 = r["termIndex"]["responseSet"][0]["term"]
        assert(term0 == 'freud psychoanalysis')
        assert(r["termIndex"]["responseSet"][0]["termCount"] >= 19000)
        term1 = r["termIndex"]["responseSet"][1]["term"]
        assert(term1 == '(BAP) (in source)')
        assert(r["termIndex"]["responseSet"][1]["termCount"] >= 403)

    def test_v2_searchanalysis_author_and_journalcode_and_text(self):
        full_URL = base_plus_endpoint_encoded('/v2/Database/SearchAnalysis/?sourcecode=PCT&citecount=3')
        response = requests.get(full_URL)
        assert(response.ok == True)
        r = response.json()
        #print (r)
        response_info = r["termIndex"]["responseInfo"]
        response_set = r["termIndex"]["responseSet"] 
        print (f"Term: {response_set[0]['term']} Count: {response_set[0]['termCount']}")
        print (f"Term: {response_set[1]['term']} Count: {response_set[1]['termCount']}")
        term0 = r["termIndex"]["responseSet"][0]["term"]
        assert(term0 == '(PCT) (in source)')
        assert(r["termIndex"]["responseSet"][0]["termCount"] == 482)
        term1 = r["termIndex"]["responseSet"][1]["term"]
        assert(term1 == '[3 TO *] (in cited, cited in the last 5 years)')
        assert(r["termIndex"]["responseSet"][1]["termCount"] >= 2322)

    def test_v2_searchanalysis_author_and_journalcode_and_text_and_articletype(self):
        full_URL = base_plus_endpoint_encoded('/v2/Database/SearchAnalysis/?volume=2')
        response = requests.get(full_URL)
        assert(response.ok == True)
        r = response.json()
        response_info = r["termIndex"]["responseInfo"]
        response_set = r["termIndex"]["responseSet"] 
        print (f"Term: {response_set[0]['term']} Count: {response_set[0]['termCount']}")
        term0 = r["termIndex"]["responseSet"][0]["term"]
        assert(r["termIndex"]["responseSet"][0]["termCount"] >= 2622)

if __name__ == '__main__':
    unittest.main()
    