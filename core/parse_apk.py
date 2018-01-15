# -*- coding: UTF-8 -*-
import sys
import binascii
import hashlib
#import pydeep
import traceback

from androguard.core.bytecodes import dvm, apk
from androguard.core.analysis import analysis
from url_and_ip_check import Find_URL, Find_IP_address
from config import dangerous_permission

def Get_info_from_APK(file_name,_file_data):
    result = {}
    apk_bytecodes = apk.APK(file_name)
    apk_dvm = dvm.DalvikVMFormat(apk_bytecodes.get_dex())
    try:
        durls = apk_dvm.get_regex_strings("http(s){0,1}://.*")
        dIPs = apk_dvm.get_regex_strings("[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}")
    except:
        traceback.print_exc()
        durls = []
        dIPs = []

    size = float(sys.getsizeof(_file_data))
    result['size'] = str(round((size/1048576),1))+'MB'
    result['version'] = apk_bytecodes.get_androidversion_name()
    result['activities'] = apk_bytecodes.get_activities()
    result['app_icon_path'] = apk_bytecodes.get_app_icon()
    result['libraries'] = apk_bytecodes.get_libraries()
    result['main_activity'] = apk_bytecodes.get_main_activity()
    result['providers'] = apk_bytecodes.get_providers()
    result['receivers'] = apk_bytecodes.get_receivers()
    result['services'] = apk_bytecodes.get_services()
    result['signatures'] = unicode(apk_bytecodes.get_signatures()).encode('utf8')
    # durls = apk_dvm.get_regex_strings("http(s){0,1}://.*")
    # dIPs = apk_dvm.get_regex_strings("[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}")
    result['interesting_strings_URL'] = Find_URL(file_name) + durls
    result['interesting_strings_IP'] = Find_IP_address(file_name) + dIPs
    # unique url and ip result
    if len(result['interesting_strings_URL']) != 0:
        result['interesting_strings_URL'] = list(set(result['interesting_strings_URL']))
    if len(result['interesting_strings_IP']) != 0:
        result['interesting_strings_IP'] = list(set(result['interesting_strings_IP']))

    result['danger_permission'] = []
    result['normal_permission'] = []

    try:
        for i in apk_bytecodes.get_permissions():
            if i in dangerous_permission:
                result['danger_permission'].append(i)
            else:
                result['normal_permission'].append(i)
    except:
        result['danger_permission'] = []
        result['normal_permission'] = []

    result.update(calc_hashes(_file_data))

    return result

def calc_hashes(_file_data):
    result = {}
    data = _file_data

    crc = 0
    md5 = hashlib.md5()
    sha1 = hashlib.sha1()
    sha256 = hashlib.sha256()
    sha512 = hashlib.sha512()

    crc = binascii.crc32(data, crc)
    md5.update(data)
    sha1.update(data)
    sha256.update(data)
    sha512.update(data)

    result['md5'] = md5.hexdigest()
    result['sha1'] = sha1.hexdigest()
    result['sha256'] = sha256.hexdigest()
    result['sha512'] = sha512.hexdigest()
    result['crc32'] = "".join("%02X" % ((crc >> i) & 0xff)
                          for i in [24, 16, 8, 0])
    try:
        #result['ssdeep'] = pydeep.hash_buf(_file_data)
        result['ssdeep'] = 'not yet processing pydeep'
    except Exception as e:
        print e
        result['ssdeep'] = None

    return result

def main():
    pass
if __name__ == '__main__':
    main()
