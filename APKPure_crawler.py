
# -*- coding: UTF-8 -*-
import logging
import requests
import time
import traceback
import urllib2
import sys
import pprint

from bs4 import BeautifulSoup
from pymongo import MongoClient, HASHED
from progress.bar import Bar

from core.db.Mongo import DB
from datetime import datetime
from core.parse_apk import Get_info_from_APK

today = datetime.now().strftime('%Y-%m-%d')
# Basic Configuration for logging module
logging.basicConfig(format='%(asctime)s %(message)s',
                    dtefmt='%Y-%m-%d %I:%M:%S',
                    level=logging.INFO)

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
    result['name'] = file_name
    result['rank'] = rank
    result['submit_date'] = today
    file_name = '/home/peter087744982/Desktop/apkfile/'+result['pgname']+'.apk'
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
        result.update(Get_info_from_APK(file_name,result['apkdata']))
    except:
        traceback.print_exc()
        return False

    return True

def Get_apk_information(apk_name,result):
    print "apk_name : ",apk_name
    print "result : ",result
    pending_href = apk_name.find_all(href=True)
    pending_url = pending_href[0]['href']
    print "pending_url : ",pending_url
    apk_info_url = "https://apkpure.com" + pending_url
    print "apk_info_url : ",apk_info_url
    pending_pgname = apk_info_url.split("/")
    print "pending_pgname : ",pending_pgname
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
    print "upload_date : ",info[5].text

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
        # app_name = title_set[0]['title'].replace(" ","_")
        app_name = title_set[0]['title']
        print "app_name : ",app_name
        #replace the space to underline
        app_name_set.append(app_name)
        uri = app.find_all(href=True)
        print "uri : ",uri
        url_to_download = "https://apkpure.com" + uri[0]['href'] + '/download?from=category'
        print "url_to_download : ",url_to_download
        app_urls_to_download.append(url_to_download)

    Bar_string = 'Processing '+ result['title']
    bar = Bar(Bar_string, max = int(len(app_name_set)))

    print "NameSet : "
    for item in app_name_set:
        print "item"

    for i in range(len(app_name_set)):
        Get_info_status = False
        Get_download_status = False
        try:
            Get_info_status = Get_apk_information(app_in_category[i],result)
            print "Get_info_status : ",Get_info_status
            Get_download_status = Download_link(app_urls_to_download[i],app_name_set[i],i+1,result)
            print "Get_download_status : ",Get_download_status
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

        bar.next()
    bar.finish()

def debug(result):
    for i in result:
        if i != 'apkdata':
            print i,': ',result[i],'\n'

def main():
    # get apk category
    res = requests.get("https://apkpure.com/app")
    soup = BeautifulSoup(res.text,"html.parser")
    page_index = soup.find_all('ul', {'class': 'index-category cicon'})
    pending_page_index = page_index[1].find_all('li')
    #print "pending_page_index : ",pending_page_index

    if len(sys.argv) != 3 and len(sys.argv) != 1:
        print 'please enter at most 2 number or None!'
        sys.exit(1)
    if len(sys.argv) == 3:
        begin = int(sys.argv[1])
        end = int(sys.argv[2])
    else:
        begin = 0
        end = len(pending_page_index)

    for i in range(begin,end):
        page_link = pending_page_index[i].find_all(href=True)
        print "page_link : ",page_link
        Get_apk_name_and_link(page_link[0]['href'].replace('/',''))

if __name__ == '__main__':
    main()
