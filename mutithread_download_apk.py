# -*- coding: UTF-8 -*-
import logging
import requests
import time
import threading
import traceback
import urllib2
import sys

from bs4 import BeautifulSoup
from multiprocessing import Process
from pymongo import MongoClient, HASHED
from progress.bar import Bar
from Queue import Queue

from core.db.Mongo import DB
from core.parse_apk import Get_info_from_APK
from datetime import datetime

today = datetime.now().strftime('%Y-%m-%d')
# Basic Configuration for logging module
logging.basicConfig(format='%(asctime)s %(message)s',
                    dtefmt='%Y-%m-%d %I:%M:%S',
                    level=logging.ERROR)

class Download_thread(threading.Thread) :
    # def __init__(self,link, func_info, func_apk) :
    def __init__(self,queue) :
        super(Download_thread, self).__init__()
        self.queue = queue
    def run(self) :
        while not self.queue.empty():
            # self.temp.append(self.queue.get())
            # print self.queue.get()
            cat = self.queue.get()
            print 'processing ',cat
            Get_apk_name_and_link(cat)
            self.queue.task_done()
            time.sleep(1)

def Retry_session(link,max_retry = 10):
    headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) \
    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'}

    while max_retry > 0:
        try:
            request = urllib2.Request(link,headers=headers)
            session = urllib2.urlopen(request,timeout = 150)
            return session
        except:
            time.sleep(3)
            logging.info('Reconnect %s %d',link,(10 - max_retry))
            max_retry = max_retry - 1
    return False

def Download_link(app_download_page, file_name,rank,result):
    file_name = unicode(file_name).encode('utf8')

    if len(file_name) == 0:
        logging.error("No file name fetch!")
    print "processing :",file_name
    result['name'] = file_name
    result['rank'] = rank
    result['submit_date'] = today
    file_name = '/tmp/'+result['pgname']+'.apk'
    #Connect to the apk download page
    res = Retry_session(app_download_page)

    if res is False:
        return False
    #parse the apk download link
    soup = BeautifulSoup(res,"html.parser")
    app_download_link = soup.find_all("a", attrs={"class": "ga"})
    download_link = app_download_link[0]['href']
    #get url and download through https
    download_response = Retry_session(download_link)

    if download_response != False:
        if download_response.code == 200:
            try:
                with open(file_name, 'wb') as f:
                    result['apkdata'] = download_response.read()
                    f.write(result['apkdata'])
                    f.close()
            except:
                # traceback.print_exc()
                return False
    else:
        return False

    try:
        lock.acquire()
        result.update(Get_info_from_APK(file_name,result['apkdata']))
        lock.release()
    except:
        #deal deadlock
        lock.release()
        traceback.print_exc()
        return False

    return True

def Get_apk_information(apk_name,result):
    pending_href = apk_name.find_all(href=True)
    pending_url = pending_href[0]['href']
    apk_info_url = "https://apkpure.com" + pending_url
    pending_pgname = apk_info_url.split("/")
    result['pgname'] = pending_pgname[4]
    res = Retry_session(apk_info_url)
    # if connect session is fail then abort the session
    if res is False:
        return False

    try:
        soup = BeautifulSoup(res,"html.parser")
        apk_info_url = soup.find_all('ul', {'class': 'version-ul'})
        info = apk_info_url[0].find_all('p')
    except:
        #if app page is 404
        return False

    result['upload_date'] = info[5].text

    return True

def Get_apk_name_and_link(apk_category):
    result = {}
    result['vt_scan'] = False
    result['url_scan'] = False
    result['source'] = 'apkpure.com'
    result['title'] = apk_category

    #Connect to the apk page
    apk_category_link = "https://apkpure.com/"+ apk_category
    res = Retry_session(apk_category_link,100)
    #parser the page
    soup = BeautifulSoup(res,"html.parser")
    #find all apk's informations in this page
    app_in_category = soup.find_all("div", attrs={"class": "category-template-title"})
    #store the apk's name
    app_name_set = []
    app_urls_to_download = []

    for app in app_in_category:
        title_set = app.find_all(title=True)
        app_name = title_set[0]['title'].replace(" ","_")
        #replace the space to underline
        app_name_set.append(app_name)
        uri = app.find_all(href=True)
        url_to_download = "https://apkpure.com" + uri[0]['href'] + '/download?from=category'
        app_urls_to_download.append(url_to_download)

    for i in range(len(app_name_set)):
        Get_info_status = False
        Get_download_status = False
        try:
            Get_info_status = Get_apk_information(app_in_category[i],result)
            Get_download_status = Download_link(app_urls_to_download[i],app_name_set[i],i+1,result)
        except:
            traceback.print_exc()
            pass

        if Get_info_status is True and Get_download_status is True :
            try:
                DB().insert_apk(result)

            except:
                traceback.print_exc()
        else:
            pass
            #write down which app was fail
            # with open('Fail_app.txt', 'a') as f:
            #     f.write(result['title']+' '+result['name']+'\n')
            #     f.close

def debug():
    for i in result:
        if i != 'apkdata':
            print i,': ',result[i],'\n'

def main():
    Category_queue = Queue()
    res = requests.get("https://apkpure.com/app")
    soup = BeautifulSoup(res.text,"html.parser")
    page_index = soup.find_all('ul', {'class': 'index-category cicon'})
    pending_page_index = page_index[1].find_all('li')
    thread_list = []

    if len(sys.argv) != 3 and len(sys.argv) != 1:
        print 'please enter at most 2 number or None!'
        sys.exit(1)
    elif len(sys.argv) == 3:
        begin = int(sys.argv[1])
        if int(sys.argv[2]) > len(pending_page_index):
            end = len(pending_page_index)
        else:
            end = int(sys.argv[2])
    else:
        begin = 0
        end = len(pending_page_index)
    #put category in queue
    for i in range(begin,end):
        page_link = pending_page_index[i].find_all(href=True)
        Category_queue.put(page_link[0]['href'].replace('/',''))

    #create theard and lock
    global lock
    lock = threading.Lock()
    # range is number of thread
    for i in range(0,4):
        thread = Download_thread(Category_queue)
        thread_list.append(thread)
    #start threads
    for i in thread_list:
        i.start()
    for i in thread_list:
        i.join()

if __name__ == '__main__':
    main()
