from termcolor import colored
from bs4 import BeautifulSoup
from pymongo import MongoClient, HASHED
from progress.bar import Bar
from core.db.Mongo import DB
from datetime import datetime
from core.parse_apk import Get_info_from_APK
import logging
import requests
import time
import traceback
import urllib
import urllib2
import sys
import pprint


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

def Download_link(app_download_link, file_name,rank,result):
    file_name = unicode(file_name).encode('utf8')

    if len(file_name) == 0:
        logging.error("No file name fetch!")
    result['name'] = file_name
    result['rank'] = rank
    result['submit_date'] = today
    file_name = '/home/peter087744982/Desktop/androidapk/'+result['pgname']+'.apk'
    #Connect to the apk download page
    res = Retry_session(app_download_link)

    if res is False:
        return False
    #get url and download through https
    download_response = Retry_session(app_download_link)

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

'''
def _download_apk(dlink,apkname):
    #dlink = "https://sirius.androidapks.com/rdata/e84da00b1ab12f4a0e4ecf9f52f57b9d/io.friendly_v1.9.84-321_Android-4.4.apk"
    hdr = {'User-Agent':'Mozilla/5.0 (Linux x86_64)\
    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'}
    # use header to change crawler to browser for crawling
    request = urllib2.Request(dlink,headers=hdr)
    try:
        page = urllib2.urlopen(request)
        apk_content = page.read()
        filepath='/home/peter087744982/Desktop/fullapk/'
        filename = filepath+apkname+'.apk'
        with open(filename,"wb") as f:
            f.write(apk_content)
            f.close()
    except urllib2.HTTPError, e:
        traceback.print_exc()

    #targetapk = "https://sirius.androidapks.com/rdata/e84da00b1ab12f4a0e4ecf9f52f57b9d/io.friendly_v1.9.84-321_Android-4.4.apk"
'''
def _get_d_link(fakeURL):
    d_link = fakeURL + '/download'
    src_exist_page = BeautifulSoup(urllib.urlopen(str(d_link)), "lxml")
    #print "src page : ",src_exist_page
    #print "dlink : ",d_link
    for url in src_exist_page.findAll('iframe',{'class':'hidden-frame'}):
        d_link = url.get('src')
    #print "src_exist_page : ",src_exist_page
    return d_link

def _get_pkg_name(fakeURL):
    pkg_exist_page = BeautifulSoup(urllib.urlopen(fakeURL), "lxml")
    pkg_name = pkg_exist_page.find("div",{"class":"apk_file_div"}).dd.string
    if type(pkg_name) =='None':
         pkg_name = pkg_exist_page.findAll("div",{"class":"post-content description"}).p.text()[1]

    #print "pkgName : ",pkg_name
    return pkg_name

def Get_apk_information(apk_info_url,result):

    #apk_info_url = "http://www.androidapksfree.com/applications/apps/" + pending_url
    res = Retry_session(apk_info_url)
    # if connect session is fail then abort the session
    if res is False:
        return False
    else:
        return True

def Get_apk_name_and_link(category_subpage,apk_category):
    result = {}
    result['vt_scan'] = False
    result['url_scan'] = False
    result['source'] = 'androidapksfree.com'
    result['title'] = apk_category


    result['category'] = []

    result['packageName']=[]
    result['apkName']=[]
    fakeURL_list = []
    pkg_name_list = []
    dlink_list = []

    #Connect to the apk page
    apk_category_link = "http://www.androidapksfree.com/applications/apps/"+ apk_category
    res = Retry_session(apk_category_link,100)

    #Bar_string = 'Processing '+ result['title']
    #bar = Bar(Bar_string, max = int(len(pkg_name_list)))

    for subpage_link in category_subpage:
        subpage = BeautifulSoup(urllib.urlopen('https://'+subpage_link),"lxml")
        subpg = subpage.findAll("div",{"class": "image-style-for-related-posts"})

        for content in xrange(0,len(subpg)):
            for url in subpg[content].findAll("a"):
                rank = 0
                try :
                    fakeURL = url.get('href')
                    fakeURL_list.append(fakeURL)
                    #print "fakeURL : ",fakeURL
                    apk_name=url.get('href')[36:][:-1]
                    print colored("downloading",'red'),apk_name,"..."
                    pkg_name = _get_pkg_name(fakeURL)
                    pkg_name_list.append(pkg_name)

                    dlink = _get_d_link(fakeURL)
                    dlink_list.append(dlink)
                    #result['category'] = apk_category
                    result['pgname'] = pkg_name
                    #result['apkName'] = apk_name

                    Get_info_status = False #initialze value
                    Get_download_status = False #initialze value

                    Get_info_status = Get_apk_information(dlink,result)
                    Get_download_status = Download_link(dlink,apk_name,rank+1,result)
                    print "Get_info_status : ",Get_info_status
                    if Get_info_status is True and Get_download_status is True :
                        try:
                            db = DB()
                            db.insert_apk(result)
                        except:
                            traceback.print_exc()
                    else:
                        pass

                except Exception,e:
                    traceback.print_exc()

def debug(result):
    for i in result:
        if i != 'apkdata':
            print i,': ',result[i],'\n'

def main():
    source = "http://www.androidapksfree.com/applications/apps"
    soup = BeautifulSoup(urllib.urlopen(source),"lxml")
    category_list = []
    category_subpage=[]
    # Save link like : www.androidapksfree.com/applications/apps/social
    for content in range(0,1):
        rawContent = soup.findAll("div",{"class": "col-8 main-content"})[content] #main content
        herf = rawContent.findAll("a",{"class": "taxonomy_button limit-line"}) # size of herf is 14
        for rawCategory in herf:
            try:
                category_list.append(rawCategory.get('href')[44:][:-1]) # grep category string
                category_subpage.append(rawCategory.get('href')[2:][:-1])
            except Exception,e:
                traceback.print_exc()
                print "download error"

    for subpage_link in category_subpage:
        #print "category_subpage : ",category_subpage
        categoryName = subpage_link[42:]
        Get_apk_name_and_link(category_subpage,categoryName)

if __name__ == '__main__':
    main()
