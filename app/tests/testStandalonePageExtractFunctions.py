#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Third-party imports...
#from nose.tools import assert_true

#  This test module is in development...

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
import opasAPISupportLib
import opasConfig
import opasQueryHelper
import opasXMLHelper
import opasCentralDBLib
import models

from unitTestConfig import base_api, base_plus_endpoint_encoded
# from main import app

# client = TestClient(app)

ocd = opasCentralDBLib.opasCentralDB()

class TestStandalonePageExtractFunctions(unittest.TestCase):
    """
    Tests
    
    Note: tests are performed in alphabetical order, hence the function naming
          with forced order in the names.
    
    """
    
    def test_0a_get_article_first_page_data_html_INCOMPLETE(self):
        """
        Retrieve an article; extract first page
        """
        # This old function wasn't used by the code otherwise so removed this call
        #  it retrieves an article but doesn't include search highlighting.
        # data = opasAPISupportLib.get_article_data("ANIJP-DE.009.0189A", fields=None)
        # this newer function includes the search parameters if there were some
        xmlstr = opasXMLHelper.xml_file_to_xmlstr(r"X:\_PEPA1\_PEPa1v\_PEPArchive\AOP\014\AOP.014.0125A(bEXP_ARCH1).XML", dtd_validations=False)
        htmlpages = opasXMLHelper.xml_get_pages_html(xmlstr, offset=0, limit=1, inside="div[@id='body']", env="body", pagebrk="div[@class='pagebreak']", pagenbr="p[@class='pagenumber']")
        extract_size = len(htmlpages)
        orig_size = len(xmlstr)
        print ("warning: test development incomplete. TODO")
        # assert (xmlpages == "")
        
    def test_1a_get_article_first_page_data_INCOMPLETE(self):
        """
        Retrieve an article; extract first page
        """
        # This old function wasn't used by the code otherwise so removed this call
        #  it retrieves an article but doesn't include search highlighting.
        # data = opasAPISupportLib.get_article_data("ANIJP-DE.009.0189A", fields=None)
        # this newer function includes the search parameters if there were some
        xmlstr = opasXMLHelper.xml_file_to_xmlstr(r"X:\_PEPA1\_PEPa1v\_PEPArchive\AOP\014\AOP.014.0125A(bEXP_ARCH1).XML", dtd_validations=False)
        xmlpages = opasXMLHelper.xml_get_pages(xmlstr, 1, 1, inside="body", env="pepkbd3", remove_tags=["meta"])
        extract_size = len(xmlpages)
        orig_size = len(xmlstr)
        print (extract_size < orig_size, extract_size, orig_size)
        print ("warning: test development incomplete. TODO")
        # assert (xmlpages == "")
        
    def test_1b_get_article_data(self):
        """
        Retrieve an article; make sure it's there and the abstract len is not 0
        """
        # This old function wasn't used by the code otherwise so removed this call
        #  it retrieves an article but doesn't include search highlighting.
        # data = opasAPISupportLib.get_article_data("ANIJP-DE.009.0189A", fields=None)
        # this newer function includes the search parameters if there were some
        data = opasAPISupportLib.documents_get_document("LU-AM.029B.0202A")
        # Confirm that the request-response cycle completed successfully.
        assert (data.documents.responseInfo.fullCount == 1)
        assert (data.documents.responseSet[0].documentID == 'LU-AM.029B.0202A')
        assert (len(data.documents.responseSet[0].abstract)) > 0

        
if __name__ == '__main__':
    unittest.main()
    print ("Tests Complete.")