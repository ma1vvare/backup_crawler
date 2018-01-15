# -*- coding: utf8 -*-
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import subprocess
import re
# file_name = "virus.apk"

def Find_URL(file_name):
    URL_list = []#store URL set
    cmd = r'strings -a %s | grep -i "http"' %file_name
    pattern = r'http.{0,1}://.*'
    #use cmd to find the raw which including "http"
    try:
        pending_string = subprocess.check_output(cmd,shell=True)
        #received the result from the cmd
    except subprocess.CalledProcessError as e:
        return URL_list #return empty list
    # put the string into list
    targe_string = ''
    result = ''

    for i in pending_string:

        if i == ' ' or i == '\n' or i == '<' or i == '(' \
            or i == ',' or i == '>' or i == '#' or i == '\'':
            match = re.search(pattern,targe_string)

            if match:
                result = match.group()
                result = result.replace('"','')
                URL_list.append(result)
                result = ''
            targe_string = ''
        else:
            targe_string += i
    URL_list = list(set(URL_list))
    return URL_list

def Find_IP_address(file_name):
    cmd = r'strings -a %s | grep "[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}\.[0-9]\{1,3\}"' %file_name
    pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
    IP_list = []
    try:
        pending_string = subprocess.check_output(cmd,shell=True)
    except subprocess.CalledProcessError as e:
        return IP_list

    targe_string = ''

    for i in pending_string:

        if i == ' ' or i == '\n':
            #filter IP
            match = re.search(pattern,targe_string)
            if match :
                IP_list.append(match.group())
            targe_string = ''
        else:
            targe_string += i

    IP_list = list(set(IP_list))
    return IP_list

def main():
    pass
if __name__ == '__main__':
    main()
