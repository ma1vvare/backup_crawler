#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import logging
import gridfs
from pymongo import MongoClient, HASHED
from bson.objectid import ObjectId
import traceback
from ConfigParser import ConfigParser

class DB():

    def __init__(self, config_name='TEST'):#set config server

        # Read db.config
        config_file = os.path.dirname(__file__)+"/db.conf"
        parser = ConfigParser()
        parser.read(config_file)

        db_server = parser.get(config_name, 'ip')
        db_name = parser.get(config_name, 'database')

        try:
            conn = MongoClient(host=db_server)
        except:
            logging.error("DB connect error!")
        finally:
            logging.debug("Using DB server: {0}, DB: {1}".format(db_server,
                                                                 db_name))
            self.db = conn[db_name]
            self.fs = gridfs.GridFS(self.db)
            #store large binary objects (e.g. files) in MongoDB.
        self.ensure_index()

    def ensure_index(self):
        self.db.fs.files.ensure_index(
            'filename', unique=True, background=True)
        self.db.apk.ensure_index(
            'vt_scan', background=True)
        self.db.apk.ensure_index(
            [('av_result', HASHED)], background=True, sparse=True)

    def _clean_query(self, queries):
        """Clean unexcepted fields
        """
        expected_fields = ('_id',
                           'source',
                           'submit_date',  # date of APK submit to DB
                           'name',
                           'version',
                           'size',
                           'requirements',
                           'pgname',
                           'upload_date',  # date of APK publish
                           'apkdata',
                           'activities',
                           'app_icon_path',
                           'libraries',
                           'main_activity',
                           'providers',
                           'receivers',
                           'services',
                           'signatures',
                           'title',
                           'sub_title',
                           'rank',
                           'sha1',
                           'crc32',
                           'ssdeep',
                           'sha256',
                           'sha512',
                           'md5',
                           'vt_scan',
                           'url_scan',
                           'url_number',
                           'url_result',
                           'av_result',
                           'normal_permission',
                           'danger_permission',
                           'interesting_strings_URL',
                           'interesting_strings_IP'
                           )

        # filter unexpect fields
        for key in queries.keys():
            if key not in expected_fields:
                queries.pop(key)

        return queries

    def insert_apk(self, origin_payload):
        """This function inserts the apk & information to mongo DB.

        Args:
            payload (dict): APK file & information.

        >>>insert_apk({binary:'foo', version:'0.1', name:'bar'})

        """

        payload = self._clean_query(origin_payload)
        # insert file to gridfs and check if file is already existed
        if self.fs.exists({'filename': payload['sha512']}):
            print "File already exists!"
            logging.debug(
                "{0} File already exists!".format(
                    payload['pgname']))
            file_id = self.fs.find_one(
                {'filename': payload['sha512']})._id
        else:
            file_id = self.fs.put(
                payload['apkdata'],
                filename=payload['sha512'])

        payload['apkdata'] = file_id

        # insert data to apk collection
        try:

            payload['_id'] = ObjectId()
            self.db.apk.insert_one(payload)
            # put the apk data in to db-apk
        except Exception,e:
            traceback.print_exc()
            print "Error insert data!"
            # logging.info("Error insert data!")

    def get_apk(self, origin_queries):
        """find documents
        """
        limit = origin_queries.get('limit', 0)
        queries = self._clean_query(origin_queries)

        if limit == 1:
            result = self.db.apk.find_one(queries)
        else:
            result = self.db.apk.find(queries, limit=limit)
        return result

    def get_apk_file(self, doc_id):
        """Get file

        Args:
            doc_id: _id in fs.file and files_id in fs.chunks

        """
        try:
            apkdata = self.fs.get(doc_id).read()

        except:
            logging.error("Download file failed !")
            raise
        finally:
            return apkdata

    def update_av_report(self, doc_id, av_result):
        """Update Anti-Virus result
        """
        if av_result:
            try:
                self.db.apk.update_one(
                    {'_id': doc_id},
                    {'$set': {'vt_scan': True, 'av_result': av_result}})
            except:
                logging.error(
                    "Update Anti-Virus result error: {}".format(doc_id))
                raise

        else:
            try:
                logging.debug("Update document without av_result.")
                self.db.apk.update_one(
                    {'_id': doc_id},
                    {'$set': {'vt_scan': True}})
            except:
                logging.error(
                    "Update Anti-Virus result error: {}".format(doc_id))
                raise
    def update_Urls_IPs_report(self, doc_id, malware_urls,malware_IPs):
        """Update Anti-Virus result
        """
        if (len(malware_urls) != 0) or (len(malware_IPs) != 0) :
            try:
                self.db.apk.update_one(
                    {'_id': doc_id},
                    # {'$set': {'url_scan': True, 'url_number': len(malware_urls),
                    # 'url_result': malware_urls, 'ip_number':len(malware_IPs),
                    # 'IPs_result':malware_IPs}})
                    {'$set': {'url_scan': True,
                    'interesting_url_number': len(malware_urls),
                    'interesting_strings_URL': malware_urls,
                    'interesting_ip_number':len(malware_IPs),
                    'interesting_strings_IP':malware_IPs}})
            except:
                logging.error(
                    "Update Anti-Urls & IPs result error: {}".format(doc_id))
                raise

        else:
            try:
                logging.debug("Update document without av_result.")
                self.db.apk.update_one(
                    {'_id': doc_id},
                    {'$set': {'url_scan': True,
                    'interesting_url_number': 0,'interesting_ip_number':0}})
            except:
                logging.error(
                    "Update Anti-Urls & IPs result error: {}".format(doc_id))
                raise

    def get_all_vt_False(self):
        result = {}
        try:
            result = self.db.apk.find({'vt_scan': False})
        except Exception,e:
            traceback.print_exc()
        return result

    def get_all_url_ip_scan_False(self):
        result = {}
        try:
            result = self.db.apk.find({'url_scan': False})
        except Exception,e:
            traceback.print_exc()
        return result
