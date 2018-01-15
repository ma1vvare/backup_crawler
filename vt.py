#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import logging
import virustotal
from core.db.Mongo import DB

logging.basicConfig(format='%(asctime)s %(message)s',
                    dtefmt='%Y-%m-%d %I:%M:%S',
                    level=logging.DEBUG)


class vt:

    def __init__(self):

        # api_key = 'b41c1ddec8a5fc5599b19333896673174e5ffd295953c132f9220db46aecc76b'
        api_key = '51d63dc8b2860fbd889ea73d564e361e1ec795ce2daadb1046771272336cdadf'
        # api_key = '264d77db499762fa7de5cf0372c2129a288ff38e02a81e8a4a736ec3667f214'
        self.v = virustotal.VirusTotal(api_key)

    def get(self, md5):
        """Return a anti-virus result, in dictionary type.
        """
        av_result = {}

        try:
            result = self.v.get(md5)

        except virustotal.VirusTotal.ApiError:
            logging.error("Maybe exceed the number of queries.")
            raise

        if result is None:
            return None

        av_result['summary'] = {}
        av_result['summary']['total'] = result.total
        av_result['summary']['positives'] = result.positives

        for antivirus, malware in result:
            av_result[antivirus[0]] = {}
            av_result[antivirus[0]]['version'] = antivirus[1]
            av_result[antivirus[0]]['result'] = malware

        return av_result

    def submit_sample(self, filename):
        """Submit APK which not in VT yet.
        """
        av_result = {}

        try:
            result = self.v.scan(filename)
            # self.v.scan(filename)

        except virustotal.VirusTotal.EntityTooLarge:
            logging.error("Exceed the limit of file size.")
            return None

        except virustotal.VirusTotal.ApiError:
            logging.error("Maybe exceed the number of queries.")
            raise

        result.join()
        av_result['summary'] = {}
        av_result['summary']['total'] = result.total
        av_result['summary']['positives'] = result.positives

        for antivirus, malware in result:
            av_result[antivirus[0]] = {}
            av_result[antivirus[0]]['version'] = antivirus[1]
            av_result[antivirus[0]]['result'] = malware

        return av_result


def main():

    try:
        db = DB()
    except:
        logging.error("DB error")
        raise

    while(True):
        #find the first data with vt_scan is False
        doc = db.get_apk({'vt_scan': False, 'limit': 1})

        if not doc:
            logging.info("Maybe there's no document without vt_scan:true.")
            break
        av_result = vt().get(doc['md5'])

        if av_result is None:
            time.sleep(20)
            filename = '/tmp/'+doc['pgname']+'.apk'#write down the apk file in the disk
            with open(filename, 'wb') as f:
                f.write(db.get_apk_file(doc['apkdata']))

            av_result = vt().submit_sample(filename)#send the file to vt for scan
            os.remove(filename)

            logging.info("Get av_result again")
            # It will try to get report with several queries,
            # so we take some sleep here.
            time.sleep(60)

        logging.debug("av_result: {}".format(av_result))
        db.update_av_report(doc['_id'], av_result)# insert vt report into db

        time.sleep(20)


if __name__ == "__main__":
    main()
