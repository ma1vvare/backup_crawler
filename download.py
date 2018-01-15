#!/usr/bin/python

# Do not remove
# GOOGLE_LOGIN = GOOGLE_PASSWORD = AUTH_TOKEN = None

import argparse
import logging
import traceback
import sys

from core.gplayapi.googleplay import GooglePlayAPI
from core.db.Mongo import DB
from core.config import *
from core.parse_apk import Get_info_from_APK
from common.helpers import sizeof_fmt
from datetime import datetime
from progress.bar import Bar
# Basic Configuration for logging module
logging.basicConfig(format='%(asctime)s %(message)s',
                    dtefmt='%Y-%m-%d %I:%M:%S',
                    level=logging.ERROR)

# Arguments handling
# parser = argparse.ArgumentParser(
#     description='List subcategories and apps within them.')
# parser.add_argument("nb_results", nargs=1, type=str, default=None,
#                     help='You can get a list of all subcategories available, by supplying a valid category')
# parser.add_argument("--offset", nargs=1, type=int, default=None,
#                     help='You can get a list of all subcategories available, by supplying a valid category')
# args = parser.parse_args()

category = [
            "ANDROID_WEAR",
            "ART_AND_DESIGN",
            "AUTO_AND_VEHICLES",
            "BEAUTY",
            "BOOKS_AND_REFERENCE",
            "BUSINESS",
            "COMICS",
            "COMMUNICATION",
            "DATING",
            "EDUCATION",
            "ENTERTAINMENT",
            "EVENTS",
            "FINANCE",
            "FOOD_AND_DRINK",
            "GAME",
            "HEALTH_AND_FITNESS",
            "HOUSE_AND_HOME",
            "LIBRARIES_AND_DEMO",
            "LIFESTYLE",
            "MAPS_AND_NAVIGATION",
            "MEDICAL",
            "MUSIC_AND_AUDIO",
            "NEWS_AND_MAGAZINES",
            "PARENTING",
            "PERSONALIZATION",
            "PHOTOGRAPHY",
            "PRODUCTIVITY",
            "SHOPPING",
            "SOCIAL",
            "SPORTS",
            "TOOLS",
            "TRAVEL_AND_LOCAL",
            "VIDEO_PLAYERS",
            "WEATHER"
        ]

# ctr = "apps_topselling_free"
# nb_results = args.nb_results[0]
#
# if args.offset:
#     logging.debug("there's offset : {}".format(args.offset))
#     offset = args.offset[0]
# else:
#     offset = None
#
# # Using GooglePlayAPI
# api = GooglePlayAPI(ANDROID_ID)
# api.login(GOOGLE_LOGIN, GOOGLE_PASSWORD, AUTH_TOKEN)

# Download apk from each category
def main():
    parser = argparse.ArgumentParser(
        description='List subcategories and apps within them.')
    parser.add_argument("nb_results", nargs=1, type=str, default=None,
                        help='You can get a list of all subcategories available, by supplying a valid category')
    parser.add_argument("--offset", nargs=1, type=int, default=None,
                        help='You can get a list of all subcategories available, by supplying a valid category')
    args = parser.parse_args()

    ctr = "apps_topselling_free"
    nb_results = args.nb_results[0]

    if args.offset:
        logging.debug("there's offset : {}".format(args.offset))
        offset = args.offset[0]
    else:
        offset = None

    # Using GooglePlayAPI
    api = GooglePlayAPI(ANDROID_ID)
    api.login(GOOGLE_LOGIN, GOOGLE_PASSWORD, AUTH_TOKEN)

    bar = Bar('Downloading: ', max = 34*int(nb_results))
    for cat in category:
        try:
            message = api.list(cat, ctr, nb_results, offset)
        except:
            logging.error(
                "Error: HTTP 500 - one of the provided parameters is invalid")
            raise

        # Get info, download apk, calculate file hashes, insert to mongodb
        # today = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        today = datetime.now().strftime('%Y-%m-%d')
        rank = 1

        for i in message.doc[0].child:
            result = {'permission': {'p': 'v'}}
            result['vt_scan'] = False
            result['submit_date'] = today
            result['source'] = 'googleplay'
            result['title'] = cat
            result['sub_title'] = ctr
            result['name'] = unicode(i.title).encode('utf8')
            result['rank'] = rank
            result['pgname'] = i.details.appDetails.packageName
            # result['version'] = i.details.appDetails.versionCode
            # result['size'] = sizeof_fmt(i.details.appDetails.installationSize)
            result['upload_date'] = datetime.strptime(unicode(i.details.appDetails.uploadDate).encode('utf8'),
                                                      locale_timestring[LANG]).strftime('%Y-%m-%d')
            # Download APK
            result['apkdata'] = api.download(i.details.appDetails.packageName,
                                             i.details.appDetails.versionCode,
                                             i.offer[0].offerType)
            # Calculate file hashes
            # result.update(File(result['apkdata']).result)

            # update rank
            rank += 1

            # write buffer to apk file
            filename = '/tmp/' + result['pgname'] + '.apk'

            with open(filename, 'wb') as f:
                f.write(result['apkdata'])
            # retrive permission from apk file
            try:
                result.update(Get_info_from_APK(filename,result['apkdata']))
                size = float(sys.getsizeof(result['apkdata']))
                result['size'] = str(round((size/1048576),1))+'MB'
                print result['sha512']
                raw_input('stop')
                # result['interesting_strings_URL']  = Find_URL(filename)
                # result['interesting_strings_IP']  = Find_IP_address(filename)

            except Exception,e:
                logging.error("DB insert error: {}".format(result['pgname']))
                traceback.print_exc()

            # result['danger_permission'], result['normal_permission'] = APK_permission(filename)

            # Insert apk into mongodb
            try:
                DB().insert_apk(result)
                bar.next()
            except KeyError:
                logging.warn(
                    "Maybe the apk already exists: {}".format(result['pgname']))
                # continue
                raise
            except:
                logging.error("DB insert error: {}".format(result['pgname']))
                raise
    bar.finish()
if __name__ == '__main__':
    main()
