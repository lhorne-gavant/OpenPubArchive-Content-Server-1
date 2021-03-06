/*
 Navicat MySQL Data Transfer

 Source Server         : XPS
 Source Server Type    : MySQL
 Source Server Version : 50726
 Source Host           : localhost:3306
 Source Schema         : opascentral

 Target Server Type    : MySQL
 Target Server Version : 50726
 File Encoding         : 65001

 Date: 29/02/2020 23:54:54
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for api_administrative_groups
-- ----------------------------
DROP TABLE IF EXISTS `api_administrative_groups`;
CREATE TABLE `api_administrative_groups`  (
  `administrative_group_id` int(11) NOT NULL,
  `group_name` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `descriptopn` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`administrative_group_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for api_articles
-- ----------------------------
DROP TABLE IF EXISTS `api_articles`;
CREATE TABLE `api_articles`  (
  `art_id` varchar(24) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL DEFAULT '' COMMENT 'The locator style ID for this article (e.g., APA.004.0109A)',
  `art_doi` varchar(255) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL,
  `art_type` varchar(4) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT '' COMMENT 'Article type, e.g., ART, COM, ERA',
  `art_lang` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `art_kwds` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `art_auth_mast` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL COMMENT 'Author names per masthead, e.g. Ronnie C. Lesser, Ph.D.',
  `art_auth_to_cite` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL COMMENT 'The heading style author list, e.g., Lesser, R. C.',
  `art_title` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL COMMENT 'The title for the heading',
  `src_title_abbr` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT 'Src title bibliogr abbrev style, e.g., Psychoanal. Dial.',
  `src_code` varchar(14) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL COMMENT 'PEP assigned Journal Code, e.g., IJP',
  `src_publisher` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci NULL DEFAULT '' COMMENT 'Publisher, e.g., Cambridge, MA / London: Harvard Univ. Press',
  `art_year` int(11) NULL DEFAULT NULL COMMENT 'Year of Publication',
  `art_vol` int(11) NULL DEFAULT NULL COMMENT 'Volume',
  `art_vol_suffix` char(5) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL COMMENT 'Vol number suffix, e.g., S for supplements',
  `art_issue` char(5) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT '' COMMENT 'Issue number or designation, e.g., 1, or pilot',
  `art_pgrg` varchar(20) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL COMMENT 'Page range of article, e.g., 1-22',
  `art_pgstart` varchar(11) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT 'Starting page number, negative for roman',
  `art_pgend` varchar(11) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT 'Ending page number, use negative for roman',
  `main_toc_id` varchar(20) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL COMMENT 'If the source has an instance as a TOC, this is the art_id for the TOC',
  `art_start_sect` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci NULL DEFAULT NULL COMMENT 'When the article starts a new section in the TOC, name',
  `bk_title` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT 'Title of parent book which contains the article',
  `bk_authors` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT 'Authors of the parent book',
  `art_citeas_text` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL COMMENT 'Text only format, citeas',
  `art_citeas_xml` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL COMMENT 'Bibliographic style reference for article, in XML',
  `art_ref_count` int(11) NULL DEFAULT NULL,
  `filename` varchar(255) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL COMMENT 'Path and filename of source file',
  `filedatetime` char(25) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL COMMENT 'Article file datetime',
  `preserve` int(11) NULL DEFAULT 0 COMMENT 'Keep this record (probably not to be used)',
  `updated` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP(0) ON UPDATE CURRENT_TIMESTAMP(0),
  PRIMARY KEY (`art_id`) USING BTREE,
  UNIQUE INDEX `Primary Key`(`art_id`) USING BTREE,
  UNIQUE INDEX `filename`(`filename`) USING BTREE,
  INDEX `xname`(`art_vol`) USING BTREE,
  INDEX `titlefulltext`(`art_title`(333)) USING BTREE,
  INDEX `yrjrnlcode`(`src_code`, `art_year`) USING BTREE,
  INDEX `voljrnlcode`(`src_code`, `art_vol`) USING BTREE,
  INDEX `authorfulltext`(`art_auth_to_cite`(255)) USING BTREE,
  INDEX `jrnlCodeIndiv`(`src_code`) USING BTREE,
  FULLTEXT INDEX `hdgtitle`(`art_title`),
  FULLTEXT INDEX `hdgauthor`(`art_auth_to_cite`),
  FULLTEXT INDEX `xmlref`(`art_citeas_xml`),
  FULLTEXT INDEX `bktitle`(`bk_title`)
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci COMMENT = 'A PEP journal article, book or book section' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for api_biblioxml
-- ----------------------------
DROP TABLE IF EXISTS `api_biblioxml`;
CREATE TABLE `api_biblioxml`  (
  `art_id` varchar(24) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL,
  `bib_local_id` varchar(25) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL,
  `bib_rx` varchar(30) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL COMMENT 'This article references...',
  `bib_rxcf` varchar(30) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT '0' COMMENT 'This article may be related to...',
  `bib_sourcecode` varchar(24) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT 'instance' COMMENT 'If it\'s refcorrections, this record came from the refcorrections table and should not be updated.',
  `bib_authors` varchar(512) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `bib_articletitle` varchar(512) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `title` varchar(255) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL,
  `full_ref_text` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL,
  `bib_sourcetype` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `bib_sourcetitle` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT 'Record the journal name as extracted from the XML referennce.  Useful to sort and check reference.',
  `bib_authors_xml` varchar(512) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `full_ref_xml` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL,
  `bib_pgrg` varchar(12) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `doi` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT 'Document Object Identifier for this reference',
  `bib_year` varchar(12) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `bib_year_int` int(255) NULL DEFAULT NULL,
  `bib_volume` varchar(12) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `bib_publisher` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `updated` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP(0) ON UPDATE CURRENT_TIMESTAMP(0),
  PRIMARY KEY (`art_id`, `bib_local_id`) USING BTREE,
  UNIQUE INDEX `Primary Key`(`art_id`, `bib_local_id`) USING BTREE,
  INDEX `articleID`(`art_id`) USING BTREE,
  INDEX `titleIndex`(`title`) USING BTREE,
  INDEX `RefersTo`(`bib_rx`) USING BTREE,
  FULLTEXT INDEX `fulreffullText`(`full_ref_text`),
  FULLTEXT INDEX `titleFullText`(`title`)
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci COMMENT = 'All bibliographic entries within PEP' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for api_client_apps
-- ----------------------------
DROP TABLE IF EXISTS `api_client_apps`;
CREATE TABLE `api_client_apps`  (
  `api_client_id` int(11) NOT NULL,
  `api_client_name` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `api_client_key` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `last_update` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP(0),
  PRIMARY KEY (`api_client_id`) USING BTREE,
  UNIQUE INDEX `idxClientname`(`api_client_name`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci COMMENT = 'Keep track of keys assigned to clients, but not used in v1 or v2 API as of 20191110' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for api_docviews
-- ----------------------------
DROP TABLE IF EXISTS `api_docviews`;
CREATE TABLE `api_docviews`  (
  `user_id` varchar(60) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `session_id` varchar(60) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `document_id` varchar(255) CHARACTER SET latin1 COLLATE latin1_spanish_ci NOT NULL DEFAULT '',
  `type` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `datetimechar` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `last_update` timestamp(0) NULL DEFAULT CURRENT_TIMESTAMP(0) ON UPDATE CURRENT_TIMESTAMP(0),
  INDEX `user_id`(`user_id`) USING BTREE,
  INDEX `session_id`(`session_id`) USING BTREE,
  CONSTRAINT `api_docviews_ibfk_1` FOREIGN KEY (`session_id`) REFERENCES `api_sessions` (`session_id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci COMMENT = 'Track the number of times a document is viewed as an abstract, full-text, PDF, or EPUB.  Somewhat redundate to api_session_endpoints table, but with less extraneous data..' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for api_endpoints
-- ----------------------------
DROP TABLE IF EXISTS `api_endpoints`;
CREATE TABLE `api_endpoints`  (
  `api_endpoint_id` int(11) NOT NULL AUTO_INCREMENT,
  `endpoint_url` varchar(200) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `last_update` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP(0),
  PRIMARY KEY (`api_endpoint_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 50 CHARACTER SET = utf8 COLLATE = utf8_general_ci COMMENT = 'Each unique API endpoint (minus base URL), starting with v1, for example\r\n' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for api_join_products_to_productbase
-- ----------------------------
DROP TABLE IF EXISTS `api_join_products_to_productbase`;
CREATE TABLE `api_join_products_to_productbase`  (
  `product_id` int(11) NOT NULL,
  `basecode` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `extra_field` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`product_id`, `basecode`) USING BTREE,
  INDEX `basecode`(`basecode`) USING BTREE,
  INDEX `product_id`(`product_id`) USING BTREE,
  CONSTRAINT `api_join_products_to_productbase_ibfk_1` FOREIGN KEY (`basecode`) REFERENCES `api_productbase` (`basecode`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `api_join_products_to_productbase_ibfk_2` FOREIGN KEY (`product_id`) REFERENCES `api_products` (`product_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for api_product_groups
-- ----------------------------
DROP TABLE IF EXISTS `api_product_groups`;
CREATE TABLE `api_product_groups`  (
  `group_id` int(11) NULL DEFAULT NULL,
  `group_name` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `level` int(11) NULL DEFAULT NULL,
  `parent_group_id` int(11) NULL DEFAULT NULL,
  `description` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for api_productbase
-- ----------------------------
DROP TABLE IF EXISTS `api_productbase`;
CREATE TABLE `api_productbase`  (
  `basecode` varchar(21) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT '' COMMENT 'Shortened form of the locator',
  `articleID` varchar(24) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL,
  `active` int(1) NULL DEFAULT NULL,
  `pep_class` set('book','journal','videostream','special','vidostream','bookseriessub') CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT '',
  `pep_class_qualifier` set('glossary','works','bookseriesvolume','multivolumebook','multivolumesubbook') CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT '',
  `wall` int(1) NULL DEFAULT 3,
  `mainTOC` varchar(21) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT '' COMMENT 'Locator for the first instance of this (or the only instance)',
  `first_author` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT 'Needed for KBART, easier than the join, which did lead to some problems since it\'s only the first author here',
  `author` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `title` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT 'Title of Publication',
  `bibabbrev` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT 'bibliographic Abbreviation',
  `ISSN` varchar(22) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL COMMENT 'ISSN for Journals only',
  `ISBN-10` varchar(13) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL,
  `ISBN-13` varchar(17) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL,
  `pages` int(4) NULL DEFAULT NULL COMMENT 'Number of pages in book',
  `Comment` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT 'use for notes, and \"unused\" ISBN for books as journals',
  `pepcode` varchar(14) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL,
  `publisher` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `jrnl` tinyint(1) NULL DEFAULT 0 COMMENT '1 if this is a journal, 0 if not',
  `pub_year` int(1) NULL DEFAULT NULL,
  `start_year` int(4) NULL DEFAULT NULL,
  `end_year` int(4) NULL DEFAULT NULL,
  `pep_url` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `language` varchar(4) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL,
  `updated` timestamp(0) NULL DEFAULT CURRENT_TIMESTAMP(0) ON UPDATE CURRENT_TIMESTAMP(0),
  `pepversion` int(1) NULL DEFAULT NULL COMMENT 'Version it first appeared in, or planned for',
  `duplicate` varchar(10) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL COMMENT 'Is this a duplicate (alternative) abbreviation/name (specified)',
  `landing_page` varchar(1024) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `coverage_notes` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci NULL DEFAULT NULL COMMENT 'Added for KBART, explain embargo if necessary',
  `landing_page_intro_html` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL,
  `landing_page_end_html` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL,
  `google_books_link` varchar(512) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL,
  PRIMARY KEY (`basecode`) USING BTREE,
  INDEX `basecode`(`basecode`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci COMMENT = 'Each ISSN Product included (from the PEP ISSN Table)\r\n\r\n' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for api_products
-- ----------------------------
DROP TABLE IF EXISTS `api_products`;
CREATE TABLE `api_products`  (
  `product_id` int(11) NOT NULL AUTO_INCREMENT,
  `subsystem_id` int(11) NOT NULL DEFAULT 8,
  `product` varchar(200) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `product_level` smallint(6) NOT NULL DEFAULT 0,
  `product_type` varchar(40) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `basecode` varchar(15) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `product_comment` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `free_access` tinyint(1) NOT NULL DEFAULT 0,
  `active` tinyint(1) NOT NULL DEFAULT 0,
  `embargo_length` tinyint(1) NULL DEFAULT NULL,
  `embargo_inverted` tinyint(1) NULL DEFAULT NULL,
  `range_limited` tinyint(1) NOT NULL DEFAULT 0,
  `range_start_year` smallint(1) NOT NULL DEFAULT 0 COMMENT 'first available year (e.g. 0 means start in the first year',
  `range_end_year` smallint(1) NOT NULL DEFAULT 0 COMMENT 'last available year',
  `parent_product_id` int(11) NULL DEFAULT 0,
  `inherit_parent_metadata` tinyint(1) NOT NULL DEFAULT 1,
  `id_type` smallint(6) NULL DEFAULT NULL,
  `counter_service` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `counter_database` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `counter_book` varchar(150) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `counter_journal_collection` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `id_code_1` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `id_code_2` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `group_sort_order` tinyint(11) NULL DEFAULT NULL,
  `hide_in_product_access` tinyint(1) NOT NULL DEFAULT 0,
  `hide_in_report_list` tinyint(1) NOT NULL DEFAULT 0,
  `added_by_user_id` int(11) NOT NULL DEFAULT 10,
  `date_added` datetime(0) NULL DEFAULT NULL,
  `modified_by_user_id` int(11) NOT NULL DEFAULT 10,
  `last_update` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP(0),
  PRIMARY KEY (`product_id`) USING BTREE,
  INDEX `idxSubsystemId`(`subsystem_id`) USING BTREE,
  INDEX `idxProductLevel`(`product_level`) USING BTREE,
  INDEX `idxParentProductId`(`parent_product_id`) USING BTREE,
  INDEX `basecode`(`basecode`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 4001 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for api_products_closure
-- ----------------------------
DROP TABLE IF EXISTS `api_products_closure`;
CREATE TABLE `api_products_closure`  (
  `ancestor_product_id` int(11) NOT NULL,
  `descendent_product_id` int(11) NOT NULL,
  `path_length` int(11) NULL DEFAULT NULL,
  `anc_prod_name` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `des_prod_name` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for api_session_endpoints
-- ----------------------------
DROP TABLE IF EXISTS `api_session_endpoints`;
CREATE TABLE `api_session_endpoints`  (
  `session_id` varchar(60) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `api_endpoint_id` int(11) NOT NULL,
  `params` varchar(2500) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `item_of_interest` varchar(60) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `return_status_code` int(11) NULL DEFAULT NULL,
  `return_added_status_message` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `last_update` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP(0),
  INDEX `fk_session_id`(`session_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci COMMENT = 'All endpoints called in a session, and parameters defining searches, retrievals etc..\r\n\r\n' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for api_sessions
-- ----------------------------
DROP TABLE IF EXISTS `api_sessions`;
CREATE TABLE `api_sessions`  (
  `session_id` varchar(60) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `user_id` int(11) NULL DEFAULT NULL,
  `username` varchar(255) CHARACTER SET ujis COLLATE ujis_japanese_ci NULL DEFAULT NULL,
  `user_ip` varchar(60) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `connected_via` varchar(512) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `referrer` varchar(512) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `session_start` timestamp(0) NOT NULL,
  `session_end` timestamp(0) NULL DEFAULT NULL,
  `session_expires_time` timestamp(0) NULL DEFAULT NULL,
  `access_token` varchar(1000) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT 'a JWT so could be long',
  `authenticated` tinyint(1) NULL DEFAULT 0,
  `admin` tinyint(1) NULL DEFAULT 0,
  `api_client_id` int(11) NOT NULL,
  `updated` timestamp(0) NULL DEFAULT CURRENT_TIMESTAMP(0) ON UPDATE CURRENT_TIMESTAMP(0),
  PRIMARY KEY (`session_id`) USING BTREE,
  INDEX `idxSession`(`session_id`) USING BTREE,
  INDEX `session_user`(`user_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci COMMENT = 'Each API session with a unique ID creates a session record. ' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for api_stat_cited_crosstab_static_copy
-- ----------------------------
DROP TABLE IF EXISTS `api_stat_cited_crosstab_static_copy`;
CREATE TABLE `api_stat_cited_crosstab_static_copy`  (
  `cited_document_id` varchar(24) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `count5` int(255) NULL DEFAULT NULL,
  `count10` int(255) NULL DEFAULT NULL,
  `count20` int(255) NULL DEFAULT NULL,
  `countall` int(255) NULL DEFAULT NULL,
  `updated` timestamp(0) NULL DEFAULT CURRENT_TIMESTAMP(0) ON UPDATE CURRENT_TIMESTAMP(0),
  PRIMARY KEY (`cited_document_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for api_stat_docviews_crosstab_static_copy
-- ----------------------------
DROP TABLE IF EXISTS `api_stat_docviews_crosstab_static_copy`;
CREATE TABLE `api_stat_docviews_crosstab_static_copy`  (
  `document_id` varchar(24) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `last_viewed` datetime(0) NULL DEFAULT NULL,
  `lastweek` int(255) NULL DEFAULT NULL,
  `lastmonth` int(255) NULL DEFAULT NULL,
  `last6months` int(255) NULL DEFAULT NULL,
  `last12months` int(255) NULL DEFAULT NULL,
  `lastcalyear` int(255) NULL DEFAULT NULL,
  `updated` timestamp(0) NULL DEFAULT CURRENT_TIMESTAMP(0) ON UPDATE CURRENT_TIMESTAMP(0),
  PRIMARY KEY (`document_id`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for api_subscriptions
-- ----------------------------
DROP TABLE IF EXISTS `api_subscriptions`;
CREATE TABLE `api_subscriptions`  (
  `user_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  `start_date` datetime(0) NOT NULL,
  `end_date` datetime(0) NOT NULL,
  `max_concurrency` int(11) NOT NULL,
  `perpetual` tinyint(1) NOT NULL DEFAULT 0,
  `modified_by_user_id` int(11) NOT NULL,
  `last_update` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP(0),
  PRIMARY KEY (`user_id`, `product_id`) USING BTREE,
  INDEX `idxStartDate`(`start_date`) USING BTREE,
  INDEX `idxEndDate`(`end_date`) USING BTREE,
  INDEX `idxProductId`(`product_id`) USING BTREE,
  CONSTRAINT `subscribed_product` FOREIGN KEY (`product_id`) REFERENCES `api_products` (`product_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `subscribed_user` FOREIGN KEY (`user_id`) REFERENCES `api_user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for api_user
-- ----------------------------
DROP TABLE IF EXISTS `api_user`;
CREATE TABLE `api_user`  (
  `user_id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `password` varchar(512) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `full_name` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `company` varchar(125) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `email_address` varchar(65) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `enabled` tinyint(1) NULL DEFAULT 0,
  `admin` tinyint(1) NULL DEFAULT 0,
  `user_agrees_date` datetime(0) NULL DEFAULT CURRENT_TIMESTAMP(0),
  `user_agrees_to_tracking` tinyint(1) NULL DEFAULT 0,
  `user_agrees_to_cookies` tinyint(1) NULL DEFAULT 0,
  `email_optin` tinyint(1) NOT NULL DEFAULT 1,
  `hide_activity` tinyint(1) NOT NULL DEFAULT 0,
  `parent_user_id` int(11) NOT NULL DEFAULT 0,
  `administrative_group_id` int(11) NOT NULL DEFAULT 64,
  `view_parent_user_reports` tinyint(1) NOT NULL DEFAULT 0,
  `deleted` tinyint(1) NOT NULL DEFAULT 0,
  `modified_by_user_id` int(11) NULL DEFAULT NULL,
  `added_by_user_id` int(11) NULL DEFAULT NULL,
  `added_date` datetime(0) NULL DEFAULT NULL,
  `last_update` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP(0) ON UPDATE CURRENT_TIMESTAMP(0),
  PRIMARY KEY (`user_id`) USING BTREE,
  UNIQUE INDEX `unique_username`(`username`) USING BTREE,
  INDEX `idxUsername`(`username`) USING BTREE,
  INDEX `user_administrative_group`(`administrative_group_id`) USING BTREE,
  CONSTRAINT `user_administrative_group` FOREIGN KEY (`administrative_group_id`) REFERENCES `api_administrative_groups` (`administrative_group_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB AUTO_INCREMENT = 119405 CHARACTER SET = utf8 COLLATE = utf8_general_ci COMMENT = 'A list of all authorized users, and the NOT_LOGGED_IN user, with ID=0' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for api_user_ip_ranges
-- ----------------------------
DROP TABLE IF EXISTS `api_user_ip_ranges`;
CREATE TABLE `api_user_ip_ranges`  (
  `ip_addresses_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `start_ip_address` bigint(20) NOT NULL,
  `end_ip_address` bigint(20) NOT NULL,
  `modified_by_user_id` int(11) NOT NULL,
  `last_update` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP(0),
  PRIMARY KEY (`ip_addresses_id`) USING BTREE,
  INDEX `idxSubsystemIdUserId`(`user_id`) USING BTREE,
  INDEX `idxStartIpAddress`(`start_ip_address`) USING BTREE,
  INDEX `idxEndIpAddress`(`end_ip_address`) USING BTREE,
  INDEX `idxUserId`(`user_id`) USING BTREE,
  INDEX `FK_ip_addresses_user_subsystem`(`user_id`) USING BTREE,
  CONSTRAINT `ip_user` FOREIGN KEY (`user_id`) REFERENCES `api_user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB AUTO_INCREMENT = 25024 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for api_user_property_name
-- ----------------------------
DROP TABLE IF EXISTS `api_user_property_name`;
CREATE TABLE `api_user_property_name`  (
  `user_property_name_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_property_name` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `user_property_data_type_id` smallint(6) NOT NULL,
  `sort_order` smallint(6) NOT NULL,
  `user_property_user_access_id` smallint(6) NOT NULL,
  `default_value` varchar(1000) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `display_width` smallint(6) NULL DEFAULT NULL,
  `display_height` smallint(6) NULL DEFAULT NULL,
  `modified_by_user_id` int(11) NOT NULL,
  `last_update` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP(0),
  PRIMARY KEY (`user_property_name_id`) USING BTREE,
  INDEX `FK_user_property_name_ref_user_property_data_type`(`user_property_data_type_id`) USING BTREE,
  INDEX `FK_user_property_name_ref_user_property_user_access`(`user_property_user_access_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 169 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for api_user_property_value
-- ----------------------------
DROP TABLE IF EXISTS `api_user_property_value`;
CREATE TABLE `api_user_property_value`  (
  `user_property_value_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `user_property_name_id` int(11) NOT NULL,
  `user_property_value` varchar(5000) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `modified_by_user_id` int(11) NOT NULL,
  `last_update` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP(0),
  PRIMARY KEY (`user_property_value_id`) USING BTREE,
  UNIQUE INDEX `IX_user_property_value`(`user_id`, `user_property_name_id`) USING BTREE,
  INDEX `idxUserPropertyNameId`(`user_property_name_id`) USING BTREE,
  CONSTRAINT `property_name` FOREIGN KEY (`user_property_name_id`) REFERENCES `api_user_property_name` (`user_property_name_id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `property_user` FOREIGN KEY (`user_id`) REFERENCES `api_user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB AUTO_INCREMENT = 577755 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for api_user_referrer_urls
-- ----------------------------
DROP TABLE IF EXISTS `api_user_referrer_urls`;
CREATE TABLE `api_user_referrer_urls`  (
  `referrer_urls_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `referrer_url` varchar(500) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `modified_by_user_id` int(11) NOT NULL,
  `last_update` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP(0),
  PRIMARY KEY (`referrer_urls_id`) USING BTREE,
  INDEX `idxSubsystemIdUserId`(`user_id`) USING BTREE,
  INDEX `idxReferrerUrl`(`referrer_url`(255)) USING BTREE,
  INDEX `idxUserId`(`user_id`) USING BTREE,
  INDEX `FK_referrer_urls_user_subsystem`(`user_id`) USING BTREE,
  CONSTRAINT `referral_url_user` FOREIGN KEY (`user_id`) REFERENCES `api_user` (`user_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB AUTO_INCREMENT = 2001 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for articles
-- ----------------------------
DROP TABLE IF EXISTS `articles`;
CREATE TABLE `articles`  (
  `articleID` varchar(24) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL DEFAULT '' COMMENT 'The PEP locator for this article',
  `arttype` varchar(4) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL DEFAULT '' COMMENT 'Article type, e.g., ART, COM, ERA',
  `authorMast` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL COMMENT 'Author names per masthead, e.g. Ronnie C. Lesser, Ph.D.',
  `hdgauthor` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL COMMENT 'The heading style author list, e.g., Lesser, R. C.',
  `hdgtitle` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL COMMENT 'The title for the heading',
  `srctitleseries` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL COMMENT 'Src title bibliogr abbrev style, e.g., Psychoanal. Dial.',
  `publisher` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci NOT NULL DEFAULT '' COMMENT 'Publisher, e.g., Cambridge, MA / London: Harvard Univ. Press',
  `jrnlcode` varchar(14) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL COMMENT 'PEP assigned Journal Code, e.g., IJP',
  `year` int(11) NULL DEFAULT NULL COMMENT 'Year of Publication',
  `vol` int(11) NULL DEFAULT NULL COMMENT 'Volume',
  `volsuffix` char(5) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL COMMENT 'Vol number suffix, e.g., S for supplements',
  `issue` char(5) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL DEFAULT '' COMMENT 'Issue number or designation, e.g., 1, or pilot',
  `pgrg` varchar(20) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL COMMENT 'Page range of article, e.g., 1-22',
  `pgstart` int(11) NULL DEFAULT NULL COMMENT 'Starting page number, negative for roman',
  `pgend` int(11) NULL DEFAULT NULL COMMENT 'Ending page number, use negative for roman',
  `source` varchar(10) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL COMMENT 'Source date',
  `preserve` int(11) NULL DEFAULT 0,
  `filename` varchar(255) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL COMMENT 'Path and filename of source file',
  `maintocID` varchar(20) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL,
  `newsecname` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci NULL DEFAULT NULL COMMENT 'When the article starts a new section in the TOC, name',
  `bktitle` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT 'Title of parent book which contains the article',
  `bkauthors` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT 'Authors of the parent book',
  `xmlref` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL COMMENT 'Bibliographic style reference for article, in XML',
  `references` int(11) NULL DEFAULT NULL,
  `doi` varchar(255) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL,
  `artkwds` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `artlang` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `updated` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP(0) ON UPDATE CURRENT_TIMESTAMP(0),
  PRIMARY KEY (`articleID`) USING BTREE,
  UNIQUE INDEX `Primary Key`(`articleID`) USING BTREE,
  UNIQUE INDEX `filename`(`filename`) USING BTREE,
  INDEX `xname`(`vol`) USING BTREE,
  INDEX `titlefulltext`(`hdgtitle`(333)) USING BTREE,
  INDEX `yrjrnlcode`(`jrnlcode`, `year`) USING BTREE,
  INDEX `voljrnlcode`(`jrnlcode`, `vol`) USING BTREE,
  INDEX `authorfulltext`(`hdgauthor`(255)) USING BTREE,
  INDEX `jrnlCodeIndiv`(`jrnlcode`) USING BTREE,
  FULLTEXT INDEX `hdgtitle`(`hdgtitle`),
  FULLTEXT INDEX `hdgauthor`(`hdgauthor`),
  FULLTEXT INDEX `xmlref`(`xmlref`),
  FULLTEXT INDEX `bktitle`(`bktitle`)
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci COMMENT = 'A PEP journal article, book or book section' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for filetracking
-- ----------------------------
DROP TABLE IF EXISTS `filetracking`;
CREATE TABLE `filetracking`  (
  `filePath` varchar(512) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `fileSize` int(11) NULL DEFAULT NULL,
  `fileModDate` decimal(18, 6) NULL,
  `buildDate` decimal(18, 6) NULL DEFAULT NULL,
  `solrServerURL` varchar(512) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  PRIMARY KEY (`filePath`, `solrServerURL`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for fullbiblioxml
-- ----------------------------
DROP TABLE IF EXISTS `fullbiblioxml`;
CREATE TABLE `fullbiblioxml`  (
  `articleID` varchar(24) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL,
  `internalID` varchar(25) CHARACTER SET latin1 COLLATE latin1_swedish_ci NOT NULL,
  `fullReference` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL,
  `rxCode` varchar(30) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL,
  `rxConfidence` double NOT NULL DEFAULT 0 COMMENT 'A value of 1 will never be automatically replaced',
  `updated` timestamp(0) NOT NULL DEFAULT CURRENT_TIMESTAMP(0) ON UPDATE CURRENT_TIMESTAMP(0),
  `fullRefText` text CHARACTER SET utf8 COLLATE utf8_general_ci NULL,
  `source` varchar(24) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT 'instance' COMMENT 'If it\'s refcorrections, this record came from the refcorrections table and should not be updated.',
  `journal` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT 'Record the journal name as extracted from the XML referennce.  Useful to sort and check reference.',
  `booktitle` varchar(255) CHARACTER SET utf8 COLLATE utf8_unicode_ci NULL DEFAULT NULL,
  `title` varchar(255) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL,
  `normalizedjournal` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `altArticleID` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  `doi` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL COMMENT 'Document Object Identifier for this reference',
  `relatedRXCode` varchar(30) CHARACTER SET latin1 COLLATE latin1_swedish_ci NULL DEFAULT NULL,
  `relatedRXConfidence` double NOT NULL DEFAULT 0,
  PRIMARY KEY (`articleID`, `internalID`) USING BTREE,
  UNIQUE INDEX `Primary Key`(`articleID`, `internalID`) USING BTREE,
  INDEX `articleID`(`articleID`) USING BTREE,
  INDEX `altArticleID`(`altArticleID`) USING BTREE,
  INDEX `titleIndex`(`title`) USING BTREE,
  INDEX `RefersTo`(`rxCode`) USING BTREE,
  FULLTEXT INDEX `fulreffullText`(`fullRefText`),
  FULLTEXT INDEX `titleFullText`(`title`)
) ENGINE = InnoDB CHARACTER SET = latin1 COLLATE = latin1_swedish_ci COMMENT = 'All bibliographic entries within PEP' ROW_FORMAT = Dynamic;

-- ----------------------------
-- View structure for vw_active_sessions
-- ----------------------------
DROP VIEW IF EXISTS `vw_active_sessions`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `vw_active_sessions` AS select `api_sessions`.`session_id` AS `session_id`,`api_sessions`.`user_id` AS `user_id`,`api_sessions`.`username` AS `username`,`api_sessions`.`user_ip` AS `user_ip`,`api_sessions`.`connected_via` AS `connected_via`,`api_sessions`.`referrer` AS `referrer`,`api_sessions`.`session_start` AS `session_start`,`api_sessions`.`session_end` AS `session_end`,`api_sessions`.`session_expires_time` AS `session_expires_time`,`api_sessions`.`access_token` AS `access_token`,`api_sessions`.`authenticated` AS `authenticated`,`api_sessions`.`api_client_id` AS `api_client_id`,`api_sessions`.`updated` AS `updated` from `api_sessions` where ((`api_sessions`.`user_id` <> 0) and isnull(`api_sessions`.`session_end`)) order by `api_sessions`.`session_start` desc;

-- ----------------------------
-- View structure for vw_api_productbase
-- ----------------------------
DROP VIEW IF EXISTS `vw_api_productbase`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `vw_api_productbase` AS select `api_productbase`.`basecode` AS `basecode`,`api_productbase`.`articleID` AS `articleID`,`api_productbase`.`active` AS `active`,`api_productbase`.`pep_class` AS `product_type`,`api_productbase`.`pep_class_qualifier` AS `product_type_qualifier`,`api_productbase`.`wall` AS `embargo`,`api_productbase`.`mainTOC` AS `mainTOC`,`api_productbase`.`first_author` AS `first_author`,`api_productbase`.`author` AS `author`,`api_productbase`.`title` AS `title`,`api_productbase`.`bibabbrev` AS `bibabbrev`,`api_productbase`.`ISSN` AS `ISSN`,`api_productbase`.`ISBN-10` AS `ISBN-10`,`api_productbase`.`ISBN-13` AS `ISBN-13`,`api_productbase`.`pages` AS `pages`,`api_productbase`.`Comment` AS `Comment`,`api_productbase`.`pepcode` AS `pepcode`,`api_productbase`.`publisher` AS `publisher`,`api_productbase`.`jrnl` AS `jrnl`,`api_productbase`.`pub_year` AS `pub_year`,`api_productbase`.`start_year` AS `start_year`,`api_productbase`.`end_year` AS `end_year`,`api_productbase`.`pep_url` AS `pep_url`,`api_productbase`.`language` AS `language`,`api_productbase`.`updated` AS `updated`,`api_productbase`.`pepversion` AS `pepversion`,`api_productbase`.`duplicate` AS `duplicate`,`api_productbase`.`landing_page` AS `landing_page`,`api_productbase`.`coverage_notes` AS `coverage_notes`,`api_productbase`.`landing_page_intro_html` AS `landing_page_intro_html`,`api_productbase`.`landing_page_end_html` AS `landing_page_end_html`,`api_productbase`.`google_books_link` AS `google_books_link` from `api_productbase`;

-- ----------------------------
-- View structure for vw_api_product_list_with_basecodes
-- ----------------------------
DROP VIEW IF EXISTS `vw_api_product_list_with_basecodes`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `vw_api_product_list_with_basecodes` AS select `api_products`.`product` AS `product`,`api_products`.`product_level` AS `product_level`,`api_products`.`product_id` AS `product_id`,`api_products`.`id_type` AS `id_type`,`api_productbase`.`pep_class` AS `pep_class`,`api_productbase`.`basecode` AS `basecode`,`api_productbase`.`articleID` AS `articleID`,`api_productbase`.`active` AS `in_production`,`api_productbase`.`pepcode` AS `pepcode`,`api_products`.`product_type` AS `product_type`,`api_products`.`free_access` AS `free_access`,`api_products`.`range_limited` AS `range_limited`,`api_products`.`embargo_length` AS `embargo_length`,`api_products`.`embargo_inverted` AS `embargo_inverted`,`api_products`.`range_start_year` AS `range_start_year`,`api_products`.`range_end_year` AS `range_end_year`,`api_products`.`active` AS `active` from ((`api_productbase` join `api_join_products_to_productbase` on((`api_join_products_to_productbase`.`basecode` = `api_productbase`.`basecode`))) join `api_products` on((`api_join_products_to_productbase`.`product_id` = `api_products`.`product_id`)));

-- ----------------------------
-- View structure for vw_api_session_endpoints_with_descriptor
-- ----------------------------
DROP VIEW IF EXISTS `vw_api_session_endpoints_with_descriptor`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `vw_api_session_endpoints_with_descriptor` AS select `api_session_endpoints`.`session_id` AS `session_id`,`api_session_endpoints`.`api_endpoint_id` AS `api_endpoint_id`,`api_session_endpoints`.`params` AS `params`,`api_session_endpoints`.`return_status_code` AS `return_status_code`,`api_session_endpoints`.`item_of_interest` AS `item_of_interest`,`api_session_endpoints`.`return_added_status_message` AS `return_added_status_message`,`api_session_endpoints`.`last_update` AS `last_update`,`api_endpoints`.`endpoint_url` AS `endpoint_url` from (`api_endpoints` join `api_session_endpoints` on((`api_session_endpoints`.`api_endpoint_id` = `api_endpoints`.`api_endpoint_id`)));

-- ----------------------------
-- View structure for vw_api_sourceinfodb
-- ----------------------------
DROP VIEW IF EXISTS `vw_api_sourceinfodb`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `vw_api_sourceinfodb` AS select `api_productbase`.`basecode` AS `pepsrccode`,`api_productbase`.`basecode` AS `basecode`,`api_productbase`.`active` AS `active`,`api_productbase`.`bibabbrev` AS `sourcetitleabbr`,`api_productbase`.`jrnl` AS `source`,`api_productbase`.`start_year` AS `start_year`,`api_productbase`.`end_year` AS `end_year`,`api_productbase`.`pep_url` AS `pep_url`,`api_productbase`.`language` AS `language`,`api_productbase`.`title` AS `sourcetitlefull`,`api_productbase`.`pep_class` AS `product_type`,`api_productbase`.`pep_class_qualifier` AS `product_type_qualifier`,`api_productbase`.`wall` AS `embargo`,`api_productbase`.`mainTOC` AS `mainTOC`,`api_productbase`.`author` AS `author`,`api_productbase`.`updated` AS `updated`,`api_productbase`.`landing_page` AS `landing_page`,`api_productbase`.`google_books_link` AS `google_books_link`,`api_productbase`.`pepversion` AS `pepversion`,`api_productbase`.`publisher` AS `publisher`,`api_productbase`.`ISSN` AS `ISSN`,`api_productbase`.`ISBN-10` AS `ISBN-10`,`api_productbase`.`ISBN-13` AS `ISBN-13`,`api_productbase`.`pages` AS `pages`,`api_productbase`.`articleID` AS `articleID`,`api_productbase`.`first_author` AS `first_author`,`api_productbase`.`bibabbrev` AS `bibabbrev`,`api_productbase`.`Comment` AS `Comment`,`api_productbase`.`pepcode` AS `pepcode`,`api_productbase`.`pub_year` AS `pub_year`,`api_productbase`.`duplicate` AS `duplicate`,`api_productbase`.`coverage_notes` AS `coverage_notes`,`api_productbase`.`landing_page_intro_html` AS `landing_page_intro_html`,`api_productbase`.`landing_page_end_html` AS `landing_page_end_html` from `api_productbase`;

-- ----------------------------
-- View structure for vw_api_user
-- ----------------------------
DROP VIEW IF EXISTS `vw_api_user`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `vw_api_user` AS select `api_user`.`user_id` AS `user_id`,`api_user`.`username` AS `username`,`api_user`.`full_name` AS `full_name`,`api_user`.`company` AS `company`,`api_user`.`email_address` AS `email_address`,`api_user`.`enabled` AS `enabled`,`api_user`.`parent_user_id` AS `parent_user_id`,`api_user`.`password` AS `password`,`api_user`.`user_agrees_date` AS `user_agrees_date`,`api_user`.`user_agrees_to_tracking` AS `user_agrees_to_tracking`,`api_user`.`user_agrees_to_cookies` AS `user_agrees_to_cookies`,`api_user`.`admin` AS `admin`,`api_user`.`email_optin` AS `email_optin`,`api_user`.`administrative_group_id` AS `administrative_group_id` from `api_user`;

-- ----------------------------
-- View structure for vw_api_user_subscriptions_with_basecodes
-- ----------------------------
DROP VIEW IF EXISTS `vw_api_user_subscriptions_with_basecodes`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `vw_api_user_subscriptions_with_basecodes` AS select `api_subscriptions`.`user_id` AS `user_id`,`api_subscriptions`.`start_date` AS `start_date`,`api_subscriptions`.`end_date` AS `end_date`,`api_subscriptions`.`perpetual` AS `perpetual`,`api_subscriptions`.`max_concurrency` AS `max_concurrency`,`api_products`.`product` AS `product`,`api_products`.`product_level` AS `product_level`,`api_products`.`product_id` AS `product_id`,`api_products`.`id_type` AS `id_type`,`api_productbase`.`pep_class` AS `pep_class`,`api_productbase`.`basecode` AS `basecode`,`api_productbase`.`articleID` AS `articleID`,`api_productbase`.`active` AS `in_production`,`api_productbase`.`pepcode` AS `pepcode`,`api_products`.`product_type` AS `product_type`,`api_products`.`free_access` AS `free_access`,`api_products`.`range_limited` AS `range_limited`,`api_productbase`.`wall` AS `embargo_length`,`api_products`.`embargo_inverted` AS `embargo_inverted`,`api_products`.`range_start_year` AS `range_start_year`,`api_products`.`range_end_year` AS `range_end_year`,`api_products`.`active` AS `active` from (((`api_productbase` join `api_join_products_to_productbase` on((`api_join_products_to_productbase`.`basecode` = `api_productbase`.`basecode`))) join `api_products` on((`api_join_products_to_productbase`.`product_id` = `api_products`.`product_id`))) join `api_subscriptions` on((`api_subscriptions`.`product_id` = `api_products`.`product_id`))) where (((`api_subscriptions`.`end_date` > curdate()) and (`api_subscriptions`.`start_date` < curdate())) or (`api_subscriptions`.`perpetual` = 1));

-- ----------------------------
-- View structure for vw_latest_session_activity
-- ----------------------------
DROP VIEW IF EXISTS `vw_latest_session_activity`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `vw_latest_session_activity` AS select `api_session_endpoints`.`session_id` AS `session_id`,max(`api_session_endpoints`.`last_update`) AS `latest_activity` from `api_session_endpoints` group by `api_session_endpoints`.`session_id` order by max(`api_session_endpoints`.`last_update`) desc;

-- ----------------------------
-- View structure for vw_products_flattened
-- ----------------------------
DROP VIEW IF EXISTS `vw_products_flattened`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `vw_products_flattened` AS select `product`.`product_id` AS `child_product_id`,`product`.`product` AS `child_product`,`product`.`basecode` AS `child_basecode`,`product`.`product_level` AS `child_product_level`,`parent`.`product_id` AS `parent_product_id`,`parent`.`product` AS `parent_product`,`parent`.`basecode` AS `parent_basecode`,`parent`.`product_level` AS `parent_product_level`,`product`.`inherit_parent_metadata` AS `inherit_parent_metadata` from (`api_products` `parent` join `api_products` `product` on(((`parent`.`product_level` = 1) and (`product`.`parent_product_id` = `parent`.`product_id`)))) union select `product`.`product_id` AS `child_product_id`,`product`.`product` AS `child_product`,`product`.`basecode` AS `child_basecode`,`product`.`product_level` AS `child_product_level`,`parent`.`product_id` AS `parent_product_id`,`parent`.`product` AS `parent_product`,`parent`.`basecode` AS `parent_basecode`,`parent`.`product_level` AS `parent_product_level`,`product`.`inherit_parent_metadata` AS `inherit_parent_metadata` from (`api_products` `parent` join `api_products` `product` on(((`parent`.`product_level` = 2) and (`product`.`parent_product_id` = `parent`.`product_id`)))) union select `product`.`product_id` AS `child_product_id`,`product`.`product` AS `child_product`,`product`.`basecode` AS `child_basecode`,`product`.`product_level` AS `child_product_level`,`parent`.`product_id` AS `parent_product_id`,`parent`.`product` AS `parent_product`,`parent`.`basecode` AS `parent_basecode`,`parent`.`product_level` AS `parent_product_level`,`product`.`inherit_parent_metadata` AS `inherit_parent_metadata` from (`api_products` `parent` join `api_products` `product` on(((`parent`.`product_level` = 3) and (`product`.`parent_product_id` = `parent`.`product_id`))));

-- ----------------------------
-- View structure for vw_products_with_productbase
-- ----------------------------
DROP VIEW IF EXISTS `vw_products_with_productbase`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `vw_products_with_productbase` AS select `api_products`.`product_id` AS `product_id`,`api_products`.`basecode` AS `basecode`,`api_products`.`product` AS `product`,`api_products`.`product_level` AS `product_level`,`api_productbase`.`pep_class` AS `product_type`,`api_productbase`.`pep_class_qualifier` AS `product_type_qualifier`,`api_products`.`active` AS `active`,`api_products`.`range_limited` AS `range_limited`,`api_products`.`embargo_length` AS `embargo_length`,`api_products`.`embargo_inverted` AS `embargo_inverted`,`api_products`.`range_start_year` AS `range_start_year`,`api_products`.`range_end_year` AS `range_end_year`,`api_productbase`.`start_year` AS `start_year`,`api_productbase`.`end_year` AS `end_year`,`api_productbase`.`pages` AS `pages`,`api_productbase`.`bibabbrev` AS `bibabbrev`,`api_productbase`.`title` AS `title`,`api_productbase`.`author` AS `author`,`api_productbase`.`ISSN` AS `ISSN`,`api_productbase`.`language` AS `language`,`api_products`.`id_code_1` AS `id_code_1`,`api_productbase`.`ISBN-10` AS `ISBN-10`,`api_productbase`.`ISBN-13` AS `ISBN-13`,`api_products`.`id_code_2` AS `id_code_2`,`api_productbase`.`pepcode` AS `pepcode`,`api_productbase`.`articleID` AS `articleID`,`api_products`.`free_access` AS `free_access`,`api_productbase`.`mainTOC` AS `mainTOC`,`api_productbase`.`first_author` AS `first_author`,`api_productbase`.`pub_year` AS `pub_year`,`api_productbase`.`jrnl` AS `jrnl`,`api_productbase`.`publisher` AS `publisher` from (`api_products` left join `api_productbase` on((`api_products`.`basecode` = `api_productbase`.`basecode`)));

-- ----------------------------
-- View structure for vw_stat_cited_crosstab
-- ----------------------------
DROP VIEW IF EXISTS `vw_stat_cited_crosstab`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `vw_stat_cited_crosstab` AS select `r0`.`cited_document_id` AS `cited_document_id`,any_value(coalesce(`r1`.`count5`,0)) AS `count5`,any_value(coalesce(`r2`.`count10`,0)) AS `count10`,any_value(coalesce(`r3`.`count20`,0)) AS `count20`,any_value(coalesce(`r4`.`countAll`,0)) AS `countAll` from ((((((select distinct `opascentral`.`fullbiblioxml`.`articleID` AS `articleID`,`opascentral`.`fullbiblioxml`.`internalID` AS `internalID`,`opascentral`.`fullbiblioxml`.`fullReference` AS `fullReference`,`opascentral`.`fullbiblioxml`.`rxCode` AS `cited_document_id` from `opascentral`.`fullbiblioxml`)) `r0` left join `opascentral`.`vw_stat_cited_in_last_5_years` `r1` on((`r1`.`cited_document_id` = `r0`.`cited_document_id`))) left join `opascentral`.`vw_stat_cited_in_last_10_years` `r2` on((`r2`.`cited_document_id` = `r0`.`cited_document_id`))) left join `opascentral`.`vw_stat_cited_in_last_20_years` `r3` on((`r3`.`cited_document_id` = `r0`.`cited_document_id`))) left join `opascentral`.`vw_stat_cited_in_all_years` `r4` on((`r4`.`cited_document_id` = `r0`.`cited_document_id`))) where ((`r0`.`cited_document_id` is not null) and (`r0`.`cited_document_id` <> 'None') and (substr(`r0`.`cited_document_id`,1,3) not in ('ZBK','IPL','SE.','GW.'))) group by `r0`.`cited_document_id` order by `countAll` desc;

-- ----------------------------
-- View structure for vw_stat_cited_crosstab_with_details
-- ----------------------------
DROP VIEW IF EXISTS `vw_stat_cited_crosstab_with_details`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `vw_stat_cited_crosstab_with_details` AS select `vw_stat_cited_crosstab`.`cited_document_id` AS `cited_document_id`,`vw_stat_cited_crosstab`.`count5` AS `count5`,`vw_stat_cited_crosstab`.`count10` AS `count10`,`vw_stat_cited_crosstab`.`count20` AS `count20`,`vw_stat_cited_crosstab`.`countAll` AS `countAll`,`opascentral`.`articles`.`hdgauthor` AS `hdgauthor`,`opascentral`.`articles`.`hdgtitle` AS `hdgtitle`,`opascentral`.`articles`.`srctitleseries` AS `srctitleseries`,`opascentral`.`articles`.`year` AS `year`,`opascentral`.`articles`.`vol` AS `vol`,`opascentral`.`articles`.`pgrg` AS `pgrg` from (`opascentral`.`vw_stat_cited_crosstab` join `opascentral`.`articles` on((`vw_stat_cited_crosstab`.`cited_document_id` = `opascentral`.`articles`.`articleID`))) order by `vw_stat_cited_crosstab`.`countAll` desc;

-- ----------------------------
-- View structure for vw_stat_cited_in_all_years
-- ----------------------------
DROP VIEW IF EXISTS `vw_stat_cited_in_all_years`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `vw_stat_cited_in_all_years` AS select `api_biblioxml`.`bib_rx` AS `cited_document_id`,count(0) AS `countAll` from (`api_biblioxml` join `api_articles` `citing_article`) where ((`api_biblioxml`.`art_id` = `citing_article`.`art_id`) and (`api_biblioxml`.`bib_rx` is not null) and (`api_biblioxml`.`bib_rx` <> '') and (substr(`api_biblioxml`.`bib_rx`,1,3) not in ('ZBK','IPL','SE.','GW.'))) group by `api_biblioxml`.`bib_rx` order by `countAll` desc;

-- ----------------------------
-- View structure for vw_stat_cited_in_last_10_years
-- ----------------------------
DROP VIEW IF EXISTS `vw_stat_cited_in_last_10_years`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `vw_stat_cited_in_last_10_years` AS select `api_biblioxml`.`bib_rx` AS `cited_document_id`,count(0) AS `count10` from (`api_biblioxml` join `api_articles` `citing_article`) where ((`api_biblioxml`.`art_id` = `citing_article`.`art_id`) and (`api_biblioxml`.`bib_rx` is not null) and (`api_biblioxml`.`bib_rx` <> '') and (`citing_article`.`art_year` > (year(now()) - 10)) and (substr(`api_biblioxml`.`bib_rx`,1,3) not in ('ZBK','IPL','SE.','GW.'))) group by `api_biblioxml`.`bib_rx` order by `count10` desc;

-- ----------------------------
-- View structure for vw_stat_cited_in_last_20_years
-- ----------------------------
DROP VIEW IF EXISTS `vw_stat_cited_in_last_20_years`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `vw_stat_cited_in_last_20_years` AS select `api_biblioxml`.`bib_rx` AS `cited_document_id`,count(0) AS `count20` from (`api_biblioxml` join `api_articles` `citing_article`) where ((`api_biblioxml`.`art_id` = `citing_article`.`art_id`) and (`api_biblioxml`.`bib_rx` is not null) and (`api_biblioxml`.`bib_rx` <> '') and (`citing_article`.`art_year` > (year(now()) - 20)) and (substr(`api_biblioxml`.`bib_rx`,1,3) not in ('ZBK','IPL','SE.','GW.'))) group by `api_biblioxml`.`bib_rx` order by `count20` desc;

-- ----------------------------
-- View structure for vw_stat_cited_in_last_5_years
-- ----------------------------
DROP VIEW IF EXISTS `vw_stat_cited_in_last_5_years`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `vw_stat_cited_in_last_5_years` AS select `api_biblioxml`.`bib_rx` AS `cited_document_id`,count(0) AS `count5` from (`api_biblioxml` join `api_articles` `citing_article`) where ((`api_biblioxml`.`art_id` = `citing_article`.`art_id`) and (`api_biblioxml`.`bib_rx` is not null) and (`api_biblioxml`.`bib_rx` <> '') and (`citing_article`.`art_year` > (year(now()) - 5)) and (substr(`api_biblioxml`.`bib_rx`,1,3) not in ('ZBK','IPL','SE.','GW.'))) group by `api_biblioxml`.`bib_rx` order by `count5` desc;

-- ----------------------------
-- View structure for vw_stat_docviews_crosstab
-- ----------------------------
DROP VIEW IF EXISTS `vw_stat_docviews_crosstab`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `vw_stat_docviews_crosstab` AS select `r0`.`document_id` AS `document_id`,any_value(max(`r0`.`last_viewed`)) AS `last_viewed`,any_value(coalesce(`r1`.`views`,0)) AS `lastweek`,any_value(coalesce(`r2`.`views`,0)) AS `lastmonth`,any_value(coalesce(`r3`.`views`,0)) AS `last6months`,any_value(coalesce(`r5`.`views`,0)) AS `last12months`,any_value(coalesce(`r4`.`views`,0)) AS `lastcalyear` from (((((((select distinct `opascentral`.`api_docviews`.`document_id` AS `document_id`,`opascentral`.`api_docviews`.`last_update` AS `last_viewed` from `opascentral`.`api_docviews`)) `r0` left join `opascentral`.`vw_stat_docviews_lastweek` `r1` on((`r1`.`document_id` = `r0`.`document_id`))) left join `opascentral`.`vw_stat_docviews_lastmonth` `r2` on((`r2`.`document_id` = `r0`.`document_id`))) left join `opascentral`.`vw_stat_docviews_lastsixmonths` `r3` on((`r3`.`document_id` = `r0`.`document_id`))) left join `opascentral`.`vw_stat_docviews_lastcalyear` `r4` on((`r4`.`document_id` = `r0`.`document_id`))) left join `opascentral`.`vw_stat_docviews_last12months` `r5` on((`r5`.`document_id` = `r0`.`document_id`))) where ((`r0`.`document_id` is not null) and (`r0`.`document_id` <> 'None')) group by `r0`.`document_id`;

-- ----------------------------
-- View structure for vw_stat_docviews_last12months
-- ----------------------------
DROP VIEW IF EXISTS `vw_stat_docviews_last12months`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `vw_stat_docviews_last12months` AS select `api_docviews`.`document_id` AS `document_id`,count(0) AS `views` from `api_docviews` where ((`api_docviews`.`last_update` > (now() - interval 12 month)) and (`api_docviews`.`type` = 'Document')) group by `api_docviews`.`document_id`;

-- ----------------------------
-- View structure for vw_stat_docviews_lastcalyear
-- ----------------------------
DROP VIEW IF EXISTS `vw_stat_docviews_lastcalyear`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `vw_stat_docviews_lastcalyear` AS select `api_docviews`.`document_id` AS `document_id`,count(0) AS `views` from `api_docviews` where ((year(`api_docviews`.`last_update`) = (year(now()) - 1)) and (`api_docviews`.`type` = 'Document')) group by `api_docviews`.`document_id`;

-- ----------------------------
-- View structure for vw_stat_docviews_lastmonth
-- ----------------------------
DROP VIEW IF EXISTS `vw_stat_docviews_lastmonth`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `vw_stat_docviews_lastmonth` AS select `api_docviews`.`document_id` AS `document_id`,count(0) AS `views` from `api_docviews` where ((`api_docviews`.`last_update` > (now() - interval 1 month)) and (`api_docviews`.`type` = 'Document')) group by `api_docviews`.`document_id`;

-- ----------------------------
-- View structure for vw_stat_docviews_lastsixmonths
-- ----------------------------
DROP VIEW IF EXISTS `vw_stat_docviews_lastsixmonths`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `vw_stat_docviews_lastsixmonths` AS select `api_docviews`.`document_id` AS `document_id`,count(0) AS `views` from `api_docviews` where ((`api_docviews`.`last_update` > (now() - interval 6 month)) and (`api_docviews`.`type` = 'Document')) group by `api_docviews`.`document_id`;

-- ----------------------------
-- View structure for vw_stat_docviews_lastweek
-- ----------------------------
DROP VIEW IF EXISTS `vw_stat_docviews_lastweek`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `vw_stat_docviews_lastweek` AS select `api_docviews`.`document_id` AS `document_id`,any_value(`api_docviews`.`type`) AS `view_type`,count(0) AS `views` from `api_docviews` where ((`api_docviews`.`last_update` > (now() - interval 7 day)) and (`api_docviews`.`type` = 'Document')) group by `api_docviews`.`document_id`;

-- ----------------------------
-- View structure for vw_stat_most_viewed
-- ----------------------------
DROP VIEW IF EXISTS `vw_stat_most_viewed`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `vw_stat_most_viewed` AS select `vw_stat_docviews_crosstab`.`document_id` AS `document_id`,`vw_stat_docviews_crosstab`.`last_viewed` AS `last_viewed`,coalesce(`vw_stat_docviews_crosstab`.`lastweek`,0) AS `lastweek`,coalesce(`vw_stat_docviews_crosstab`.`lastmonth`,0) AS `lastmonth`,coalesce(`vw_stat_docviews_crosstab`.`last6months`,0) AS `last6months`,coalesce(`vw_stat_docviews_crosstab`.`last12months`,0) AS `last12months`,coalesce(`vw_stat_docviews_crosstab`.`lastcalyear`,0) AS `lastcalyear`,`opascentral`.`articles`.`hdgauthor` AS `hdgauthor`,`opascentral`.`articles`.`hdgtitle` AS `hdgtitle`,`opascentral`.`articles`.`srctitleseries` AS `srctitleseries`,`opascentral`.`articles`.`publisher` AS `publisher`,`opascentral`.`articles`.`jrnlcode` AS `jrnlcode`,`opascentral`.`articles`.`year` AS `pubyear`,`opascentral`.`articles`.`vol` AS `vol`,`opascentral`.`articles`.`pgrg` AS `pgrg`,`opascentral`.`api_products`.`product_type` AS `source_type`,`opascentral`.`articles`.`preserve` AS `preserve`,`opascentral`.`articles`.`filename` AS `filename`,`opascentral`.`articles`.`bktitle` AS `bktitle`,`opascentral`.`articles`.`bkauthors` AS `bkauthors`,`opascentral`.`articles`.`xmlref` AS `xmlref`,`opascentral`.`articles`.`authorMast` AS `authorMast`,`opascentral`.`articles`.`issue` AS `issue`,`opascentral`.`articles`.`updated` AS `updated` from ((`opascentral`.`vw_stat_docviews_crosstab` join `opascentral`.`articles` on((convert(`opascentral`.`articles`.`articleID` using utf8) = convert(`vw_stat_docviews_crosstab`.`document_id` using utf8)))) left join `opascentral`.`api_products` on((convert(`opascentral`.`articles`.`jrnlcode` using utf8) = `opascentral`.`api_products`.`basecode`)));

-- ----------------------------
-- View structure for vw_subscriptions
-- ----------------------------
DROP VIEW IF EXISTS `vw_subscriptions`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `vw_subscriptions` AS select `api_user`.`username` AS `username`,`api_user`.`user_id` AS `user_id`,`api_user`.`enabled` AS `enabled`,`api_products`.`product` AS `product`,`api_products`.`parent_product_id` AS `parent_product_id`,`api_products`.`product_id` AS `product_id`,`api_subscriptions`.`start_date` AS `start_date`,`api_subscriptions`.`end_date` AS `end_date`,`api_subscriptions`.`max_concurrency` AS `max_concurrency`,`api_subscriptions`.`perpetual` AS `perpetual` from ((`api_user` join `api_subscriptions` on((`api_subscriptions`.`user_id` = `api_user`.`user_id`))) join `api_products` on((`api_subscriptions`.`product_id` = `api_products`.`product_id`)));

-- ----------------------------
-- View structure for vw_user_active_subscriptions
-- ----------------------------
DROP VIEW IF EXISTS `vw_user_active_subscriptions`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `vw_user_active_subscriptions` AS select `api_user`.`user_id` AS `user_id`,`api_user`.`username` AS `username`,`api_user`.`company` AS `company`,`api_user`.`enabled` AS `enabled`,`api_user`.`last_update` AS `last_update`,`api_subscriptions`.`start_date` AS `start_date`,`api_subscriptions`.`end_date` AS `end_date`,`api_subscriptions`.`max_concurrency` AS `max_concurrency`,`api_subscriptions`.`product_id` AS `product_id`,`api_products`.`product` AS `product`,`api_user`.`admin` AS `admin`,`api_user`.`password` AS `password` from ((`api_user` join `api_subscriptions` on((`api_subscriptions`.`user_id` = `api_user`.`user_id`))) join `api_products` on((`api_subscriptions`.`product_id` = `api_products`.`product_id`))) where (((`api_user`.`enabled` = TRUE) and (`api_subscriptions`.`end_date` > now())) or (`api_subscriptions`.`perpetual` = TRUE));

-- ----------------------------
-- View structure for vw_user_referred
-- ----------------------------
DROP VIEW IF EXISTS `vw_user_referred`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `vw_user_referred` AS select `api_user`.`user_id` AS `user_id`,`api_user`.`username` AS `username`,`api_user`.`enabled` AS `enabled`,`api_user`.`company` AS `company`,`api_user`.`email_address` AS `email_address`,`api_user_referrer_urls`.`referrer_url` AS `referrer_url` from (`api_user` left join `api_user_referrer_urls` on((`api_user_referrer_urls`.`user_id` = `api_user`.`user_id`))) order by `api_user`.`user_id`;

-- ----------------------------
-- View structure for vw_user_referrer_account_management
-- ----------------------------
DROP VIEW IF EXISTS `vw_user_referrer_account_management`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `vw_user_referrer_account_management` AS select `api_user`.`username` AS `username`,`api_user`.`company` AS `company`,`api_user`.`email_address` AS `email_address`,`api_user`.`admin` AS `admin`,`api_user`.`user_agrees_date` AS `user_agrees_date`,`api_user`.`user_agrees_to_tracking` AS `user_agrees_to_tracking`,`api_user`.`user_agrees_to_cookies` AS `user_agrees_to_cookies`,`api_user`.`added_date` AS `added_date`,`api_user`.`last_update` AS `last_update`,`vw_user_referred`.`referrer_url` AS `referrer_url`,`api_user`.`enabled` AS `enabled` from (`api_user` join `vw_user_referred` on((`vw_user_referred`.`user_id` = `api_user`.`user_id`)));

-- ----------------------------
-- View structure for vw_user_session_activity
-- ----------------------------
DROP VIEW IF EXISTS `vw_user_session_activity`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `vw_user_session_activity` AS select `api_user`.`username` AS `username`,`api_user`.`company` AS `company`,`api_user`.`enabled` AS `enabled`,`api_sessions`.`user_ip` AS `user_ip`,`api_sessions`.`connected_via` AS `connected_via`,`api_sessions`.`referrer` AS `referrer`,`api_sessions`.`session_start` AS `session_start`,`api_sessions`.`session_end` AS `session_end`,`api_session_endpoints`.`item_of_interest` AS `item_of_interest`,`api_endpoints`.`endpoint_url` AS `endpoint_url`,`api_session_endpoints`.`params` AS `params`,`api_session_endpoints`.`return_status_code` AS `return_status_code`,`api_session_endpoints`.`return_added_status_message` AS `return_added_status_message`,`api_session_endpoints`.`last_update` AS `last_update`,`api_session_endpoints`.`session_id` AS `session_id`,`api_user`.`user_id` AS `user_id` from (((`api_user` join `api_sessions` on((`api_sessions`.`user_id` = `api_user`.`user_id`))) join `api_session_endpoints` on((`api_session_endpoints`.`session_id` = `api_sessions`.`session_id`))) join `api_endpoints` on((`api_endpoints`.`api_endpoint_id` = `api_session_endpoints`.`api_endpoint_id`))) order by `api_endpoints`.`last_update` desc;

-- ----------------------------
-- View structure for vw_user_subscriptions_products
-- ----------------------------
DROP VIEW IF EXISTS `vw_user_subscriptions_products`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `vw_user_subscriptions_products` AS select `api_user`.`user_id` AS `user_id`,`api_user`.`username` AS `username`,`api_products`.`product` AS `product`,`api_products`.`basecode` AS `basecode`,`api_products`.`product_type` AS `product_type`,`api_user`.`email_address` AS `email_address`,`api_user`.`added_date` AS `added_date`,`api_subscriptions`.`max_concurrency` AS `max_concurrency`,`api_subscriptions`.`product_id` AS `product_id`,`api_subscriptions`.`start_date` AS `start_date`,`api_subscriptions`.`end_date` AS `end_date`,`api_user`.`company` AS `company`,`api_products`.`product_comment` AS `product_comment` from ((`api_user` join `api_subscriptions` on((`api_subscriptions`.`user_id` = `api_user`.`user_id`))) join `api_products` on((`api_products`.`product_id` = `api_subscriptions`.`product_id`)));

-- ----------------------------
-- View structure for xxxvw_products_with_productbase
-- ----------------------------
DROP VIEW IF EXISTS `xxxvw_products_with_productbase`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `xxxvw_products_with_productbase` AS select `api_products`.`product_id` AS `product_id`,`api_products`.`product` AS `product`,`api_productbase`.`basecode` AS `basecode`,`api_productbase`.`wall` AS `wall`,`api_products`.`product_type` AS `product_type`,`api_products`.`last_update` AS `last_update`,`api_productbase`.`active` AS `active`,`api_productbase`.`pep_class` AS `pep_class` from (`api_products` join `api_productbase` on((`api_productbase`.`basecode` = `api_products`.`basecode`)));

-- ----------------------------
-- View structure for xxx_vw_products
-- ----------------------------
DROP VIEW IF EXISTS `xxx_vw_products`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `xxx_vw_products` AS select `api_products`.`product_id` AS `product_id`,`api_products`.`subsystem_id` AS `subsystem_id`,`api_products`.`product` AS `product`,`api_products`.`product_level` AS `product_level`,`api_products`.`product_type` AS `product_type`,`api_products`.`basecode` AS `basecode`,`api_products`.`parent_product_id` AS `parent_product_id`,`api_products`.`inherit_parent_metadata` AS `inherit_parent_metadata`,`api_products`.`id_type` AS `id_type`,`api_products`.`id_code_1` AS `id_code_1`,`api_products`.`id_code_2` AS `id_code_2`,`api_products`.`active` AS `active`,`api_products`.`range_limited` AS `range_limited`,`api_products`.`embargo_length` AS `embargo_length`,`api_products`.`range_start_date` AS `range_start_date_allowed`,`api_products`.`range_end_date` AS `range_end_date_allowed`,`api_products`.`group_sort_order` AS `group_sort_order`,`api_products`.`hide_in_product_access` AS `hide_in_product_access`,`api_products`.`hide_in_report_list` AS `hide_in_report_list`,`api_products`.`last_update` AS `last_update`,`api_products`.`free_access` AS `free_access` from `api_products`;

-- ----------------------------
-- View structure for xxx_vw_user_products
-- ----------------------------
DROP VIEW IF EXISTS `xxx_vw_user_products`;
CREATE ALGORITHM = UNDEFINED SQL SECURITY DEFINER VIEW `xxx_vw_user_products` AS select `api_subscriptions`.`user_id` AS `user_id`,`api_user`.`username` AS `username`,`vw_products_with_productbase`.`product_id` AS `product_id`,`vw_products_with_productbase`.`basecode` AS `basecode`,`vw_products_with_productbase`.`product` AS `product`,`vw_products_with_productbase`.`product_level` AS `product_level`,`vw_products_with_productbase`.`product_type` AS `product_type`,`vw_products_with_productbase`.`product_type_qualifier` AS `product_type_qualifier`,`vw_products_with_productbase`.`active` AS `active`,`vw_products_with_productbase`.`range_limited` AS `range_limited`,`vw_products_with_productbase`.`embargo_length` AS `embargo_length`,`vw_products_with_productbase`.`embargo_inverted` AS `embargo_inverted`,`vw_products_with_productbase`.`range_start_date` AS `range_start_date`,`vw_products_with_productbase`.`range_end_date` AS `range_end_date`,`vw_products_with_productbase`.`start_year` AS `start_year`,`vw_products_with_productbase`.`end_year` AS `end_year`,`vw_products_with_productbase`.`pages` AS `pages`,`vw_products_with_productbase`.`bibabbrev` AS `bibabbrev`,`vw_products_with_productbase`.`title` AS `title`,`vw_products_with_productbase`.`author` AS `author`,`vw_products_with_productbase`.`ISSN` AS `ISSN`,`vw_products_with_productbase`.`language` AS `language`,`vw_products_with_productbase`.`id_code_1` AS `id_code_1`,`vw_products_with_productbase`.`ISBN-10` AS `ISBN-10`,`vw_products_with_productbase`.`ISBN-13` AS `ISBN-13`,`vw_products_with_productbase`.`id_code_2` AS `id_code_2`,`vw_products_with_productbase`.`pepcode` AS `pepcode`,`vw_products_with_productbase`.`articleID` AS `articleID`,`vw_products_with_productbase`.`free_access` AS `free_access`,`vw_products_with_productbase`.`mainTOC` AS `mainTOC`,`vw_products_with_productbase`.`first_author` AS `first_author`,`vw_products_with_productbase`.`pub_year` AS `pub_year`,`vw_products_with_productbase`.`jrnl` AS `jrnl`,`vw_products_with_productbase`.`publisher` AS `publisher` from ((`vw_products_with_productbase` join `api_subscriptions` on((`vw_products_with_productbase`.`product` = `api_subscriptions`.`product_id`))) join `api_user` on((`api_subscriptions`.`user_id` = `api_user`.`user_id`)));

-- ----------------------------
-- Triggers structure for table api_products
-- ----------------------------
DROP TRIGGER IF EXISTS `ins_added_date`;
delimiter ;;
CREATE TRIGGER `ins_added_date` BEFORE INSERT ON `api_products` FOR EACH ROW SET NEW.date_added = now()
;;
delimiter ;

SET FOREIGN_KEY_CHECKS = 1;
