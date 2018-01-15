#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import math
import os
import time
import threading
import virustotal

from core.config import api_key
from core.db.Mongo import DB
from multiprocessing import Process


logging.basicConfig(format='%(asctime)s %(message)s',
                    dtefmt='%Y-%m-%d %I:%M:%S',
                    level=logging.DEBUG)

def spilt(doc,total_tasks,number_of_key):
    num_of_thread_tasks = int(math.floor(float(total_tasks)/number_of_key))
    doc_list = []
    thread_data_list = []
    # change class type into list
    for i in range(0,total_tasks):
        doc_list.append(doc[i])
    #spilt data into different list
    for i in range(0,(number_of_key-1) * num_of_thread_tasks,num_of_thread_tasks):
        thread_data_list.append(doc_list[i:i + num_of_thread_tasks])
    #deal remaining data
    thread_data_list.append(doc_list[(number_of_key-1) * num_of_thread_tasks: ])
    return thread_data_list

def submit_sample(v,filename):
    """Submit APK which not in VT yet.
    """
    av_result = {}

    try:
        result = v.scan(filename)

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

class Thread_mongo(threading.Thread):
    #thread class
    def __init__(self,lock,api_key,data):
        threading.Thread.__init__(self)
        self.v = virustotal.VirusTotal(api_key)
        self.db = DB()
        self.lock = lock
        self.thread_data = data

    def run(self):
        av_result = {}

        for i in self.thread_data:
            time.sleep(20)
            result = self.v.get(i['md5'])

            if result is not None:
                av_result['summary'] = {}
                av_result['summary']['total'] = result.total
                av_result['summary']['positives'] = result.positives

                for antivirus, malware in result:
                    av_result[antivirus[0]] = {}
                    av_result[antivirus[0]]['version'] = antivirus[1]
                    av_result[antivirus[0]]['result'] = malware

                self.lock.acquire()
                self.db.update_av_report(i['_id'], av_result)
                self.lock.release()
            else:
                continue

def main():
    start = time.time()
    try:
        db = DB()
    except:
        logging.error("DB error")
        raise

    number_of_key = 8
    #get all data whitch including sacn :False
    doc = db.get_all_vt_False()
    lock = threading.Lock()#thread lock
    thread_data = spilt(doc,doc.count(),number_of_key)
    # api_key =['51d63dc8b2860fbd889ea73d564e361e1ec795ce2daadb1046771272336cdadf',
    # '20f0728b711931ef2f60c8c403e83c20b600a902a12293a7d1fe566f85ca22dd',
    # '7ec895bab30a273bf6df3e211105f5f2ee45a96ddea57f53d6e4fe2b98f0c7c1',
    # 'd0fe387a075ca62d0336485641912f1b318240f6132c576fa96dbf81b242da71',
    # '29b45a9dc40737a7bc894cbacc3da603044e7f3a2651606dfca89de9accab80a',
    # '51d63dc8b2860fbd889ea73d564e361e1ec795ce2daadb1046771272336cdadf',
    # '60473b7caf108d05a5f51b9fd7544f6bb7bd0a4d966ca58d0c7b65e43611abc9',
    # '860011e025932bd8ad550e3174b75ee1c686134543a4635a4e37fef038c0fbec']
    thread_pool = []
    #deal apk with md5
    for i in range(0,number_of_key):
        p = Thread_mongo(lock,api_key[i],thread_data[i])
        thread_pool.append(p)

    for i in thread_pool:
        i.start()

    for i in thread_pool:
        i.join()
    # get the remaining data
    doc = db.get_all_vt_False()

    v = virustotal.VirusTotal('51d63dc8b2860fbd889ea73d564e361e1ec795ce2daadb1046771272336cdadf')
    #send apk data by one process
    for i in doc:
        print i['name']
        time.sleep(20)
        filename = '/tmp/'+i['pgname']+'.apk'#write down the apk file in the disk
        with open(filename, 'wb') as f:
            f.write(db.get_apk_file(i['apkdata']))

        av_result = submit_sample(v,filename)
        os.remove(filename)
        db.update_av_report(i['_id'], av_result)

    end = time.time()

    print 'total used:', end - start,' s'
if __name__ == "__main__":
    main()
