import BeautifulSoup
import logging
import re
import sys
import threading
import traceback
import urllib
# from progress.bar import Bar

from core.db.Mongo import DB
from core.parse_apk import Get_info_from_APK
from datetime import datetime
# from common.helpers import sizeof_fmt, print_header_line, print_result_line

s1 = "http://m.apk.tw/top"

today = datetime.now().strftime('%Y-%m-%d')

soup = BeautifulSoup.BeautifulSoup(urllib.urlopen(s1))


def insert_into_db(result):
    DB().insert_apk(result)


def generate_apk_info(targetapk, rank,subcategory,cat_sub,apk_name,pkg_name):

    result = {}
    result['vt_scan'] = False
    result['submit_date'] = today
    result['source'] = "mapk"
    result['title'] = cat_sub
    result['sub_title'] = subcategory
    result['name'] = unicode(apk_name).encode('utf8')
    result['rank'] = rank
    result['pgname'] = pkg_name
    # result['version'] = version
    # result['size'] = size
    result['upload_date'] = ""

    # Download APK

    result['apkdata'] = targetapk.read()
    # Calculate file hashes
    # result.update(File(result['apkdata']).result)

    # write buffer to apk file
    filename = '/tmp/' + result['pgname'] + '.apk'
    with open(filename, 'wb') as f:
        f.write(result['apkdata'])

    result.update(Get_info_from_APK(filename,result['apkdata']))
    size = float(sys.getsizeof(result['apkdata']))
    result['size'] = str(round((size/1048576),1))+'MB'

    try:
        lock.acquire()
        result.update(Get_info_from_APK(filename,result['apkdata']))
        lock.release()
        size = float(sys.getsizeof(result['apkdata']))
        result['size'] = str(round((size/1048576),1))+'MB'
    except:
        lock.release()
        traceback.print_exc()
        logging.warn(
            "androguard can't open the apk: {}".format(result['pgname']))
    debug(result)
    # print ' N ' + result['name']
    # print ' V ' + result['version']
    # print ' M ' + result['md5']
    # print ' S ' + result['size']
    return result

def debug(result):
    for i in result:
        if i != 'apkdata':
            print i,': ',result[i],'\n'

def _download_apk(dlink):
    targetapk = urllib.urlopen(dlink)
    return targetapk


def _get_d_url(durl):
    soup = BeautifulSoup.BeautifulSoup(urllib.urlopen(durl))
    dclass = soup.find("div", {"class": "download"})
    print " o " + dclass.fin d("a").get('href')
    dlink = dclass.find("a").get('href')

    return dlink


def _get_apk_name(durl):
    soup = BeautifulSoup.BeautifulSoup(urllib.urlopen(durl))
    title = soup.find("div", {"class": "detailInfo mt-5"})
    apk_name = title.find("h3").string

    return apk_name


def _get_apk_attr(durl):
    soup = BeautifulSoup.BeautifulSoup(urllib.urlopen(durl))
    ppt = soup.find("div", {"class": "property mt-10"})
    ppts = ppt.findAll("li")
    v = ppts[0].string
    s = ppts[1].string

    vparser = re.compile('(\d[\.\d]*\d)')
    sparser = re.compile('(\d[\.\d]*[MB|GB])')

    version = vparser.findall(v)[0]
    size = sparser.findall(s)[0]

    return version, size

class Download_thread(threading.Thread) :
    def __init__(self,w240,category) :
        super(Download_thread, self).__init__()
        self.w240 = w240
        self.category = category
    def run(self) :
        for ts in range(0, 2):
            # sub-category
            tab = self.w240.findAll("div", {"class": "tab"})
            spans = self.w240.findAll('span')
            # print subcategory
            subcategory = spans[ts].string
            # print subcategory

            cat_sub = self.category + "-" + subcategory
            # download list
            toplist = self.w240.findAll("div", {"class": "toplist ami"})
            rank = 1

            for url in toplist[ts].findAll("a"):
                if url.get('class') == "down":
                    try:
                        # slicing package name
                        pkg_name = url.get('href')[20:][:-1]
                        fakeurl = url.get('href')
                        dlink = _get_d_url(fakeurl)
                        targetapk = _download_apk(dlink)
                        apk_name = _get_apk_name(fakeurl)
                        print apk_name
                        # version, size = _get_apk_attr(fakeurl)
                        result = generate_apk_info(targetapk, rank,subcategory,cat_sub,
                        apk_name,pkg_name)
                        insert_into_db(result)
                        rank += 1

                    except Exception,e:
                        traceback.print_exc()
                        print "download failed"
#----------------------------------------------
def main():

    thread_list = []
    for cat in range(0,6):
        w240 = soup.findAll("div", {"class": "w240 mt-12 mr-15"})[cat]
        category = w240.find("div", {"class": "title"}).h3.string
        download_thread = Download_thread(w240,category)
        thread_list.append(download_thread)
    global lock
    lock = threading.Lock()
    for thread in thread_list:
        thread.start()

    for thread in thread_list:
        thread.join()

if __name__ == '__main__':
    main()
