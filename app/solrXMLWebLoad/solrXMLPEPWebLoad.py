#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=C0321,C0103,C0301,E1101,C0303,E1004,C0330,R0915,R0914,W0703,C0326
print(
    """ 
    OPAS - Open Publications-Archive Software - Document, Authors, and References Core Loader
    
        Load articles into one Solr core and extract individual references from
        the bibliography into a second Solr core.
        
        This data loader is specific to PEP Data and Bibliography schemas but can 
        serve as a model or framework for other schemas
        
        Example Invocation:
        
                $ python solrXMLPEPWebLoad.py
        
                Use -h for help on arguments.
                
                (Requires Python 3.7)
        
    """
)

__author__      = "Neil R. Shapiro"
__copyright__   = "Copyright 2020, Psychoanalytic Electronic Publishing"
__license__     = "Apache 2.0"
__version__     = "2020.07.23"
__status__      = "Development"

#Revision Notes:
    #2019.0516  # Added command line options to specify a different path for PEPSourceInfo.json
                # Added error logging using python's built-in logging library default INFO level - nrs

    #2019.0605  # added int fields for year as they are needeed to do faceting ranges (though that's
                # beginning to be unclear) - nrs

    #2019.0705  # added citedCounts processing to load the Solr core from the mySQL database 
                # table which calculates these. - nrs

    #2019.1231  # Support remote datbase tunnel.  Fix use of SQL when not using SQLite.

    #2020.0105  # Some fields marked xml were being loaded as text...fixed.

    #2020.0223  # Populate biblio table.

    #2020.0224  # Insert a summary excerpt to new Solr field art_excerpt, so server doesn't have to spend time extracting at runtime.
                # currently, it can be either XML or HTML but should change it to one or the other to make it more consistent.
                # (though the server now handles it this way fine, converting to HTML on output when necessary.)
                # Starting to convert this to snake_case, per "pythonic-style".  But will put in more effort
                # on this later
                 
    #2020.0303  # Complete code to populate new api_articles and api_biblioxml tables which replace the ones 
                # copied from the XML processing pepa1db tables.  This eliminates the need for the filetracking table
                # since the file tracking can now be done in the api_articles table.  Run through fixes with new
                # database load, adjusting schema to accomodate the sometimes oddball data in the instances.
                # Finished new code to extract first page summaries, the old algorithm wasn't working properly 
                # across the database.  In this case, the new method using libxml's parseXML had some of it's
                # own issues because it automatically translated all entities, making it unsafe output for HTML.
                # Fixed though easily by catching those characters in the event framework.
                # Will remove the now unused code next build after it gets put into the repository for longer term
                # storage and study.
    
    #2020.0305  # Optimize performance, especially file discovery.  Set up tp compare against Solr dates rather than 
                # MySQL because that way you make sure the articles are in Solr, which is most important.
                # General cleanup and another pass at camelCase to snake_case conversion
                 
    #2020.0326  # Needed to set lang attribute from p up the ancestors in order to find all paragraphs in a particular
                # language when the lang attribute could be local or inherited at intermediate (e.g., section), levels
                # even.  It's a shame it's not done by default in lxml.

    #2020.0330  # Removing the bibliocore code (commented out for now).  Instead the biblio will be managed simply in the
                # database

    #2020.0413  # Changed the way it checks for modified files...was in MySQL records but set it to use Solr file date instead
                # because it makes less sense to have one mySQL database per solr database.  This way, we can actually check
                # if that version of the file is in Solr.  (You don't know by checking mysql, especially if the database/solr
                # relation isn't one-to-one.)
                # 
                # Also: Added new options:
                # --before
                #     looks at file date, was it created before this date (use YYYY-MM-DD format)
                # --after
                #     looks at file date, was it created after this date (use YYYY-MM-DD format)
                # --reloadbefore
                #     looks at updated (load) date IN SOLR, was it loaded into solr before this date (use YYYY-MM-DD format)
                # --reloadafter
                #     looks at updated (load) date IN SOLR, was it loaded into solr after this date (use YYYY-MM-DD format)
    
    #2020.0423  # Changes to excerpting in opasXMLHelper which affect loading, since that's when excerpts happen.

    #2020.0424  # Added stop words to highlighted terms list.  Stop words in file opasConfig.HIGHLIGHT_STOP_WORDS_FILE 
                # Changed it so highlighted terms would have tagging stripped.
                # Verbose option -v removed.  Must use --verbose instead

    #2020.0425  # Changed from highlighted words collecting <i> and <b> to collecting <impx>, which are glossary terms. 

    #2020.0425  # Added --only option to match other PEP processing software for single file mode.  (-d still works as well)
                # fixed variable name problem in the error report when the file wasn't found.

    #2020.0507  # Added art_pgcount and art_isbn to masterPEPWebDocsSchema and manually added them to Solr to match.
                # Added code to load these data.
                 
    #2020.0529  # Added updates(!) to the docs database, allowing views to be included and updated with the weekly
                # Use the -v option to turn it on.  It will add data for any document that was viewed n the last month
                # during updates.  No user option to force the whole database, but it can be done easily by a one line
                # code tweak.
                # 
                # Note that Solr 8.5 is very tricky about updating db's with child documents that started after 8.2,
                # but it works as long as you just give the art_id (I tried adding art_level when I first got the error,
                # but that didn't work on 8.5.  To get it to work, I had to more closely follow the definitions for
                # the schema, with basically only doc_values defined.

    #2020.0603  # Moved the options out of main function to the implied main area at the end of the file 
                #  (start of code processing).
                # Added a highlighted area to show what database and core will be updated, and prompt the user
                #  to ensure they want to continue.  This was done to prevent doing updates accidentally to
                #  a production system when in fact it was meant for staging.
                # Fixed a bug in the solr lookup of filenames to determine updates needed: was not escaping filename chars
                #  that need to be escaped for solr, like ( and )
                
    #2020.0709  # Updates for schema changes

    #2020.0723  # Change author core field authors (multivalued) to art_author_id_list.  The author record
                #  is for a specific author, but this is the set of authors for that paper.

    #2020.0814  # Changes to schema reflected herein...particularly the bib fields in the solrdocscore, since
                # those are mainly for faceting.  Also, docvalues=true was causing fields to show up in results
                # when I wanted those fields hidden, so went to uninvertible instead.


# Disable many annoying pylint messages, warning me about variable naming for example.
# yes, in my Solr code I'm caught between two worlds of snake_case and camelCase.

import sys
sys.path.append('../libs')
sys.path.append('../config')
sys.path.append('../libs/configLib')
import re
import os
import os.path
# import ntpath # note: if dealing with Windows path names on Linux, use ntpath instead)
import time
import string

import logging
logger = logging.getLogger(__name__)

import urllib.request, urllib.parse, urllib.error
import random
import pysolr

import modelsOpasCentralPydantic

# Python 3 code in this block
from io import StringIO

# used this name because later we needed to refer to the module, and datetime is also the name
#  of the import from datetime.
import datetime as dtime 
# import datetime
from datetime import datetime
import dateutil
import dateutil.parser

from optparse import OptionParser

from lxml import etree
#now uses pysolr exclusively!
# import solrpy as solr 
import pymysql

import config
import opasConfig
import opasCoreConfig
from opasCoreConfig import solr_authors, solr_gloss

# from OPASFileTrackerMySQL import FileTracker, FileTrackingInfo
import opasXMLHelper as opasxmllib
import opasCentralDBLib
import opasGenSupportLib as opasgenlib
import localsecrets

def read_stopwords(): 
    with open(opasConfig.HIGHLIGHT_STOP_WORDS_FILE) as f:
        stopWordList = f.read().splitlines()
    
    stopPattern = "<[ib]>[A-Z]</[ib]>"
    for n in stopWordList:
        stopPattern += f"|<[ib]>{n}</[ib]>"

    ret_val = re.compile(stopPattern, re.IGNORECASE)
    return ret_val

# Module Globals
gCitedTable = dict() # large table of citation counts, too slow to run one at a time.
bib_total_reference_count = 0
rc_stopword_match = read_stopwords() # returns compile re for matching stopwords 

def strip_tags(value, compiled_tag_pattern):
    """
    Strip tags matching the compiled_tag_pattern.
    
    """
    ret_val = value
    m = compiled_tag_pattern.match(value)
    if m:
        ret_val = m.group("word")
        if ret_val == None:
            ret_val = "pagebreak"
        ret_val = ret_val.translate(str.maketrans('','', '!"#$%&\'()*+,./:;<=>?@[\\]^_`{|}~'))

    return ret_val

def remove_values_from_terms_highlighted_list(the_list, remove_stop_words=True, start_tag_pattern = "<(i|b|bi|bui|fi|impx[^>]*?)>", end_tag_pattern="</(i|b|bi|bui|impx|fi)>"):
    """
    Using the list of stop words read in at initialization, remove these from the words used for highlighted lists.
    
    >> remove_values_from_terms_highlighted_list(["<i>not</i>","<i>is</i>","<i>and</i>", "<i>she</i>", "<i>The Interpretation of Dreams</i>", "<i>will</i>", "<i>I</i>", "<i>be</i>" ])
    ['The Interpretation of Dreams']
    """
    stripPattern = f".*<pb>.*|({start_tag_pattern}[\s\n\t]*)+(?P<word>[^<]+?)[\s\n]*({end_tag_pattern})+"
    cStripPattern = re.compile(stripPattern, re.IGNORECASE)
    # passing the compiled pattern saves from recompiling for every value in function
    if remove_stop_words:
        return [strip_tags(value, compiled_tag_pattern = cStripPattern) for value in the_list if not rc_stopword_match.match(value)]
    else:
        return [strip_tags(value, compiled_tag_pattern = cStripPattern) for value in the_list]

def find_all(name_pat, path):
    result = []
    name_patc = re.compile(name_pat, re.IGNORECASE)
    for root, dirs, files in os.walk(path):
        for filename in files:
            if name_patc.match(filename):
                result.append(os.path.join(root, filename))
    return result

def non_empty_string(strval):
    try:
        return strval if strval != "" else None
    except Exception as e:
        return None
        

class NewFileTracker(object):
    """
    >>> ocd =  opasCentralDBLib.opasCentralDB()
    >>> ft = NewFileTracker(ocd)
    >>> fsel = r"X:\\_PEPA1\\_PEPa1v\\_PEPArchive\\IJP\\043\\IJP.043.0306A(bEXP_ARCH1).XML"
    >>> ft.load_fs_fileinfo(fsel)
    >>> ft.is_refresh_needed(filename=fsel)
    False
    >>> ft.is_refresh_needed(filename=fsel, before_date="2020-03-01")
    True
    >>> ft.is_refresh_needed(filename=fsel, after_date="2019-01-01")
    True
    >>> ft.is_refresh_needed(filename=fsel, after_date="2020-03-01")
    False
    >>> ft.is_refresh_needed(filename=fsel, before_date="2019-01-01")
    False
    >>> ft.is_refresh_needed(filename=fsel, after_date="2020-03-01")
    False
    >>> ft.is_refresh_needed(filename=fsel, before_date="2019-01-01")
    False
    
    
    """
    #----------------------------------------------------------------------------------------
    def __init__(self, ocd):
        self.filename = ""
        self.ocd = ocd
        self.fileModDate = None
        self.fileSize = 0
        self.buildDate = None
        self.conn = self.ocd.open_connection(caller_name="FileTracker")
        self.fullfileset = {}
        self.file_set = {}
        
    #----------------------------------------------------------------------------------------
    def close(self):
        self.conn = self.ocd.close_connection(caller_name="FileTracker")

    #------------------------------------------------------------------------------------------------------
    def load_fs_fileinfo(self, filename):
        """
        Load key info for file of interest
        """
        if os.path.exists(filename):
            self.filename = filename
            self.base_filename = os.path.basename(filename)
            self.timestamp_str = datetime.utcfromtimestamp(os.path.getmtime(filename)).strftime(localsecrets.TIME_FORMAT_STR)
            self.timestamp_obj = datetime.strptime(self.timestamp_str, localsecrets.TIME_FORMAT_STR)
            self.fileSize = os.path.getsize(filename)
            self.buildDate = time.time()

    #------------------------------------------------------------------------------------------------------
    def is_refresh_needed(self, filename, before_date=None, after_date=None):
        """
        Compare the file's date with whichever is specified
           1) before_date: is it before a specified date
           2) after_date: is it after a specified date
        if neither of those specified:
           3) db_date: is the file newer
        
        """
        ret_val = False
        self.load_fs_fileinfo(filename)

        if before_date is not None:
            before_obj = dateutil.parser.parse(before_date)
            if self.timestamp_obj < before_obj:
                ret_val = True

        if after_date is not None:
            after_obj = dateutil.parser.parse(after_date)
            if self.timestamp_obj > after_obj:
                ret_val = True

        if before_date is None and after_date is None: # check database updated and 
            getFileInfoSQL = """
                                SELECT
                                   art_id,
                                   filename,
                                   filedatetime,
                                   updated
                                FROM api_articles
                                WHERE filename = %s
                            """
            try:
                c = self.ocd.db.cursor(pymysql.cursors.DictCursor)
                c.execute(getFileInfoSQL, self.base_filename)
                row = c.fetchone()
                if row == None:
                    # no database record here, so newer by default
                    ret_val = True
                else:
                    self.db_fileinfo = row
                    
            except pymysql.Error as e:
                print(e)
                ret_val = False
            else:
                if self.db_fileinfo["filedatetime"] < self.timestamp_str:
                    ret_val = True
            
            c.close()  # close cursor

        return ret_val

    #------------------------------------------------------------------------------------------------------
    def is_load_date_before_or_after(self, before=None, after=None):
        """
        To allow updating (reloading) files before or after a date, compare the date updated
        in the database to the before or after time passed in from args.
        
        Note that this uses the timestamp on the database record rather than the file mod date.
        
        """
        ret_val = False
        # lookup the current file from the fullset (no db access needed)
        files_db_record = self.fullfileset.get(self.base_filename, None)

        if before is not None:
            before_obj = dateutil.parser.parse(before)
            before_time = True
        else:
            before_time = False
        
        if after is not None:
            after_obj = dateutil.parser.parse(after)
            after_time = True
        else:
            after_time = False
            
        if files_db_record is not None:
            # it's in the database
            db_timestamp_obj = files_db_record.get("updated", None)
            # stored format is human readable, UTC time, eg. 2020-02-24T00:41:53Z, per localsecrets.TIME_FORMAT_STR
            if db_timestamp_obj is not None:
                # default return False, not modified
                ret_val = False
                if before_time:
                    if db_timestamp_obj < before_obj:
                        # file is modified
                        # print ("File is considered modified: %s.  %s > %s" % (curr_fileinfo.filename, curr_fileinfo.timestamp_str, db_timestamp_str))
                        ret_val = True
                if after_time:
                    if db_timestamp_obj > after_obj:
                        # file is modified
                        # print ("File is considered modified: %s.  %s > %s" % (curr_fileinfo.filename, curr_fileinfo.timestamp_str, db_timestamp_str))
                        ret_val = True
            else: # db record has no value for timestamp, so consider modified
                ret_val = True
        else:
            ret_val = True # no record of it, so effectively modified.
    
        return ret_val

class ExitOnExceptionHandler(logging.StreamHandler):
    """
    Allows us to exit on serious error.
    """
    def emit(self, record):
        super().emit(record)
        if record.levelno in (logging.ERROR, logging.CRITICAL):
            raise SystemExit(-1)


class BiblioEntry(object):
    """
    An entry from a documents bibliography.
    
    Used to populate the MySQL table api_biblioxml for statistical gathering
       and the Solr core pepwebrefs for searching in special cases.
    
    """
    def __init__(self, artInfo, ref):
        self.ref_entry_xml = etree.tostring(ref, with_tail=False)
        if self.ref_entry_xml is not None:
            self.ref_entry_xml = self.ref_entry_xml.decode("utf8") # convert from bytes
        self.ref_entry_text = opasxmllib.xml_elem_or_str_to_text(ref)
        self.art_id = artInfo.art_id
        self.art_year_int = artInfo.art_year_int
        self.ref_local_id= opasxmllib.xml_get_element_attr(ref, "id")
        self.ref_id = artInfo.art_id + "." + self.ref_local_id
        self.ref_title = opasxmllib.xml_get_subelement_textsingleton(ref, "t")
        self.ref_title = self.ref_title[:1023]
        self.pgrg = opasxmllib.xml_get_subelement_textsingleton(ref, "pp")
        self.pgrg = opasgenlib.first_item_grabber(self.pgrg, re_separator_ptn=";|,", def_return=self.pgrg)
        self.pgrg = self.pgrg[:23]
        self.rx = opasxmllib.xml_get_element_attr(ref, "rx", default_return=None)
        self.rxcf = opasxmllib.xml_get_element_attr(ref, "rxcf", default_return=None) # related rx
        if self.rx is not None:
            self.rx_sourcecode = re.search("(.*?)\.", self.rx, re.IGNORECASE).group(1)
        else:
            self.rx_sourcecode = None
        self.volume = opasxmllib.xml_get_subelement_textsingleton(ref, "v")
        self.volume = self.volume[:23]
        self.source_title = opasxmllib.xml_get_subelement_textsingleton(ref, "j")
        self.publishers = opasxmllib.xml_get_subelement_textsingleton(ref, "bp")
        self.publishers = self.publishers[:254]
        if self.publishers != "":
            self.source_type = "book"
        else:
            self.source_type = "journal"

        if self.source_type == "book":
            self.year_of_publication = opasxmllib.xml_get_subelement_textsingleton(ref, "bpd")
            if self.year_of_publication == "":
                self.year_of_publication = opasxmllib.xml_get_subelement_textsingleton(ref, "y")
            if self.source_title is None or self.source_title == "":
                # sometimes has markup
                self.source_title = opasxmllib.xml_get_direct_subnode_textsingleton(ref, "bst")  # book title
        else:
            self.year_of_publication = opasxmllib.xml_get_subelement_textsingleton(ref, "y")
         
        if self.year_of_publication != "":
            # make sure it's not a range or list of some sort.  Grab first year
            self.year_of_publication = opasgenlib.year_grabber(self.year_of_publication)
        else:
            # try to match
            try:
                self.year_of_publication = re.search(r"\(([A-z]*\s*,?\s*)?([12][0-9]{3,3}[abc]?)\)", self.ref_entry_xml).group(2)
            except Exception as e:
                logger.warning("no match %s/%s/%s" % (self.year_of_publication, ref, e))
            
        self.year_of_publication_int = 0
        if self.year_of_publication != "" and self.year_of_publication is not None:
            self.year_of_publication = re.sub("[^0-9]", "", self.year_of_publication)
            if self.year_of_publication != "" and self.year_of_publication is not None:
                try:
                    self.year_of_publication_int = int(self.year_of_publication[0:4])
                except ValueError as e:
                    logger.warning("Error converting year_of_publication to int: %s / %s.  (%s)" % (self.year_of_publication, self.ref_entry_xml, e))
                except Exception as e:
                    logger.warning("Error trying to find untagged bib year in %s (%s)" % (self.ref_entry_xml, e))
            else:
                logger.warning("Non-numeric year of pub: %s" % (self.ref_entry_xml))

        self.year = self.year_of_publication

        if self.year != "" and self.year is not None:
            self.year_int = int(self.year)
        else:
            self.year_int = "Null"
            
        self.author_name_list = [etree.tostring(x, with_tail=False).decode("utf8") for x in ref.findall("a") if x is not None]
        self.authors_xml = '; '.join(self.author_name_list)
        self.authors_xml = self.authors_xml[:2040]
        self.author_list = [opasxmllib.xml_elem_or_str_to_text(x) for x in ref.findall("a") if opasxmllib.xml_elem_or_str_to_text(x) is not None]  # final if x gets rid of any None entries which can rarely occur.
        self.author_list_str = '; '.join(self.author_list)
        self.author_list_str = self.author_list_str[:2040]

        #if artInfo.file_classification == opasConfig.DOCUMENT_ACCESS_OFFSITE: # "pepoffsite":
            ## certain fields should not be stored in returnable areas.  So full-text searchable special field for that.
            #self.ref_offsite_entry = self.bibRefEntry
            #self.bibRefEntry = None
        #else:
            #self.ref_offsite_entry = None
        
        # setup for Solr load
        #self.thisRef = {
                        #"id" : self.ref_id,
                        #"art_id" : artInfo.art_id,
                        #"file_last_modified" : artInfo.filedatetime,
                        #"file_classification" : artInfo.file_classification,
                        #"file_size" : artInfo.file_size,
                        #"file_name" : artInfo.filename,
                        #"timestamp" : artInfo.processed_datetime,  # When batch was entered into core
                        #"art_title" : artInfo.art_title,
                        #"art_sourcecode" : artInfo.src_code,
                        #"art_sourcetitleabbr" : artInfo.src_title_abbr,
                        #"art_sourcetitlefull" : artInfo.src_title_full,
                        #"art_sourcetype" : artInfo.src_type,
                        #"art_authors" : artInfo.art_all_authors,
                        #"reference_count" :artInfo.ref_count,  # would be the same for each reference in article, but could still be useful
                        #"art_year" : artInfo.art_year,
                        #"art_year_int" : artInfo.art_year_int,
                        #"art_vol" : artInfo.art_vol,
                        #"art_pgrg" : artInfo.art_pgrg,
                        #"art_lang" : artInfo.art_lang,
                        #"art_citeas_xml" : artInfo.art_citeas_xml,
                        #"text_ref" : self.ref_entry_xml,                        
                        #"text_offsite_ref": self.ref_offsite_entry,
                        #"authors" : self.author_list_str,
                        #"title" : self.ref_title,
                        #"bib_articletitle" : self.ref_title, 
                        #"bib_sourcetitle" : self.source_title,
                        #"bib_authors_xml" : self.authors_xml,
                        #"bib_ref_id" : self.ref_id,
                        #"bib_ref_rx" : self.rx,
                        #"bib_ref_rxcf" : self.rxcf, # the not 
                        #"bib_ref_rx_sourcecode" : self.rx_sourcecode,
                        #"bib_sourcetype" : self.source_type,
                        #"bib_pgrg" : self.pgrg,
                        #"bib_year" : self.year_of_publication,
                        #"bib_year_int" : self.year_int,
                        #"bib_volume" : self.volume,
                        #"bib_publisher" : self.publishers
                      #}


class ArticleInfo(object):
    """
    An entry from a documents metadata.
    
    Used to populate the MySQL table api_articles for relational type querying
       and the Solr core pepwebdocs for full-text searching (and the majority of
       client searches.

    """
    def __init__(self, sourceinfodb_data, pepxml, art_id, logger):
        # let's just double check artid!
        self.art_id = None
        self.art_id_from_filename = art_id # file name will always already be uppercase (from caller)
        self.bk_subdoc = None
        self.bk_seriestoc = None

        # Just init these.  Creator will set based on filename
        self.file_classification = None
        self.file_size = 0  
        self.filedatetime = ""
        self.filename = ""

        # now, the rest of the variables we can set from the data
        self.processed_datetime = datetime.utcfromtimestamp(time.time()).strftime(localsecrets.TIME_FORMAT_STR)
        try:
            self.art_id = opasxmllib.xml_xpath_return_textsingleton(pepxml, "//artinfo/@id", None)
            if self.art_id is None:
                self.art_id = self.art_id_from_filename
            else:
                # just to watch for xml keying or naming errors
                if self.art_id_from_filename != self.art_id:
                    logger.warning("File name ID tagged and artID disagree.  %s vs %s", self.art_id, self.art_id_from_filename)
                    self.art_id = self.art_id_from_filename
                    
            # make sure it's uppercase
            self.art_id = self.art_id.upper()
                
        except Exception as err:
            logger.warning("Issue reading file's article id. (%s)", err)

        # Containing Article data
        #<!-- Common fields -->
        #<!-- Article front matter fields -->
        #---------------------------------------------
        artinfo_xml = pepxml.xpath("//artinfo")[0] # grab full artinfo node, so it can be returned in XML easily.
        self.artinfo_xml = etree.tostring(artinfo_xml).decode("utf8")
        self.src_code = pepxml.xpath("//artinfo/@j")[0]
        try:
            self.src_code = self.src_code.upper()  # 20191115 - To make sure this is always uppercase
            self.src_title_abbr = sourceinfodb_data[self.src_code].get("sourcetitleabbr", None)
            self.src_title_full = sourceinfodb_data[self.src_code].get("sourcetitlefull", None)
            self.src_type = sourceinfodb_data[self.src_code].get("product_type", None)  # journal, book, video...
            self.src_embargo = sourceinfodb_data[self.src_code].get("wall", None)
        except KeyError as err:
            self.src_title_abbr = None
            self.src_title_full = None
            if self.src_code in ["ZBK"]:
                self.src_type = "book"
            else:           
                self.src_type = None
                
            self.src_embargo = None
            logger.warning("Error: PEP Source %s not found in source info db.  Use the 'PEPSourceInfo export' after fixing the issn table in MySQL DB", self.src_code)
        except Exception as err:
            logger.error("Error: Problem with this files source info. File skipped. (%s)", err)
            #processingErrorCount += 1
            return

        vol_actual = opasxmllib.xml_xpath_return_textsingleton(pepxml, '//artinfo/artvol/@actual', default_return=None)
        self.art_vol_str = opasxmllib.xml_xpath_return_textsingleton(pepxml, '//artinfo/artvol/node()', default_return=None)
        m = re.match("(\d+)([A-Z]*)", self.art_vol_str)
        if m is None:
            logger.error(f"Bad Vol # in element content: {self.art_vol_str}")
            m = re.match("(\d+)([A-z\-\s]*)", vol_actual)
            if m is not None:
                self.art_vol_int = m.group(1)
                logger.error(f"Recovered Vol # from actual attr: {self.art_vol_int}")
            else:
                raise ValueError("Severe Error in art_vol")
        else:
            self.art_vol_int = m.group(1)
            if len(m.groups()) == 2:
                art_vol_suffix = m.group(2)

        # now convert to int
        try:
            self.art_vol_int = int(self.art_vol_int)
        except ValueError:
            logger.warning(f"Can't convert art_vol to int: {self.art_vol_int} Error: {e}")
            art_vol_suffix = self.art_vol_int[-1]
            art_vol_ints = re.findall(r'\d+', self.art_vol_str)
            if len(art_vol_ints) >= 1:
                self.art_vol_int = art_vol_ints[1]
                self.art_vol_int = int(self.art_vol_int)
        except Exception as e:
            logger.warning(f"Can't convert art_vol to int: {self.art_vol_int} Error: {e}")

        if vol_actual is not None:
            self.art_vol_str = vol_actual
            
        self.art_issue = opasxmllib.xml_xpath_return_textsingleton(pepxml, '//artinfo/artiss/node()', default_return=None)
        self.art_issue_title = opasxmllib.xml_xpath_return_textsingleton(pepxml, '//artinfo/artissinfo/isstitle/node()', default_return=None)

        self.art_year_str = opasxmllib.xml_xpath_return_textsingleton(pepxml, '//artinfo/artyear/node()', default_return=None)
        m = re.match("(?P<yearint>[0-9]{4,4})(?P<yearsuffix>[a-zA-Z])?(\s*\-\s*)?((?P<year2int>[0-9]{4,4})(?P<year2suffix>[a-zA-Z])?)?", self.art_year_str)
        if m is not None:
            self.art_year = m.group("yearint")
            self.art_year_int = int(m.group("yearint"))
        else:
            try:
                art_year_for_int = re.sub("[^0-9]", "", self.art_year)
                self.art_year_int = int(art_year_for_int)
            except ValueError as err:
                logger.warning("Error converting art_year to int: %s", self.art_year)
                self.art_year_int = 0


        artInfoNode = pepxml.xpath('//artinfo')[0]
        self.art_type = opasxmllib.xml_get_element_attr(artInfoNode, "arttype", default_return=None)
        self.art_vol_title = opasxmllib.xml_xpath_return_textsingleton(pepxml, '//artinfo/artvolinfo/voltitle/node()', default_return=None)
        if self.art_vol_title is None:
            # try attribute for value (lower priority than element above)
            self.art_vol_title = opasxmllib.xml_get_element_attr(artInfoNode, "voltitle", default_return=None)

        # m = re.match("(?P<volint>[0-9]+)(?P<volsuffix>[a-zA-Z])", self.art_vol)
        m = re.match("(?P<volint>[0-9]+)(?P<volsuffix>[a-zA-Z])?(\s*\-\s*)?((?P<vol2int>[0-9]+)(?P<vol2suffix>[a-zA-Z])?)?", str(self.art_vol_str))
        if m is not None:
            self.art_vol_suffix = m.group("volsuffix")
            # self.art_vol = m.group("volint")
        else:
            self.art_vol_suffix = None
            
        if self.art_vol_title is not None:
            print (f"   ...Volume title: {self.art_vol_title}")
    
        if self.art_issue_title is not None:
            print (f"   ...Issue title: {self.art_issue_title}")
            
        self.art_doi = opasxmllib.xml_get_element_attr(artInfoNode, "doi", default_return=None) 
        self.art_issn = opasxmllib.xml_get_element_attr(artInfoNode, "ISSN", default_return=None) 
        self.art_isbn = opasxmllib.xml_get_element_attr(artInfoNode, "ISBN", default_return=None) 
        self.art_orig_rx = opasxmllib.xml_get_element_attr(artInfoNode, "origrx", default_return=None) 
        self.start_sectname = opasxmllib.xml_get_element_attr(artInfoNode, "newsecnm", default_return=None)
        if self.start_sectname is None:
            #  look in newer, tagged, data
            self.start_sectname = opasxmllib.xml_xpath_return_textsingleton(pepxml, '//artsectinfo/secttitle/node()', default_return=None)
        
        self.art_pgrg = opasxmllib.xml_get_subelement_textsingleton(artInfoNode, "artpgrg", default_return=None)  # note: getSingleSubnodeText(pepxml, "artpgrg")
        self.art_pgstart, self.art_pgend = opasgenlib.pgrg_splitter(self.art_pgrg)
        try:
            self.art_pgcount = int(pepxml.xpath("count(//pb)")) # 20200506
        except Exception as e:
            self.art_pgcount = 0
            
        if self.art_pgstart is not None:
            self.art_pgstart_prefix, self.art_pgstart, self.pgstart_suffix = opasgenlib.pgnum_splitter(self.art_pgstart)
        else:
            self.art_pgstart_prefix, self.art_pgstart, self.pgstart_suffix = (None, None, None)
            
        if self.art_pgend is not None:
            self.pgend_prefix, self.art_pgend, self.pgend_suffix = opasgenlib.pgnum_splitter(self.art_pgend)
        else:
            self.pgend_prefix, self.art_pgend, self.pgend_suffix = (None, None, None)

        self.art_title = opasxmllib.xml_get_subelement_textsingleton(artInfoNode, "arttitle", skip_tags=["ftnx"])
        if self.art_title == "-": # weird title in ANIJP-CHI
            self.art_title = ""

        self.art_subtitle = opasxmllib.xml_get_subelement_textsingleton(artInfoNode, 'artsub')
        if self.art_subtitle == "":
            pass
        elif self.art_subtitle is None:
            self.art_subtitle = ""
        else:
            #self.artSubtitle = ''.join(etree.fromstring(self.artSubtitle).itertext())
            if self.art_title != "":
                self.art_subtitle = ": " + self.art_subtitle
                self.art_title = self.art_title + self.art_subtitle
            else:
                self.art_title = self.art_subtitle
                self.art_subtitle = ""
                
        self.art_lang = pepxml.xpath('//pepkbd3/@lang')
        
        if self.art_lang == []:
            self.art_lang = ['EN']
        
        self.author_xml_list = pepxml.xpath('//artinfo/artauth/aut')
        self.author_xml = opasxmllib.xml_xpath_return_xmlsingleton(pepxml, '//artinfo/artauth')
        self.authors_bibliographic, self.author_list = opasxmllib.authors_citation_from_xmlstr(self.author_xml, listed=True)
        self.art_auth_citation = self.authors_bibliographic
        # ToDo: I think I should add an author ID to bib aut too.  But that will have
        #  to wait until later.
        self.art_author_id_list = opasxmllib.xml_xpath_return_textlist(pepxml, '//artinfo/artauth/aut[@listed="true"]/@authindexid')
        self.art_authors_count = len(self.author_list)
        if self.art_author_id_list == []: # no authindexid
            logger.warning("This document %s does not have an author list; may be missing authindexids" % art_id)
            self.art_author_id_list = self.author_list

        self.author_ids_str = ", ".join(self.art_author_id_list)
        self.art_auth_mast, self.art_auth_mast_list = opasxmllib.author_mast_from_xmlstr(self.author_xml, listed=True)
        self.art_auth_mast_unlisted_str, self.art_auth_mast_unlisted_list = opasxmllib.author_mast_from_xmlstr(self.author_xml, listed=False)
        self.art_auth_count = len(self.author_xml_list)
        self.art_author_lastnames = opasxmllib.xml_xpath_return_textlist(pepxml, '//artinfo/artauth/aut[@listed="true"]/nlast')
        
        self.art_all_authors = self.art_auth_mast + " (" + self.art_auth_mast_unlisted_str + ")"
        self.art_kwds = opasxmllib.xml_xpath_return_textsingleton(pepxml, "//artinfo/artkwds/node()", None)

        # Usually we put the abbreviated title here, but that won't always work here.
        self.art_citeas_xml = u"""<p class="citeas"><span class="authors">%s</span> (<span class="year">%s</span>) <span class="title">%s</span>. <span class="sourcetitle">%s</span> <span class="pgrg">%s</span>:<span class="pgrg">%s</span></p>""" \
            %                   (self.authors_bibliographic,
                                 self.art_year,
                                 self.art_title,
                                 self.src_title_full,
                                 self.art_vol_int,
                                 self.art_pgrg)
        
        self.art_citeas_text = opasxmllib.xml_elem_or_str_to_text(self.art_citeas_xml)
        art_qual_node = pepxml.xpath("//artinfo/artqual")
        if art_qual_node != []:
            self.art_qual = opasxmllib.xml_get_element_attr(art_qual_node[0], "rx", default_return=None)
        else:
            self.art_qual = pepxml.xpath("//artbkinfo/@extract")
            if self.art_qual == []:
                self.art_qual = None 

        # will be None if not a book extract
        # self.art_qual = None
        if self.art_qual is not None:
            if isinstance(self.art_qual, list):
                self.art_qual = str(self.art_qual[0])
                
            if self.art_qual != self.art_id:
                self.bk_subdoc = True
            else:
                self.bk_subdoc = False
        else:
            self.bk_subdoc = False           

        refs = pepxml.xpath("/pepkbd3//be")
        self.bib_authors = []
        self.bib_rx = []
        self.bib_title = []
        self.bib_journaltitle = []
        
        for x in refs:
            try:
                if x.attrib["rx"] is not None:
                    self.bib_rx.append(x.attrib["rx"])
            except:
                pass
            journal = x.find("j")
            if journal is not None:
                journal_lc = opasxmllib.xml_elem_or_str_to_text(journal).lower()
                journal_lc = journal_lc.translate(str.maketrans('', '', string.punctuation))
                self.bib_journaltitle.append(journal_lc)

            title = x.find("t")
            # bib article titles for faceting, get rid of punctuation variations
            if title is not None:
                bib_title = opasxmllib.xml_elem_or_str_to_text(title)
                bib_title = bib_title.lower()
                bib_title = bib_title.translate(str.maketrans('', '', string.punctuation))
                self.bib_title.append(opasxmllib.xml_elem_or_str_to_text(title))

            title = x.find("bst")
            # bib source titles for faceting, get rid of punctuation variations
            # cumulate these together with article title
            if title is not None:
                bib_title = opasxmllib.xml_elem_or_str_to_text(title)
                bib_title = bib_title.lower()
                bib_title = bib_title.translate(str.maketrans('', '', string.punctuation))
                self.bib_title.append(bib_title)

            auths = x.findall("a")
            for y in auths:
                if opasxmllib.xml_elem_or_str_to_text(x) is not None:
                    self.bib_authors.append(opasxmllib.xml_elem_or_str_to_text(y))
        
        self.ref_count = len(refs )
        # clear it, we aren't saving it.
        refs  = None
        
        self.bk_info_xml = opasxmllib.xml_xpath_return_xmlsingleton(pepxml, "/pepkbd3//artbkinfo") # all book info in instance
        # break it down a bit for the database
        self.main_toc_id = opasxmllib.xml_xpath_return_textsingleton(pepxml, "/pepkbd3//artbkinfo/@extract", None)
        self.bk_title = opasxmllib.xml_xpath_return_textsingleton(pepxml, "/pepkbd3//bktitle", None)
        self.bk_publisher = opasxmllib.xml_xpath_return_textsingleton(pepxml, "/pepkbd3//bkpubandloc", None)
        self.bk_seriestoc = opasxmllib.xml_xpath_return_textsingleton(pepxml, "/pepkbd3//artbkinfo/@seriestoc", None)
        self.bk_next_id = opasxmllib.xml_xpath_return_textsingleton(pepxml, "//artbkinfo/@next", None)
        # hard code special cases SE/GW if they are not covered by the instances
        if self.bk_seriestoc is None:
            if self.src_code == "SE":
                self.bk_seriestoc = "SE.000.0000A"
            if self.src_code == "GW":
                self.bk_seriestoc = "GW.000.0000A"
        
#------------------------------------------------------------------------------------------------------------
#  Support functions
#------------------------------------------------------------------------------------------------------------
def process_article_for_doc_core(pepxml, artInfo, solrcon, file_xml_contents):
    """
    Extract and load data for the full-text core.  Whereas in the Refs core each
      Solr document is a reference, here each Solr document is a PEP Article.

      This core contains bib entries too, but not subfields.

      TODO: Originally, this core supported each bibliography record in its own
            json formatted structure, saved in a single field.  However, when
            the code was switched from PySolr to Solrpy this had to be removed,
            since Solrpy prohibits this for some reason.  Need to raise this
            as a case on the issues board for Solrpy.

    """
    #------------------------------------------------------------------------------------------------------
    # global gCitedTable
    
    print("   ...Processing main file content for the %s core." % opasCoreConfig.SOLR_DOCS)

    art_lang = pepxml.xpath('//@lang')
    if art_lang == []:
        art_lang = ['EN']
        

    # see if this is an offsite article
    if artInfo.file_classification == opasConfig.DOCUMENT_ACCESS_OFFSITE:
        # certain fields should not be stored in returnable areas.  So full-text searchable special field for that.
        offsite_contents = True
        offsite_ref =  """<p>This article or book is available online on a non-PEP website. 
                            Click <a href="//www.doi.org/%s" target="_blank">here</a> to open that website 
                            in another window or tab.
                            </p>
                        """ % urllib.parse.quote(artInfo.art_doi)
        summaries_xml = f"""<abs>
                            {offsite_ref}
                            </abs>
                         """
        excerpt = excerpt_xml = abstracts_xml = summaries_xml
    else:
        offsite_contents = False
        summaries_xml = opasxmllib.xml_xpath_return_xmlstringlist(pepxml, "//summaries", default_return=None)
        abstracts_xml = opasxmllib.xml_xpath_return_xmlstringlist(pepxml, "//abs", default_return=None)
        # multiple data fields, not needed, search children instead, which allows search by para
        excerpt = None
        excerpt_xml = None
        if artInfo.art_type == opasConfig.ARTINFO_ARTTYPE_TOC_INSTANCE: # "TOC"
            # put the whole thing in the abstract!  Requires some extra processing though
            #heading = opasxmllib.get_running_head( source_title=artInfo.src_title_abbr,
                                                   #pub_year=artInfo.art_year,
                                                   #vol=artInfo.art_vol,
                                                   #issue=artInfo.art_issue,
                                                   #pgrg=artInfo.art_pgrg,
                                                   #ret_format="HTML"
                                                   #)
            #pepxml.remove(pepxml.find('artinfo'))
            #pepxml.remove(pepxml.find('meta'))
            excerpt_xml = pepxml
            excerpt = opasxmllib.xml_str_to_html(excerpt_xml, transformer_name=opasConfig.TRANSFORMER_XMLTOHTML_EXCERPT)
            # excerpt = re.sub("\[\[RunningHead\]\]", f"{heading}", excerpt, count=1)
            
        else:
            # copy abstract or summary to excerpt, if not there, then generate it.
            # this is so that an app can rely on excerpt to have the abstract or excerpt (or summary)
            # TODO: later consider we could just put the excerpt in abstract instead, and make abstract always HTML.
            #       but for now, I like to be able to distinguish an original abstract from a generated one.
            if abstracts_xml is not None:
                excerpt_xml = abstracts_xml[0]
            elif summaries_xml is not None:
                excerpt_xml = summaries_xml[0]
            else:
                excerpt_xml = opasxmllib.get_first_page_excerpt_from_doc_root(pepxml)

            excerpt = opasxmllib.xml_str_to_html(excerpt_xml)
                
    excerpt_xml = opasxmllib.xml_elem_or_str_to_xmlstring(excerpt_xml, None)
    
    #art_authors_unlisted = pepxml.xpath(r'//artinfo/artauth/aut[@listed="false"]/@authindexid') 
    cited_counts = gCitedTable.get(artInfo.art_id, modelsOpasCentralPydantic.MostCitedArticles())
    # anywhere in the doc.
    children = doc_children() # new instance, reset child counter suffix
    children.add_children(stringlist=opasxmllib.xml_xpath_return_xmlstringlist_withinheritance(pepxml, "//body//p|//body//p2", attr_to_find="lang"),
                          parent_id=artInfo.art_id,
                          parent_tag="p_body",
                          default_lang=art_lang[0])
    children.add_children(stringlist=opasxmllib.xml_xpath_return_xmlstringlist_withinheritance(pepxml, "//h1|//h2|//h3|//h4|//h5|//h6", attr_to_find="lang"),
                          parent_id=artInfo.art_id,
                          parent_tag="p_heading",
                          default_lang=art_lang[0])
    children.add_children(stringlist=opasxmllib.xml_xpath_return_xmlstringlist_withinheritance(pepxml, "//quote//p|//quote//p2", attr_to_find="lang"),
                          parent_id=artInfo.art_id,
                          parent_tag="p_quote",
                          default_lang=art_lang[0])
    children.add_children(stringlist=opasxmllib.xml_xpath_return_xmlstringlist_withinheritance(pepxml, "//dream//p|//dream//p2", attr_to_find="lang"),
                          parent_id=artInfo.art_id,
                          parent_tag="p_dream",
                          default_lang=art_lang[0])
    children.add_children(stringlist=opasxmllib.xml_xpath_return_xmlstringlist_withinheritance(pepxml, "//poem//p|//poem//p2", attr_to_find="lang"),
                          parent_id=artInfo.art_id,
                          parent_tag="p_poem",
                          default_lang=art_lang[0])
    children.add_children(stringlist=opasxmllib.xml_xpath_return_xmlstringlist_withinheritance(pepxml, "//note//p|//note//p2", attr_to_find="lang"),
                          parent_id=artInfo.art_id,
                          parent_tag="p_note",
                          default_lang=art_lang[0])
    children.add_children(stringlist=opasxmllib.xml_xpath_return_xmlstringlist_withinheritance(pepxml, "//dialog//p|//dialog//p2", attr_to_find="lang"),
                          parent_id=artInfo.art_id,
                          parent_tag="p_dialog",
                          default_lang=art_lang[0])
    children.add_children(stringlist=opasxmllib.xml_xpath_return_xmlstringlist_withinheritance(pepxml, "//panel//p|//panel//p2", attr_to_find="lang"),
                          parent_id=artInfo.art_id,
                          parent_tag="p_panel",
                          default_lang=art_lang)
    children.add_children(stringlist=opasxmllib.xml_xpath_return_xmlstringlist_withinheritance(pepxml, "//caption//p", attr_to_find="lang"),
                          parent_id=artInfo.art_id,
                          parent_tag="p_caption",
                          default_lang=art_lang[0])
    children.add_children(stringlist=opasxmllib.xml_xpath_return_xmlstringlist_withinheritance(pepxml, "//bib//be|//binc", attr_to_find="lang"),
                          parent_id=artInfo.art_id,
                          parent_tag="p_bib",
                          default_lang=art_lang[0])
    children.add_children(stringlist=opasxmllib.xml_xpath_return_xmlstringlist_withinheritance(pepxml, "//appxs//p|//appxs//p2", attr_to_find="lang"),
                          parent_id=artInfo.art_id,
                          parent_tag="p_appxs",
                          default_lang=art_lang[0])
    # summaries and abstracts
    children.add_children(stringlist=opasxmllib.xml_xpath_return_xmlstringlist_withinheritance(pepxml, "//summaries//p|//summaries//p2|//abs//p|//abs//p2", attr_to_find="lang"),
                          parent_id=artInfo.art_id,
                          parent_tag="p_summaries",
                          default_lang=art_lang[0])

    # indented status
    print (f"   ...Adding children, tags/counts: {children.tag_counts}")
    art_kwds_str = opasgenlib.string_to_list(artInfo.art_kwds)
    terms_highlighted = opasxmllib.xml_xpath_return_xmlstringlist(pepxml, "//body/*/b|//body/*/i|//body/*/bi|//body/*/bui")
                        #opasxmllib.xml_xpath_return_xmlstringlist(pepxml, "//body/*/i") 
    terms_highlighted = remove_values_from_terms_highlighted_list(terms_highlighted)
    # include pep dictionary marked words
    glossary_terms_list = opasxmllib.xml_xpath_return_xmlstringlist(pepxml, "//body/*/impx")
    # strip the tags, but keep stop words
    glossary_terms_list = remove_values_from_terms_highlighted_list(glossary_terms_list, remove_stop_words=False)
    
    glossary_group_terms = pepxml.xpath("//body/*/impx/@grpname")
    glossary_group_terms_list = []
    if glossary_group_terms is not None:
        for n in glossary_group_terms:
            glossary_group_terms_list += opasgenlib.string_to_list(n, sep=";")
    freuds_italics = opasxmllib.xml_xpath_return_xmlstringlist(pepxml, "//body/*/fi", default_return=None)
    if freuds_italics is not None:
        freuds_italics = remove_values_from_terms_highlighted_list(freuds_italics)
    
    new_rec = {
                "id": artInfo.art_id,                                         # important =  note this is unique id for every reference
                "art_id" : artInfo.art_id,                                    # important                                     
                "title" : artInfo.art_title,                                  # important                                      
                "art_title_xml" : opasxmllib.xml_xpath_return_xmlsingleton(pepxml, "//arttitle", default_return = None),
                "art_sourcecode" : artInfo.src_code,                 # important
                "art_sourcetitleabbr" : artInfo.src_title_abbr,
                "art_sourcetitlefull" : artInfo.src_title_full,
                "art_sourcetype" : artInfo.src_type,
                # abstract_xml and summaries_xml should not be searched, but useful for display without extracting
                "abstract_xml" : opasxmllib.xml_xpath_return_xmlstringlist(pepxml, "//abs", default_return = None),
                "summaries_xml" : summaries_xml,
                "art_excerpt" : excerpt,
                "art_excerpt_xml" : excerpt_xml,
                # very important field for displaying the whole document or extracting parts
                "text_xml" : file_xml_contents,                                # important
                "art_offsite" : offsite_contents, #  true if it's offsite
                "author_bio_xml" : opasxmllib.xml_xpath_return_xmlstringlist(pepxml, "//nbio", default_return = None),
                "author_aff_xml" : opasxmllib.xml_xpath_return_xmlstringlist(pepxml, "//autaff", default_return = None),
                "bk_title_xml" : opasxmllib.xml_xpath_return_xmlstringlist(pepxml, "//artbkinfo/bktitle", default_return = None),
                "bk_subdoc" : artInfo.bk_subdoc,
                "art_info_xml" : artInfo.artinfo_xml,
                "bk_alsoknownas_xml" : opasxmllib.xml_xpath_return_xmlstringlist(pepxml, "//artbkinfo/bkalsoknownas", default_return = None),
                "bk_editors_xml" : opasxmllib.xml_xpath_return_xmlstringlist(pepxml, "//bkeditors", default_return = None),
                "bk_seriestitle_xml" : opasxmllib.xml_xpath_return_xmlstringlist(pepxml, "//bktitle", default_return = None),
                "bk_series_toc_id" : artInfo.bk_seriestoc,
                "bk_main_toc_id" : artInfo.main_toc_id,
                "bk_next_id" : artInfo.bk_next_id,
                "caption_text_xml" : opasxmllib.xml_xpath_return_xmlstringlist(pepxml,"//caption", default_return = None),
                "caption_title_xml" : opasxmllib.xml_xpath_return_xmlstringlist(pepxml, "//ctitle", default_return = None),
                "headings_xml" : opasxmllib.xml_xpath_return_xmlstringlist(pepxml, "//h1|//h2|//h3|//h4|//h5|//h6", default_return = None), # reinstated 2020-08-14
                "meta_xml" : opasxmllib.xml_xpath_return_xmlstringlist(pepxml, "//meta", default_return = None),
                "text_xml" : file_xml_contents,
                "timestamp" : artInfo.processed_datetime,                     # important
                "file_last_modified" : artInfo.filedatetime,
                "file_classification" : non_empty_string(artInfo.file_classification),
                "file_size" : artInfo.file_size,
                "file_name" : artInfo.filename,
                "art_subtitle_xml" : opasxmllib.xml_xpath_return_xmlsingleton(pepxml, "//artsubtitle", default_return = None),
                "art_citeas_xml" : artInfo.art_citeas_xml,
                "art_cited_all" : cited_counts.countAll,
                "art_cited_5" : cited_counts.count5,
                "art_cited_10" : cited_counts.count10,
                "art_cited_20" : cited_counts.count20,
                #"art_body_xml" : bodyXml,
                "authors" :  artInfo.author_list, # artInfo.art_all_authors,
                "art_authors" : artInfo.author_list,
                "art_authors_count" : artInfo.art_authors_count,
                "art_authors_mast" : non_empty_string(artInfo.art_auth_mast),
                "art_authors_citation" : non_empty_string(artInfo.art_auth_citation),
                "art_authors_unlisted" : non_empty_string(artInfo.art_auth_mast_unlisted_str),
                "art_authors_xml" : opasxmllib.xml_xpath_return_xmlstringlist(pepxml, "//aut", default_return = None),
                "art_year" : non_empty_string(artInfo.art_year),
                "art_year_int" : artInfo.art_year_int,
                "art_vol" : artInfo.art_vol_int,
                "art_vol_suffix" : non_empty_string(artInfo.art_vol_suffix),
                "art_vol_title" : non_empty_string(artInfo.art_vol_title),
                "art_pgrg" : non_empty_string(artInfo.art_pgrg),
                "art_pgcount" : artInfo.art_pgcount,
                "art_iss" : artInfo.art_issue,
                "art_iss_title" : artInfo.art_issue_title,
                "art_doi" : artInfo.art_doi,
                "art_lang" : artInfo.art_lang,
                "art_issn" : artInfo.art_issn,
                "art_isbn" : artInfo.art_isbn,
                "art_origrx" : artInfo.art_orig_rx,
                "art_qual" : artInfo.art_qual,
                "art_kwds" : artInfo.art_kwds, # pure search field, but maybe not as good as str
                "art_kwds_str" : art_kwds_str, # list, multivalue field for faceting
                "glossary_terms": glossary_terms_list,
                "glossary_group_terms": glossary_group_terms_list,
                "freuds_italics": freuds_italics,
                "art_type" : artInfo.art_type,
                "art_newsecnm" : artInfo.start_sectname,
                "terms_xml" : opasxmllib.xml_xpath_return_xmlstringlist(pepxml, "//impx[@type='TERM2']", default_return=None),
                "terms_highlighted" : terms_highlighted,
                "dialogs_spkr" : opasxmllib.xml_xpath_return_xmlstringlist(pepxml, "//dialog/spkr/node()", default_return=None),
                "panels_spkr" : opasxmllib.xml_xpath_return_xmlstringlist(pepxml, "//panel/spkr", default_return=None),
                "poems_src" : opasxmllib.xml_xpath_return_xmlstringlist(pepxml, "//poem/src/node()", default_return=None), # multi
                "dialogs_xml" : opasxmllib.xml_xpath_return_xmlstringlist(pepxml, "//dialog", default_return=None), # multi
                "dreams_xml" : opasxmllib.xml_xpath_return_xmlstringlist(pepxml, "//dream", default_return=None), # multi
                "notes_xml" : opasxmllib.xml_xpath_return_xmlstringlist(pepxml, "//note", default_return=None),
                "panels_xml" : opasxmllib.xml_xpath_return_xmlstringlist(pepxml, "//panel", default_return=None),
                "poems_xml" : opasxmllib.xml_xpath_return_xmlstringlist(pepxml, "//poem", default_return=None), # multi
                "quotes_xml" : opasxmllib.xml_xpath_return_xmlstringlist(pepxml, "//quote", default_return=None), # multi
                "reference_count" : artInfo.ref_count,
                "references_xml" : opasxmllib.xml_xpath_return_xmlstringlist(pepxml, "//be|binc", default_return=None), # multi
                "tables_xml" : opasxmllib.xml_xpath_return_xmlstringlist(pepxml, "//tbl", default_return=None), # multi
                "bk_pubyear" : opasxmllib.xml_xpath_return_xmlstringlist(pepxml, "//bkpubyear/node()", default_return=None), # multi
                "bib_authors" : artInfo.bib_authors,
                "bib_title" : artInfo.bib_title,
                "bib_journaltitle" : artInfo.bib_journaltitle,
                "bib_rx" : artInfo.bib_rx,
                "art_level" : 1,
                #"art_para" : parasxml, 
                "_doc" : children.child_list
              }

    #experimental paras save
    # parasxml_update(parasxml, solrcon, artInfo)
    # format for pysolr (rather than solrpy, supports nesting)
    try:
        solrcon.add([new_rec], commit=False)
    except Exception as err:
        #processingErrorCount += 1
        errStr = "Solr call exception for save doc on %s: %s" % (artInfo.art_id, err)
        print (errStr)

    return

class doc_children(object):
    """
    Create an list of child strings to be used as the Solr nested document.
    The parent_tag allows different groups of subelements to be added and separately searchable.
    
    """
    def __init__(self):
        self.count = 0
        self.child_list = []
        self.tag_counts = {}
        
    def add_children(self, stringlist, parent_id, parent_tag=None, level=2, default_lang=None):
        """
        params:
         - stringlist is typically going to be the return of an xpath expression on an xml instance
         - parent_id is the typically going to be the Solr ID of the parent, and this is suffixed
                     to produce a similar but unique id for the child
         - parent_tag for indicating where this was located in the main instance, e.g., references, dreams, etc.
         - level for creating children at different levels (even if in the same object)
        """
        for n in stringlist:
            self.count += 1
            try:
                self.tag_counts[parent_tag] += 1
            except: # initialize
                self.tag_counts[parent_tag] = 1
            
            # special attr handling.  Later look and see if this is slowing us down...
            currelem = etree.fromstring(n)
            lang = currelem.attrib.get("lang", default_lang)
            para_lgrid = currelem.attrib.get("lgrid", None)
            para_lgrx = currelem.attrib.get("lgrx", None)
            if para_lgrx is not None:
                para_lgrx = [item.strip() for item in para_lgrx.split(',')]
                
            self.child_list.append({"id": parent_id + f".{self.count}",
                                    "art_level": level,
                                    "parent_tag": parent_tag,
                                    "lang": lang,
                                    "para": n,
                                    "para_lgrid" : para_lgrid,
                                    "para_lgrx" : para_lgrx
                                  })
        return self.count

#------------------------------------------------------------------------------------------------------
def process_info_for_author_core(pepxml, artInfo, solrAuthor):
    """
    Get author data and write a record for each author in each document.  Hence an author
       of multiple articles will be listed multiple times, once for each article.  But
       this core will let us research by individual author, including facets.
       
    """
    #------------------------------------------------------------------------------------------------------
    # update author data
    #<!-- ID = PEP articleID + authorID -->
    try:
        # Save author info in database
        authorPos = 0
        for author in artInfo.author_xml_list:
            authorID = author.attrib.get('authindexid', None)
            if authorID is None:
                authorID = opasxmllib.authors_citation_from_xmlstr(author)
                try:
                    authorID = authorID[0]
                except:
                    authorID = "GenID" + "%05d" % random.randint(1, 5000)
            authorListed = author.attrib.get('listed', "true")
            if authorListed.lower() == "true":
                authorPos += 1
            authorRole = author.attrib.get('role', None)
            authorXML = opasxmllib.xml_elem_or_str_to_xmlstring(author)
            authorDocid = artInfo.art_id + "." + ''.join(e for e in authorID if e.isalnum())
            authorBio = opasxmllib.xml_xpath_return_textsingleton(author, "nbio")
            try:
                authorAffID = author.attrib['affid']
            except KeyError as e:
                authorAffil = None  # see if the add still takes!
            else:
                authorAffil = pepxml.xpath('//artinfo/artauth/autaff[@affid="%s"]' % authorAffID)
                authorAffil = etree.tostring(authorAffil[0])
               
            try:  
                response_update = solrAuthor.add(id = authorDocid,         # important =  note this is unique id for every author + artid
                                                 art_id = artInfo.art_id,
                                                 title = artInfo.art_title,
                                                 authors = artInfo.art_author_id_list,
                                                 art_author_id = authorID,
                                                 art_author_listed = authorListed,
                                                 art_author_pos_int = authorPos,
                                                 art_author_role = authorRole,
                                                 art_author_bio = authorBio,
                                                 art_author_affil_xml = authorAffil,
                                                 art_year_int = artInfo.art_year_int,
                                                 art_sourcetype = artInfo.src_type,
                                                 art_sourcetitlefull = artInfo.src_title_full,
                                                 art_citeas_xml = artInfo.art_citeas_xml,
                                                 art_author_xml = authorXML,
                                                 file_last_modified = artInfo.filedatetime,
                                                 file_classification = artInfo.file_classification,
                                                 file_name = artInfo.filename,
                                                 timestamp = artInfo.processed_datetime  # When batch was entered into core
                                                )
                if not re.search('"status">0</int>', response_update):
                    print (response_update)
            except Exception as err:
                #processingErrorCount += 1
                errStr = "Error for %s: %s" % (artInfo.art_id, err)
                print (errStr)
                config.logger.error(errStr)
               

    except Exception as err:
        #processingErrorCount += 1
        errStr = "Error for %s: %s" % (artInfo.art_id, err)
        print (errStr)
        config.logger.error(errStr)

#------------------------------------------------------------------------------------------------------
#def processBibForReferencesCore(pepxml, artInfo, solrbib):
    #"""
    #Adds the bibliography data from a single document to the core per the pepwebrefs solr schema
    
    #"""
    #print(("   ...Processing %s references for the references database." % (artInfo.ref_count)))
    ##------------------------------------------------------------------------------------------------------
    ##<!-- biblio section fields -->
    ##Note: currently, this does not include footnotes or biblio include tagged data in document (binc)
    #bibReferences = pepxml.xpath("/pepkbd3//be")  # this is the second time we do this (also in artinfo, but not sure or which is better per space vs time considerations)
    #retVal = artInfo.ref_count
    ##processedFilesCount += 1
    #bib_total_reference_count = 0
    #allRefs = []
    #for ref in bibReferences:
        ## bib_entry = BiblioEntry(artInfo, ref)
        #bib_total_reference_count += 1
        #bibRefEntry = etree.tostring(ref, with_tail=False)
        #bibRefID = opasxmllib.xml_get_element_attr(ref, "id")
        #refID = artInfo.art_id + "." + bibRefID
        #bibSourceTitle = opasxmllib.xml_get_subelement_textsingleton(ref, "j")
        #bibPublishers = opasxmllib.xml_get_subelement_textsingleton(ref, "bp")
        #if bibPublishers != "":
            #bibSourceType = "book"
        #else:
            #bibSourceType = "journal"
        #if bibSourceType == "book":
            #bibYearofPublication = opasxmllib.xml_get_subelement_textsingleton(ref, "bpd")
            #if bibYearofPublication == "":
                #bibYearofPublication = opasxmllib.xml_get_subelement_textsingleton(ref, "y")
            #if bibSourceTitle is None or bibSourceTitle == "":
                ## sometimes has markup
                #bibSourceTitle = opasxmllib.xml_get_direct_subnode_textsingleton(ref, "bst")  # book title
        #else:
            #bibYearofPublication = opasxmllib.xml_get_subelement_textsingleton(ref, "y")
           
        #if bibYearofPublication == "":
            ## try to match
            #try:
                #bibYearofPublication = re.search(r"\(([A-z]*\s*,?\s*)?([12][0-9]{3,3}[abc]?)\)", bibRefEntry).group(2)
            #except Exception as e:
                #logger.warning("no match %s/%s/%s" % (bibYearofPublication, ref, e))
            
        #try:
            #bibYearofPublication = re.sub("[^0-9]", "", bibYearofPublication)
            #bibYearofPublicationInt = int(bibYearofPublication[0:4])
        #except ValueError as e:
            #logger.warning("Error converting bibYearofPublication to int: %s / %s.  (%s)" % (bibYearofPublication, bibRefEntry, e))
            #bibYearofPublicationInt = 0
        #except Exception as e:
            #logger.warning("Error trying to find untagged bib year in %s (%s)" % (bibRefEntry, e))
            #bibYearofPublicationInt = 0
            

        #bibAuthorNameList = [etree.tostring(x, with_tail=False).decode("utf8") for x in ref.findall("a") if x is not None]
        #bibAuthorsXml = '; '.join(bibAuthorNameList)
        ##Note: Changed to is not None since if x gets warning - FutureWarning: The behavior of this method will change in future versions. Use specific 'len(elem)' or 'elem is not None' test instead
        #authorList = [opasxmllib.xml_elem_or_str_to_text(x) for x in ref.findall("a") if opasxmllib.xml_elem_or_str_to_text(x) is not None]  # final if x gets rid of any None entries which can rarely occur.
        #authorList = '; '.join(authorList)
        #bibRefRxCf = opasxmllib.xml_get_element_attr(ref, "rxcf", default_return=None)
        #bibRefRx = opasxmllib.xml_get_element_attr(ref, "rx", default_return=None)
        #if bibRefRx is not None:
            #bibRefRxSourceCode = re.search("(.*?)\.", bibRefRx, re.IGNORECASE).group(1)
        #else:
            #bibRefRxSourceCode = None
            
        ## see if this is an offsite article
        #if artInfo.file_classification == opasConfig.DOCUMENT_ACCESS_OFFSITE: # "pepoffsite":
            ## certain fields should not be stored in returnable areas.  So full-text searchable special field for that.
            #bibRefOffsiteEntry = bibRefEntry
            ##bibEntryXMLContents = """<html>
                                 ##<p>This reference is in an article or book where text is not is available on PEP. 
                                    ##Click <a href="//www.doi.org/%s" target="_blank">here</a> to show the article on another website 
                                    ##in another window or tab.
                                 ##</p>
                                 ##</html>
                              ##""" % urllib.quote(artInfo.artDOI)
            ## should we trust clients, or remove this data?  For now, remove.  Need to probably do this in biblio core too
            #bibRefEntry = None
        #else:
            #bibRefOffsiteEntry = None
    
        #thisRef = {
                    #"id" : refID,
                    #"art_id" : artInfo.art_id,
                    #"file_last_modified" : artInfo.filedatetime,
                    #"file_classification" : artInfo.file_classification,
                    #"file_size" : artInfo.file_size,
                    #"file_name" : artInfo.filename,
                    #"timestamp" : artInfo.processed_datetime,  # When batch was entered into core
                    #"art_title" : artInfo.art_title,
                    #"art_sourcecode" : artInfo.src_code,
                    #"art_sourcetitleabbr" : artInfo.art_source_title_abbr,
                    #"art_sourcetitlefull" : artInfo.art_source_title_full,
                    #"art_sourcetype" : artInfo.art_source_type,
                    #"art_authors" : artInfo.artAllAuthors,
                    #"reference_count" :artInfo.ref_count,  # would be the same for each reference in article, but could still be useful
                    #"art_year" : artInfo.art_year,
                    #"art_year_int" : artInfo.art_year_int,
                    #"art_vol" : artInfo.art_vol,
                    #"art_pgrg" : artInfo.art_pgrg,
                    #"art_lang" : artInfo.art_lang,
                    #"art_citeas_xml" : artInfo.art_citeas_xml,
                    #"text_ref" : bibRefEntry,                        
                    #"text_offsite_ref": bibRefOffsiteEntry,
                    #"authors" : authorList,
                    #"title" : opasxmllib.xml_get_subelement_textsingleton(ref, "t"),
                    #"bib_authors_xml" : bibAuthorsXml,
                    #"bib_ref_id" : bibRefID,
                    #"bib_ref_rx" : bibRefRx,
                    #"bib_ref_rxcf" : bibRefRxCf, # the not 
                    #"bib_ref_rx_sourcecode" : bibRefRxSourceCode,
                    #"bib_articletitle" : opasxmllib.xml_get_subelement_textsingleton(ref, "t"),
                    #"bib_sourcetype" : bibSourceType,
                    #"bib_sourcetitle" : bibSourceTitle,
                    #"bib_pgrg" : opasxmllib.xml_get_subelement_textsingleton(ref, "pp"),
                    #"bib_year" : bibYearofPublication,
                    #"bib_year_int" : bibYearofPublicationInt,
                    #"bib_volume" : opasxmllib.xml_get_subelement_textsingleton(ref, "v"),
                    #"bib_publisher" : bibPublishers
                  #}
        #allRefs.append(thisRef)
        
    ## We collected all the references.  Now lets save the whole shebang
    #try:
        #response_update = solrbib.add_many(allRefs)  # lets hold off on the , _commit=True)

        #if not re.search('"status">0</int>', response_update):
            #print (response_update)
    #except Exception as err:
        ##processingErrorCount += 1
        #config.logger.error("Solr call exception %s", err)

    #return retVal  # return the bibRefCount

#------------------------------------------------------------------------------------------------------
def add_reference_to_biblioxml_table(ocd, artInfo, bib_entry):
    """
    Adds the bibliography data from a single document to the biblioxml table in mysql database opascentral.
    
    This database table is used as the basis for the cited_crosstab views, which show most cited articles
      by period.  It replaces fullbiblioxml which was being imported from the non-OPAS document database
      pepa1db, which is generated during document conversion from KBD3 to EXP_ARCH1.  That was being used
      as an easy bridge to start up OPAS.
      
    Note: This data is in addition to the Solr pepwebrefs (biblio) core which is added elsewhere.  The SQL table is
          primarily used for the cross-tabs, since the Solr core is more easily joined with
          other Solr cores in queries.  (TODO: Could later experiment with bridging Solr/SQL.)
          
    Note: More info than needed for crosstabs is captured to this table, but that's as a bridge
          to potential future uses.
          
          TODO: Finish redefining crosstab queries to use this base table.
      
    """
    ret_val = False
    insert_if_not_exists = r"""REPLACE
                               INTO api_biblioxml (
                                    art_id,
                                    bib_local_id,
                                    art_year,
                                    bib_rx,
                                    bib_sourcecode, 
                                    bib_rxcf, 
                                    bib_authors, 
                                    bib_authors_xml, 
                                    bib_articletitle, 
                                    bib_sourcetype, 
                                    bib_sourcetitle, 
                                    bib_pgrg, 
                                    bib_year, 
                                    bib_year_int, 
                                    bib_volume, 
                                    bib_publisher, 
                                    full_ref_xml,
                                    full_ref_text
                                    )
                                values (%(art_id)s,
                                        %(ref_local_id)s,
                                        %(art_year_int)s,
                                        %(rx)s,
                                        %(rx_sourcecode)s,
                                        %(rxcf)s,
                                        %(author_list_str)s,
                                        %(authors_xml)s,
                                        %(ref_title)s,
                                        %(source_type)s,
                                        %(source_title)s,
                                        %(pgrg)s,
                                        %(year_of_publication)s,
                                        %(year_of_publication_int)s,
                                        %(volume)s,
                                        %(publishers)s,
                                        %(ref_entry_xml)s,
                                        %(ref_entry_text)s
                                        );
                            """
    query_param_dict = bib_entry.__dict__
    
    try:
        res = ocd.do_action_query(querytxt=insert_if_not_exists, queryparams=query_param_dict)
    except Exception as e:
        print (f"Error {e}")
    else:
        ret_val = True
        
    return ret_val  # return True for success
#------------------------------------------------------------------------------------------------------
def add_article_to_api_articles_table(ocd, art_info):
    """
    Adds the article data from a single document to the api_articles table in mysql database opascentral.
    
    This database table is used as the basis for
     
    Note: This data is in addition to the Solr pepwebdocs core which is added elsewhere.  The SQL table is
          currently primarily used for the crosstabs rather than API queries, since the Solr core is more
          easily joined with other Solr cores in queries.  (TODO: Could later experiment with bridging Solr/SQL.)
      
    """
    ret_val = False
    ocdconn = ocd.open_connection(caller_name="processArticles")
  
    insert_if_not_exists = r"""REPLACE
                               INTO api_articles (
                                    art_id,
                                    art_doi,
                                    art_type,
                                    art_lang,
                                    art_kwds,
                                    art_auth_mast,
                                    art_auth_citation,
                                    art_title,
                                    src_title_abbr,
                                    src_code,
                                    art_year,
                                    art_vol,
                                    art_vol_str,
                                    art_vol_suffix,
                                    art_issue,
                                    art_pgrg,
                                    art_pgstart,
                                    art_pgend,
                                    main_toc_id,
                                    start_sectname,
                                    bk_info_xml,
                                    bk_title,
                                    bk_publisher,
                                    art_citeas_xml,
                                    art_citeas_text,
                                    ref_count,
                                    filename,
                                    filedatetime
                                    )
                                values (
                                        %(art_id)s,
                                        %(art_doi)s,
                                        %(art_type)s,
                                        %(art_lang)s,
                                        %(art_kwds)s,
                                        %(art_auth_mast)s,
                                        %(art_auth_citation)s,
                                        %(art_title)s,
                                        %(src_title_abbr)s,
                                        %(src_code)s,
                                        %(art_year)s,
                                        %(art_vol_int)s,
                                        %(art_vol_str)s,
                                        %(art_vol_suffix)s,
                                        %(art_issue)s,
                                        %(art_pgrg)s,
                                        %(art_pgstart)s,
                                        %(art_pgend)s,
                                        %(main_toc_id)s,
                                        %(start_sectname)s,
                                        %(bk_info_xml)s,
                                        %(bk_title)s,
                                        %(bk_publisher)s,
                                        %(art_citeas_xml)s,
                                        %(art_citeas_text)s,
                                        %(ref_count)s,
                                        %(filename)s,
                                        %(filedatetime)s
                                        );
                            """

    # string entries above must match an attr of the art_info instance.
    query_param_dict = art_info.__dict__.copy()
    # the element objects in the author_xml_list cause an error in the action query 
    # even though that dict entry is not used.  So removed in a copy.
    query_param_dict["author_xml_list"] = None
        
    try:
        res = ocd.do_action_query(querytxt=insert_if_not_exists, queryparams=query_param_dict)
    except Exception as e:
        print (f"art_articles table insert error {e}")
    else:
        ret_val = True
        
    try:
        ocd.db.commit()
        ocdconn = ocd.close_connection(caller_name="processArticles")
    except pymysql.Error as e:
        print("SQL Database -- Commit failed!", e)
    
    return ret_val  # return True for success

#------------------------------------------------------------------------------------------------------
def update_views_data(solrcon, view_period=0):
    """
    Use in-place updates to update the views data
           
    """
    
    ocd =  opasCentralDBLib.opasCentralDB()
    
    # viewed last calendar year, default
    if view_period < 0 or view_period > 4:
        view_period = 0

    count, most_viewed = ocd.get_most_viewed_crosstab()
    print ("Crosstab data downloaded.  Starting to update the Solr database with the views data.")
    update_count = 0
    if most_viewed is not None:
        for n in most_viewed:
            doc_id = n.get("document_id", None)
            count_lastcalyear = n.get("lastcalyear", None) 
            count_last12mos = n.get("last12months", None) 
            count_last6mos = n.get("last6months", None) 
            count_last1mos = n.get("lastmonth", None)
            count_lastweek = n.get("lastweek", None)
            
            update_if_count = count_last6mos
            if doc_id is not None and update_if_count > 0:
                update_count += 1
                upd_rec = {
                            "id":doc_id,
                            "art_views_lastcalyear": count_lastcalyear, 
                            "art_views_last12mos": count_last12mos, 
                            "art_views_last6mos": count_last6mos, 
                            "art_views_last1mos": count_last1mos, 
                            "art_views_lastweek": count_lastweek
                }                    
                try:
                    solrcon.add([upd_rec], fieldUpdates={"art_views_lastcalyear": 'set',
                                                         "art_views_last12mos": 'set',
                                                         "art_views_last6mos": 'set',
                                                         "art_views_last1mos": 'set',
                                                         "art_views_lastweek": 'set',
                                                         }, commit=True)
                except Exception as err:
                    errStr = "Solr call exception for views update on %s: %s" % (doc_id, err)
                    print (errStr)
                    
    print (f"Finished updating Solr database with {update_count} article views/downloads.")

#------------------------------------------------------------------------------------------------------
def process_glossary_core(solr_glossary_core):
    """
    Process the special PEP Glossary documents.  These are linked to terms in the document
       as popups.
       
    Unlike the other cores processing, this has a limited document set so it runs
      through them all as a single pass, in a single call to this function.
       
    Note: Moved code 2019/11/30 from separate solrXMLGlossaryLoad program.  It was separate
          because the glossary isn't updated frequently.  However, it was felt that
          it was not as easy to keep in sync as a completely separate program.
    """
    global options
    countFiles = 0
    countTerms = 0
    ret_val = (countFiles, countTerms) # File count, entry count
    
    # find the Glossaary (bEXP_ARCH1) files (processed with links already) in path
    processedDateTime = datetime.utcfromtimestamp(time.time()).strftime(localsecrets.TIME_FORMAT_STR)
    pat = r"ZBK.069(.*)\(bEXP_ARCH1\)\.(xml|XML)$"
    filePatternMatch = re.compile(pat)
    filenames = []
    if options.singleFilePath is not None:
        if os.path.exists(options.singleFilePath):
            folderStart = options.singleFilePath
        else:
            print(f"Error: Single file mode name: {options.singleFilePath} does not exist.")
    else:
        folderStart = options.rootFolder
        if options.subFolder is not None:
            folderStart = os.path.join(folderStart, options.subFolder)
        
    for root, d_names, f_names in os.walk(folderStart):
        for f in f_names:
            if filePatternMatch.match(f):
                countFiles += 1
                filenames.append(os.path.join(root, f))

    print (f"Ready to import glossary records from {countFiles} files at path: {folderStart}")
    gloss_fileTimeStart = time.time()
    for n in filenames:
        f = open(n, encoding='utf8')
        fileXMLContents = f.read()

        # get file basename without build (which is in paren)
        base = os.path.basename(n)
        artID = os.path.splitext(base)[0]
        m = re.match(r"(.*)\(.*\)", artID)
        artID = m.group(1)
        # all IDs to upper case.
        artID = artID.upper()
        fileTimeStamp = processedDateTime

        # import into lxml
        # root = etree.fromstring(fileXMLContents)
        root = etree.fromstring(opasxmllib.remove_encoding_string(fileXMLContents))
        pepxml = root[0]

        # Containing Article data
        #<!-- Common fields -->
        #<!-- Article front matter fields -->
        #---------------------------------------------
        # Usually we put the abbreviated title here, but that won't always work here.

        #<!-- biblio section fields -->
        #Note: currently, this does not include footnotes or biblio include tagged data in document (binc)
        glossaryGroups = pepxml.xpath("/pepkbd3//dictentrygrp")  
        groupCount = len(glossaryGroups)
        print("File %s has %s groups." % (base, groupCount))
        # processedFilesCount += 1

        allDictEntries = []
        for glossaryGroup in glossaryGroups:
            glossaryGroupXML = etree.tostring(glossaryGroup, with_tail=False)
            glossaryGroupID = opasxmllib.xml_get_element_attr(glossaryGroup, "id")
            glossaryGroupTerm = opasxmllib.xml_get_subelement_textsingleton(glossaryGroup, "term")
            glossaryGroupAlso = opasxmllib.xml_get_subelement_xmlsingleton(glossaryGroup, "dictalso")
            if glossaryGroupAlso == "":
                glossaryGroupAlso = None
            print ("Processing Term: %s" % glossaryGroupTerm)
            countTerms += 1
            dictEntries = glossaryGroup.xpath("dictentry")  
            groupTermCount = len(dictEntries)
            counter = 0
            for dictEntry in dictEntries:
                counter += 1
                thisDictEntry = {}
                dictEntryID = glossaryGroupID + ".{:03d}".format(counter)
                dictEntryTerm = opasxmllib.xml_get_subelement_textsingleton(dictEntry, "term")
                if dictEntryTerm == "":
                    dictEntryTerm = glossaryGroupTerm
                dictEntryTermType = dictEntry.xpath("term/@type")  
                if dictEntryTermType != []:
                    dictEntryTermType = dictEntryTermType[0]
                else:
                    dictEntryTermType = "term"
                
                dictEntrySrc = opasxmllib.xml_get_subelement_textsingleton(dictEntry, "src")
                dictEntryAlso = opasxmllib.xml_get_subelement_xmlsingleton(dictEntry, "dictalso")
                if dictEntryAlso == "":
                    dictEntryAlso = None
                dictEntryDef = opasxmllib.xml_get_subelement_xmlsingleton(dictEntry, "def")
                dictEntryDefRest = opasxmllib.xml_get_subelement_xmlsingleton(dictEntry, "defrest")
                thisDictEntry = {
                    "term_id"             : dictEntryID,
                    "group_id"            : glossaryGroupID,
                    "art_id"              : artID,
                    "term"                : dictEntryTerm,
                    "term_type"           : dictEntryTermType,
                    "term_source"         : dictEntrySrc,
                    "term_also"           : dictEntryAlso,
                    "term_def_xml"        : dictEntryDef,
                    "term_def_rest_xml"   : dictEntryDefRest,
                    "group_name"          : glossaryGroupTerm,
                    "group_also"          : glossaryGroupAlso,
                    "group_term_count"    : groupTermCount,
                    "text"                : str(glossaryGroupXML, "utf8"),
                    "file_name"           : base,
                    "timestamp"           : processedDateTime,
                    "file_last_modified"  : fileTimeStamp
                }
                allDictEntries.append(thisDictEntry)

        # We collected all the dictentries for the group.  Now lets save the whole shebang
        try:
            response_update = solr_glossary_core.add_many(allDictEntries)  # lets hold off on the , _commit=True)
    
            if not re.search('"status">0</int>', response_update):
                print (response_update)
        except Exception as err:
            logger.error("Solr call exception %s", err)
    
        f.close()

    solr_glossary_core.commit()
    gloss_fileTimeEnd = time.time()
    
    elapsed_seconds = gloss_fileTimeEnd-gloss_fileTimeStart # actual processing time going through files
    elapsed_minutes = elapsed_seconds / 60
    
    msg2 = f"Imported {countFiles} glossary documents and {countTerms} terms. Glossary load time: {elapsed_seconds} secs ({elapsed_minutes} minutes)"
    print(msg2) 
    if countFiles > 0:
        print(f"...Files per Min: {countFiles/elapsed_minutes:.4f}") 

    ret_val = (countFiles, countTerms) # File count, entry count
    return ret_val    

def collect_citation_counts(ocd):
    citation_table = dict()
    print ("Collecting citation counts from cross-tab in biblio database...this will take a minute or two...")
    try:
        ocd.open_connection()
        # Get citation lookup table
        try:
            cursor = ocd.db.cursor(pymysql.cursors.DictCursor)
            sql = """
                  SELECT cited_document_id, count5, count10, count20, countAll from vw_stat_cited_crosstab; 
                  """
            success = cursor.execute(sql)
            if success:
                for n in cursor.fetchall():
                    row = modelsOpasCentralPydantic.MostCitedArticles(**n)
                    citation_table[row.cited_document_id] = row
                cursor.close()
            else:
                logger.error("Cursor execution failed.  Can't fetch.")
                
        except MemoryError as e:
            print(("Memory error loading table: {}".format(e)))
        except Exception as e:
            print(("Table Query Error: {}".format(e)))
        
        ocd.close_connection()
    except Exception as e:
        print(("Database Connect Error: {}".format(e)))
        citation_table["dummy"] = modelsOpasCentralPydantic.MostCitedArticles()
    
    return citation_table

#------------------------------------------------------------------------------------------------------
def file_was_created_before(before_date, filename):
    ret_val = False
    try:
        timestamp_str = datetime.utcfromtimestamp(os.path.getmtime(filename)).strftime(localsecrets.TIME_FORMAT_STR)
        if timestamp_str < before_date:
            ret_val = True
        else:
            ret_val = False
    except Exception as e:
        ret_val = False # not found or error, return False
        
    return ret_val

#------------------------------------------------------------------------------------------------------
def file_was_created_after(after_date, filename):
    ret_val = False
    try:
        timestamp_str = datetime.utcfromtimestamp(os.path.getmtime(filename)).strftime(localsecrets.TIME_FORMAT_STR)
        if timestamp_str >  after_date:
            ret_val = True
        else:
            ret_val = False
    except Exception as e:
        ret_val = False # not found or error, return False
        
    return ret_val
#------------------------------------------------------------------------------------------------------
def file_was_loaded_before(solrcore, before_date, filename):
    ret_val = False
    try:
        result = get_file_dates_solr(solrcore, filename)
        if result[0]["timestamp"] < before_date:
            ret_val = True
        else:
            ret_val = False
    except Exception as e:
        ret_val = True # not found or error, return true
        
    return ret_val

#------------------------------------------------------------------------------------------------------
def file_was_loaded_after(solrcore, after_date, filename):
    ret_val = False
    try:
        result = get_file_dates_solr(solrcore, filename)
        if result[0]["timestamp"] > after_date:
            ret_val = True
        else:
            ret_val = False
    except Exception as e:
        ret_val = True # not found or error, return true
        
    return ret_val

#------------------------------------------------------------------------------------------------------
def file_is_same_as_in_solr(solrcore, filename):
    ret_val = False
    try:
        timestamp_str = datetime.utcfromtimestamp(os.path.getmtime(filename)).strftime(localsecrets.TIME_FORMAT_STR)
        result = get_file_dates_solr(solrcore, filename)
        if result[0]["file_last_modified"] == timestamp_str:
            ret_val = True
        else:
            ret_val = False
    except Exception as e:
        ret_val = False # error, return false so it's loaded anyway.
        
    return ret_val

#------------------------------------------------------------------------------------------------------
def get_file_dates_solr(solrcore, filename=None):
    """
    Fetch the article dates
    """
    ret_val = {}
    max_rows = 1000000

    basename = os.path.basename(filename)

    # these legal file name chars are special chars to Solr, so escape them!
    b_escaped = basename.translate(str.maketrans({"(":  r"\(", 
                                                  ")":  r"\)", 
                                                  "-":  r"\-", 
                                                  ":":  r"\:", 
                                                  }))    

    getFileInfoSOLR = f'art_level:1 && file_name:"{b_escaped}"'

    try:
        results = solrcore.search(getFileInfoSOLR, fl="art_id, file_name, file_last_modified, timestamp", rows=max_rows)
    except Exception as e:
        logger.error(f"Solr Query Error {e}")
        # let me know whatever the logging is!
        print (f"Warning: Solr Query Error: {e}")
    else:
        if results.hits > 0:
            ret_val = results.docs
        else:
            ret_val = {}

    return ret_val


#------------------------------------------------------------------------------------------------------
def main():
    
    global options  # so the information can be used in support functions
    global gCitedTable
    
    cumulative_file_time_start = time.time()
    
    # scriptSourcePath = os.path.dirname(os.path.realpath(__file__))

    processed_files_count = 0
    ocd =  opasCentralDBLib.opasCentralDB()
    # Python 3 did not like the following...
    #logging.basicConfig(handlers=[ExitOnExceptionHandler()], filename=logFilename, level=options.logLevel)
    logging.basicConfig(filename=logFilename, level=options.logLevel)
    logger = config.logger = logging.getLogger(programNameShort)

    logger.info('Started at %s', datetime.today().strftime('%Y-%m-%d %H:%M:%S"'))

    solrurl_docs = None
    #solrurl_refs = None
    solrurl_authors = None
    solrurl_glossary = None
    
    if (options.biblio_update or options.fulltext_core_update or options.glossary_core_update) == True:
        try:
            solrurl_docs = localsecrets.SOLRURL + opasCoreConfig.SOLR_DOCS  # e.g., http://localhost:8983/solr/    + pepwebdocs'
            #solrurl_refs = localsecrets.SOLRURL + opasConfig.SOLR_REFS  # e.g., http://localhost:8983/solr/  + pepwebrefs'
            solrurl_authors = localsecrets.SOLRURL + opasCoreConfig.SOLR_AUTHORS
            solrurl_glossary = localsecrets.SOLRURL + opasCoreConfig.SOLR_GLOSSARY
            print("Logfile: ", logFilename)
            if options.singleFilePath is not None:
                print (f"Single file only mode: {options.singleFilePath} will be processed.")
            else:
                print("Input data Root: ", options.rootFolder)
                print("Input data Subfolder: ", options.subFolder)

            print("Reset Core Data: ", options.resetCoreData)
            print(80*"*")
            print(f"Database Location: {localsecrets.DBHOST}")
            if options.fulltext_core_update:
                print("Solr Full-Text Core will be updated: ", solrurl_docs)
                print("Solr Authors Core will be updated: ", solrurl_authors)
            if options.glossary_core_update:
                print("Solr Glossary Core will be updated: ", solrurl_glossary)

            #**********************************
            #Not used at this time
            #if options.biblio_update:
                #print("Solr References Core will be updated: ", solrurl_refs)
            #**********************************
            print(80*"*")
            if not options.no_check:
                cont = input ("The above databases will be updated.  Do you want to continue (y/n)?")
                if cont.lower() == "n":
                    print ("User requested exit.  No data changed.")
                    sys.exit(0)
                
        except Exception as e:
            msg = f"cores specification error ({e})."
            print((len(msg)*"-"))
            print (msg)
            print((len(msg)*"-"))
            sys.exit(0)
    else:
        msg = "No cores requested for update.  Use -f or -b to update the full-text and biblio cores respectively"
        print((len(msg)*"-"))
        print (msg)
        print((len(msg)*"-"))
        sys.exit(0)
        
    timeStart = time.time()
    print (f"Processing started at ({time.ctime()})..")
    
    if options.singleFilePath is not None:
        singleFileMode = True
        folderStart = options.singleFilePath
    else:
        singleFileMode = False
        folderStart = options.rootFolder
        if options.subFolder is not None:
            folderStart = os.path.join(folderStart, options.subFolder)
        
    # import data about the PEP codes for journals and books.
    #  Codes are like APA, PAH, ... and special codes like ZBK000 for a particular book
    sourceDB = opasCentralDBLib.SourceInfoDB()
    solr_docs2 = None
    #TODO: Try without the None test, the library should not try to use None as user name or password, so only the first case may be needed
    # The connection call is to solrpy (import was just solr)
    #if options.httpUserID is not None and options.httpPassword is not None:
    if localsecrets.SOLRUSER is not None and localsecrets.SOLRPW is not None:
        if options.fulltext_core_update:
            solr_docs2 = pysolr.Solr(solrurl_docs, auth=(localsecrets.SOLRUSER, localsecrets.SOLRPW))
            # fulltext update always includes authors
            # solr_docs = None
            # this is now done in opasCoreConfig
            #solr_authors = solr.SolrConnection(solrurl_authors, http_user=localsecrets.SOLRUSER, http_pass=localsecrets.SOLRPW)
        #if options.glossary_core_update:
            # this is now done in opasCoreConfig
            #solr_gloss = solr.SolrConnection(solrurl_glossary, http_user=localsecrets.SOLRUSER, http_pass=localsecrets.SOLRPW)
    else: #  no user and password needed
        solr_docs2 = pysolr.Solr(solrurl_docs)
        # fulltext update always includes authors
        # disconnect the other
        # solr_docs = None
        # this is now done in opasCoreConfig
        #solr_authors = solr.SolrConnection(solrurl_authors)
        #if options.glossary_core_update:
            # this is now done in opasCoreConfig
            #solr_gloss = solr.SolrConnection(solrurl_glossary)

    # Reset core's data if requested (mainly for early development)
    if options.resetCoreData:
        if options.fulltext_core_update:
            print ("*** Deleting all data from the docs and author cores ***")
            #solrcore_docs.delete_query("*:*")
            solr_docs2.delete(q='*:*')
            solr_docs2.commit()
            #solrcore_docs.commit()
            solr_authors.delete_query("*:*")
            solr_authors.commit()
        if options.glossary_core_update:
            print ("*** Deleting all data from the Glossary core ***")
            solr_gloss.delete_query("*:*")
            solr_gloss.commit()
    else:
        # check for missing files and delete them from the core, since we didn't empty the core above
        pass

    if options.views_update:
        print(("Update 'View Counts' in Solr selected.  Counts to be updated for all files viewed in the last month."))
        
    # Glossary Processing only
    if options.glossary_core_update:
        # this option will process all files in the glossary core.
        glossary_file_count, glossary_terms = process_glossary_core(solr_gloss)
        processed_files_count += glossary_file_count
    
    # Docs, Authors and References go through a full set of regular XML files
    bib_total_reference_count = 0 # zero this here, it's checked at the end whether references are processed or not
    if (options.biblio_update or options.fulltext_core_update) == True:
        if options.forceRebuildAllFiles == True:
            print ("Forced Rebuild - All files added, regardless of whether they were marked in the as already added.")
    
        # find all processed XML files where build is (bEXP_ARCH1) in path
        # glob.glob doesn't unfortunately work to do this in Py2.7.x
        skipped_files = 0
        new_files = 0
        total_files = 0
        if options.file_key != None:  
            #selQry = "select distinct filename from articles where articleID
            #New for 2021 - built TOCs as "Series TOC rather than hard coding them."
            print (f"File Key Specified: {options.file_key}")
            pat = fr"({options.file_key}.*)\(bEXP_ARCH1|bSeriesTOC\)\.(xml|XML)$"
            file_pattern_match = re.compile(pat)
            filenames = find_all(pat, folderStart)
        else:
            pat = r"(.*)\(bEXP_ARCH1|bSeriesTOC\)\.(xml|XML)$"
            file_pattern_match = re.compile(pat)
            filenames = []
        
        #all_solr_docs = get_file_dates_solr(solrcore_docs2)
        if singleFileMode: # re.match(".*\.xml$", folderStart, re.IGNORECASE):
            # single file mode.
            if os.path.exists(options.singleFilePath):
                filenames.append(options.singleFilePath)
                total_files = 1
                new_files = 1
            else:
                print(f"Error: Single file mode name: {options.singleFilePath} does not exist.")
        elif filenames != []:
            total_files = len(filenames)
            new_files = len(filenames)
        else:
            # get a list of all the XML files that are new
            singleFileMode = False
            currentfile_info = NewFileTracker(ocd)  
            for root, d_names, f_names in os.walk(folderStart):
                for f in f_names:
                    if file_pattern_match.match(f):
                        total_files += 1
                        #needed only if the check is very slow, not now.
                        #if totalFiles % 1000 == 0:
                            #print (f"{totalFiles} files checked so far") # print a dot to show progress, no CR
                        filename = os.path.join(root, f)

                        # by default, build all files, but will check modified during actual run 
                        is_modified = True 

                        # this is quick, but if you use the same database for multiple solr installs, it's not accurate
                        # is_modified = currentfile_info.is_refresh_needed(filename, before_date=options.created_before, after_date=options.created_after)
                        # don't check solr database here, check to see when actually loading.  Takes to long to check each one
                        # is_modified = file_is_same_as_in_solr(solrcore_docs2, filename=filename)

                        # look at file date only (no database or solr, compare to create option)
                        if options.created_after is not None:
                            is_modified = file_was_created_after(after_date=options.created_after, filename=filename)
                            #is_modified =\
                                # currentfile_info.is_load_date_before_or_after(after=options.created_after)
                            
                        if options.created_before is not None:
                            is_modified = file_was_created_before(before_date=options.created_before, filename=filename)
                            #is_modified =\
                                #currentfile_info.is_load_date_before_or_after(before=options.created_before)

                        if not is_modified:
                            # file seen before, need to compare.
                            #print "File is the same!  Skipping..."
                            skipped_files += 1
                            continue
                        else:
                            new_files += 1
                            #print "File is NOT the same!  Scanning the data..."
                            filenames.append(filename)
        
            # clear fileTracker it takes a lot of Memory
            currentfile_info.close() # close the database
            currentfile_info = None

        print((80*"-"))
        if singleFileMode:
            print(f"Single File Mode Selected.  Only file {options.singleFilePath} will be imported") 
        else:
            if options.forceRebuildAllFiles:
                print(f"Ready to import records from {new_files} files of {total_files} at path {folderStart}")
            else:
                print(f"Ready to import {new_files} files of {total_files} *if modified* at path: {folderStart}")

            print(f"{skipped_files} Skipped files (excluded by date options)")
    
        print((80*"-"))
        precommit_file_count = 0
        skipped_files = 0
        cumulative_file_time_start = time.time()
        if new_files > 0:
            gCitedTable = collect_citation_counts(ocd)
               
            if options.run_in_reverse:
                print ("-r option selected.  Running the files found in reverse order.")
                filenames.reverse()
            
            # ----------------------------------------------------------------------
            # Now walk through all the filenames selected
            # ----------------------------------------------------------------------
            print (f"Load process started ({time.ctime()}).  Examining files.")
            for n in filenames:
                fileTimeStart = time.time()
                if not options.forceRebuildAllFiles:                    
                    if not options.display_verbose and skipped_files % 100 == 0 and skipped_files != 0:
                        print (f"Skipped {skipped_files} so far...loaded {processed_files_count} out of {new_files} possible." )
                    
                    if options.reload_before_date is not None:
                        if not file_was_loaded_before(solr_docs2, before_date=options.reload_before_date, filename=n):
                            skipped_files += 1
                            if options.display_verbose:
                                print (f"Skipped - Not loaded before {options.reload_before_date} - {n}.")
                            continue
                        
                    if options.reload_after_date is not None:
                        if not file_was_loaded_before(solr_docs2, after_date=options.reload_after_date, filename=n):
                            skipped_files += 1
                            if options.display_verbose:
                                print (f"Skipped - Not loaded after {options.reload_after_date} - {n}.")
                            continue
    
                    if file_is_same_as_in_solr(solr_docs2, filename=n):
                        skipped_files += 1
                        if options.display_verbose:
                            print (f"Skipped - No refresh needed for {n}")
                        continue
                
                # get mod date/time, filesize, etc. for mysql database insert/update
                processed_files_count += 1
                f = open(n, encoding="utf-8")
                fileXMLContents = f.read()
                
                # get file basename without build (which is in paren)
                base = os.path.basename(n)
                artID = os.path.splitext(base)[0]
                m = re.match(r"(.*)\(.*\)", artID)
        
                # Update this file in the database as "processed"
                file_info = opasgenlib.FileInfo(n)
                #currentfile_info.loadForFile(n)
                #fileTracker.setFileDatabaseRecord(currFileInfo)
                # fileTimeStamp = datetime.utcfromtimestamp(currentfile_info.fileModDate).strftime(localsecrets.TIME_FORMAT_STR)
                print(("Processing file #%s of %s: %s (%s bytes)." % (processed_files_count, new_files, base, file_info.fileSize)))
        
                # Note: We could also get the artID from the XML, but since it's also important
                # the file names are correct, we'll do it here.  Also, it "could" have been left out
                # of the artinfo (attribute), whereas the filename is always there.
                artID = m.group(1)
                # all IDs to upper case.
                artID = artID.upper()
        
                # import into lxml
                root = etree.fromstring(opasxmllib.remove_encoding_string(fileXMLContents))
                pepxml = root
        
                # save common document (article) field values into artInfo instance for both databases
                artInfo = ArticleInfo(sourceDB.sourceData, pepxml, artID, logger)
                artInfo.filedatetime = file_info.timestamp_str
                artInfo.filename = base
                artInfo.file_size = file_info.fileSize
                try:
                    artInfo.file_classification = re.search("(current|archive|future|free|offsite)", n, re.IGNORECASE).group(1)
                    # set it to lowercase for ease of matching later
                    artInfo.file_classification = artInfo.file_classification.lower()
                except Exception as e:
                    logging.warning("Could not determine file classification for %s (%s)" % (n, e))
        
                # walk through bib section and add to refs core database
        
                precommit_file_count += 1
                if precommit_file_count > config.COMMITLIMIT:
                    print(("Committing info for %s documents/articles" % config.COMMITLIMIT))

                # input to the full-text code
                if options.fulltext_core_update:
                    # this option will also load the authors cores.
                    process_article_for_doc_core(pepxml, artInfo, solr_docs2, fileXMLContents)
                    process_info_for_author_core(pepxml, artInfo,
                                                 solr_authors)
                    add_article_to_api_articles_table(ocd, artInfo)
                    
                    if precommit_file_count > config.COMMITLIMIT:
                        precommit_file_count = 0
                        solr_docs2.commit()
                        solr_authors.commit()
                        #fileTracker.commit()
        
                # input to the references core
                if options.biblio_update:
                    if artInfo.ref_count > 0:
                        bibReferences = pepxml.xpath("/pepkbd3//be")  # this is the second time we do this (also in artinfo, but not sure or which is better per space vs time considerations)
                        if 1: # options.display_verbose:
                            print(("   ...Processing %s references for the references database." % (artInfo.ref_count)))

                        #processedFilesCount += 1
                        bib_total_reference_count = 0
                        ocd.open_connection(caller_name="processBibliographies")
                        for ref in bibReferences:
                            bib_total_reference_count += 1
                            bib_entry = BiblioEntry(artInfo, ref)
                            add_reference_to_biblioxml_table(ocd, artInfo, bib_entry)

                        try:
                            ocd.db.commit()
                        except pymysql.Error as e:
                            print("SQL Database -- Biblio Commit failed!", e)
                            
                        ocd.close_connection(caller_name="processBibliographies")
                        # process_bibliographies(pepxml, artInfo, solrcore_references)

                        #if preCommitFileCount > config.COMMITLIMIT:
                            #preCommitFileCount = 0
                            #solrcore_references.commit()
                            #fileTracker.commit()
        
                        #preCommitFileCount += 1

                # close the file, and do the next
                f.close()
                if 1: # options.display_verbose:
                    print(("   ...Time: %s seconds." % (time.time() - fileTimeStart)))
        
            # all done with the files.  Do a final commit.
            #try:
                #if options.biblio_update:
                    #solrcore_references.commit()
                    ## fileTracker.commit()
            #except Exception as e:
                #print(("Exception: ", e))
            
            # if called for with the -v option, do an update on all the views data, 
            # it takes about 5 minutes to remote update 400 records on AWS
            if options.views_update:
                print (f"Updating Views Data Starting ({time.ctime()}).")
                update_views_data(solr_docs2)
            
            print (f"Load process complete ({time.ctime()}).")
            if processed_files_count > 0:
                try:
                    print ("Performing final commit.")
                    if options.fulltext_core_update:
                        solr_docs2.commit()
                        solr_authors.commit()
                        # fileTracker.commit()
                except Exception as e:
                    print(("Exception: ", e))

    # end of docs, authors, and/or references Adds

    # ---------------------------------------------------------
    # Closing time
    # ---------------------------------------------------------
    timeEnd = time.time()
    #currentfile_info.close()

    # for logging
    msg = msg2 = None
    if (options.biblio_update or options.fulltext_core_update) == True:
        elapsed_seconds = timeEnd-cumulative_file_time_start # actual processing time going through files
        elapsed_minutes = elapsed_seconds / 60
        if bib_total_reference_count > 0:
            msg = f"Finished! Imported {processed_files_count} documents and {bib_total_reference_count} references. Total file inspection/load time: {elapsed_seconds:.2f} secs ({elapsed_minutes:.2f} minutes.) "
            print(msg)
        else:
            msg = f"Finished! Imported {processed_files_count} documents. Total file load time: {elapsed_seconds:.2f} secs ({elapsed_minutes:.2f} minutes.)"
            print(msg) 
        if processed_files_count > 0:
            print(f"...Files loaded per Min: {processed_files_count/elapsed_minutes:.4f}") 
            print(f"...Files evaluated per Min: {len(filenames)/elapsed_minutes:.4f}") 

    elapsed_seconds = timeEnd-timeStart # actual processing time going through files
    elapsed_minutes = elapsed_seconds / 60
    print (f"Note: File load time is not total elapsed time. Total elapsed time is: {elapsed_seconds:.2f} secs ({elapsed_minutes:.2f} minutes.)")
    if processed_files_count > 0:
        print(f"Files per elapsed min: {processed_files_count/elapsed_minutes:.4f}") 
    if msg:
        config.logger.info(msg)
    if msg2:
        config.logger.info(msg)
        
    #if processingWarningCount + processingErrorCount > 0:
        #print ("  Issues found.  Warnings: %s, Errors: %s.  See log file %s" % (processingWarningCount, processingErrorCount, logFilename))

# -------------------------------------------------------------------------------------------------------
# run it!

if __name__ == "__main__":
    global options  # so the information can be used in support functions
    options = None
    programNameShort = "solrXMLPEPWebLoad"  # used for log file
    logFilename = programNameShort + "_" + datetime.today().strftime('%Y-%m-%d') + ".log"

    parser = OptionParser(usage="%prog [options] - PEP Solr Reference Text Data Loader", version="%prog ver. 0.1.14")
    parser.add_option("-a", "--allfiles", action="store_true", dest="forceRebuildAllFiles", default=False,
                      help="Option to force all files to be updated on the specified cores.  This does not reset the file tracker but updates it as files are processed.")
    parser.add_option("-b", "--biblioupdate", dest="biblio_update", action="store_true", default=False,
                      help="Whether to update the biblio table in the mysql database (used to be a core)")
    parser.add_option("-d", "--dataroot", dest="rootFolder", default=config.DEFAULTDATAROOT,
                      help="Root folder path where input data is located")
    parser.add_option("--only", dest="singleFilePath", default=None,
                      help="Full path (including filename) of single file to process")
    parser.add_option("-f", "--fulltextcoreupdate", dest="fulltext_core_update", action="store_true", default=False,
                      help="Whether to update the full-text and authors core. Use -d option to specify file folder root path.")
    parser.add_option("--key", dest="file_key", default=None,
                      help="Key for a single file to process")
    parser.add_option("-l", "--loglevel", dest="logLevel", default=logging.INFO,
                      help="Level at which events should be logged")
    parser.add_option("--logfile", dest="logfile", default=logFilename,
                      help="Logfile name with full path where events should be logged")
    parser.add_option("--resetcore",
                      action="store_true", dest="resetCoreData", default=False,
                      help="reset the data in the selected cores. (authorscore is reset with the fulltext core)")
    parser.add_option("-g", "--glossarycoreupdate", dest="glossary_core_update", action="store_true", default=False,
                      help="Whether to update the glossary core. Use -d option to specify glossary file folder root path.")
    parser.add_option("--pw", dest="httpPassword", default=None,
                      help="Password for the server")
    parser.add_option("-q", "--quickload", dest="quickload", action="store_true", default=False,
                      help="Load the full-set of database file records for a full solr db reload")
    parser.add_option("-r", "--reverse", dest="run_in_reverse", action="store_true", default=False,
                      help="Whether to run the files selected in reverse")
    #parser.add_option("-t", "--trackerdb", dest="fileTrackerDBPath", default=None,
                      #help="Full path and database name where the File Tracking Database is located (sqlite3 db)")
    parser.add_option("--sub", dest="subFolder", default=None,
                      help="Sub folder of root folder specified via -d to process")
    parser.add_option("--test", dest="testmode", action="store_true", default=False,
                      help="Run Doctests")
    parser.add_option("-v", "--viewsupdate", dest="views_update", action="store_true", default=False,
                      help="Whether to update the view count data in Solr when updating documents (adds about 5 minutes)")
    #parser.add_option("-u", "--url",
                      #dest="solrURL", default=config.DEFAULTSOLRHOME,
                      #help="Base URL of Solr api (without core), e.g., http://localhost:8983/solr/", metavar="URL")
    parser.add_option("--verbose", action="store_true", dest="display_verbose", default=False,
                      help="Display status and operational timing info as load progresses.")
    parser.add_option("--nocheck", action="store_true", dest="no_check", default=False,
                      help="Display status and check whether to proceed.")
    parser.add_option("--userid", dest="httpUserID", default=None,
                      help="UserID for the server")
    parser.add_option("--config", dest="config_info", default="Local",
                      help="UserID for the server")
    parser.add_option("--before", dest="created_before", default=None,
                      help="Load files created before this datetime (use YYYY-MM-DD format)")
    parser.add_option("--after", dest="created_after", default=None,
                      help="Load files created after this datetime (use YYYY-MM-DD format)")
    parser.add_option("--reloadbefore", dest="reload_before_date", default=None,
                      help="Reload files added to Solr before this datetime (use YYYY-MM-DD format)")
    parser.add_option("--reloadafter", dest="reload_after_date", default=None,
                      help="Reload files added to Solr after this datetime (use YYYY-MM-DD format)")

    (options, args) = parser.parse_args()

    if options.testmode:
        import doctest
        doctest.testmod()
        print ("Fini. SolrXMLPEPWebLoad Tests complete.")
        sys.exit()

    main()
