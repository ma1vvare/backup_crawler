import time
import threading
import traceback
import virustotal

from multiprocessing import Process
from pymongo import MongoClient, HASHED
from Queue import Queue

from core.db.Mongo import DB
from core.config import api_key,api_key_IP

urls_queue = Queue()
IPs_queue = Queue()
class Url_thread(threading.Thread) :
    # def __init__(self,link, func_info, func_apk) :
    def __init__(self,api_key) :
        super(Url_thread, self).__init__()
        self.v = virustotal.VirusTotal(api_key)
        self.malware_urls_count = 0
        self.malware_urls_list = []
        # self.queue = queue
    def run(self) :
        while not urls_queue.empty():
            url = urls_queue.get()
            try:
                if self.v.get(url).positives > 0:
                    self.malware_urls_count += 1
                    self.malware_urls_list.append(url)
            except AttributeError:
                pass
            except :
                self.malware_urls_count += 1
                self.malware_urls_list.append(url)

            urls_queue.task_done()
            time.sleep(15)

class IP_thread(threading.Thread) :
    def __init__(self,api_key) :
        super(IP_thread, self).__init__()
        self.v = virustotal.VirusTotal(api_key)
        self.malware_IP_count = 0
        self.malware_IP_list = []
    def run(self) :
        while not IPs_queue.empty():
            IP = IPs_queue.get()
            try:
                if self.v.get(IP).positives > 0:
                    self.malware_IP_count += 1
                    self.malware_IP_list.append(IP)
            except AttributeError:
                pass
            except :
                self.malware_IP_count += 1
                self.malware_IP_list.append(IP)

            IPs_queue.task_done()
            time.sleep(15)

def main():
    db = DB()
    docs = db.get_all_url_ip_scan_False()
    for doc in docs:
        count_url = 0
        malware_urls = []
        url_thread_list = []
        malware_IPs = []
        IPs_thread_list = []
        #create threads
        for i in range(0,18):
            url_thread_list.append(Url_thread(api_key[i]))
        for i in range(0,5):
            IPs_thread_list.append(IP_thread(api_key_IP[i]))
        #set urls into queue
        for url in doc['interesting_strings_URL']:
            urls_queue.put(url)
        for url_thread in url_thread_list:
            url_thread.start()
        for url_thread in url_thread_list:
            url_thread.join()
        for url_thread in url_thread_list:
            count_url +=  url_thread.malware_urls_count
            for malware_url in url_thread.malware_urls_list:
                malware_urls.append(malware_url)
        count_IP = 0

        for i in doc['interesting_strings_IP']:
            IPs_queue.put('http://'+i+'/')
        for IPs_thread in IPs_thread_list:
            IPs_thread.start()
        for IPs_thread in IPs_thread_list:
            IPs_thread.join()
        for IPs_thread in IPs_thread_list:
            count_IP +=  IPs_thread.malware_IP_count
            for malware_IP in IPs_thread.malware_IP_list:
                malware_IPs.append(malware_IP)

        db.update_Urls_IPs_report(doc['_id'],malware_urls,malware_IPs)

        print ''
        print ''
        print count_url,malware_urls
        print count_IP,malware_IPs
        print ''
        print ''


if __name__ == '__main__':
    main()
