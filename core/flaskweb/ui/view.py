#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
from core.common.utils import Pagination
from flask import Blueprint, render_template, request, make_response, g
from collections import defaultdict

ui = Blueprint('ui', __name__)


@ui.before_request
def check_page():
    """
    Cleans up any query parameter that is used
    to build pagination.
    """
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    logging.debug("Current Page: {}".format(page))
    g.page = page


@ui.route('/all_apks/', methods=['GET'])
def all_apks():
    from core.db.Mongo import DB

    # result = DB().get_apk({'title': 'APP_WIDGETS'})
    result = []

    g.total = list(DB().get_apk({}))
    for i in g.total[(10 * (g.page - 1)):(10 * (g.page - 1)) + 10]:
        result.append(i)

    for i in g.total[0:20]:
        logging.info(i['name'])

    return render_template('all_apks.html',
                           apks=Pagination(g.page, len(g.total), result),
                           view='ui.all_apks',
                           **request.args.to_dict())


@ui.route('/', methods=['GET'])
@ui.route('/daily_apks/', methods=['GET'])
def daily_apks():
    import datetime
    from core.db.Mongo import DB

    today = datetime.datetime.strftime(
        datetime.datetime.today(), '%Y-%m-%d')
    # db_result_gplay = list(DB().get_apk({'submit_date': today, 'source': 'googleplay'}))
    # db_result_mapk = list(DB().get_apk({'submit_date': today, 'source': 'mapk'}))
    # db_result_gplay = list(DB().get_apk({'source': 'googleplay'}))
    # db_result_mapk = list(DB().get_apk({"source": "mapk"}))

    db_result_allapk = list(DB().get_apk({'submit_date': today}))
    # db_result_mapk = list(DB().get_apk({'submit_date': today}))
    # db_result_APKPure = list(DB().get_apk({'submit_date': today}))

    # db_result_gplay = list(DB().get_apk({"$and":[{'submit_date': "2017-01-15"}, {'source': 'googleplay'}]}))
    # db_result_mapk = list(DB().get_apk({"$and":[{'submit_date': "2017-01-15"}, {'source': 'mapk'}]}))

    db_result_gplay_today = []
    db_result_mapk_today = []
    db_result_APKPure_today = []
    for apk_record in db_result_allapk:
        if apk_record['source'] == "googleplay":
            db_result_gplay_today.append(apk_record)
        elif apk_record['source'] == "mapk":
            db_result_mapk_today.append(apk_record)
        else:
            db_result_APKPure_today.append(apk_record)

    categories_result_gplay = daily_apks_by_categories(db_result_gplay_today)
    antivirus_result_gplay = daily_apks_by_antivirus(db_result_gplay_today)
    permission_result_gplay = daily_apks_by_permission(db_result_gplay_today)
    URL_result_gplay = daily_apks_by_URL(db_result_gplay_today)
    IP_result_gplay = daily_apks_by_IP(db_result_gplay_today)

    categories_result_mapk = daily_apks_by_categories(db_result_mapk_today)
    antivirus_result_mapk = daily_apks_by_antivirus(db_result_mapk_today)
    permission_result_mapk = daily_apks_by_permission(db_result_mapk_today)
    URL_result_mapk = daily_apks_by_URL(db_result_mapk_today)
    IP_result_mapk = daily_apks_by_IP(db_result_mapk_today)


    categories_result_APKPure = daily_apks_by_categories(db_result_APKPure_today)
    antivirus_result_APKPure = daily_apks_by_antivirus(db_result_APKPure_today)
    permission_result_APKPure = daily_apks_by_permission(db_result_APKPure_today)
    URL_result_APKPure = daily_apks_by_URL(db_result_APKPure_today)
    IP_result_APKPure = daily_apks_by_IP(db_result_APKPure_today)
    # get data form db
    # print db_result_gplay[0]['submit_date']
    # print categories_result_gplay
    # print categories_result_mapk




    #add data for return to html
    return render_template('daily_apks.html',
                           date=today,
                           categories_gplay = categories_result_gplay,
                           antivirus_gplay = antivirus_result_gplay,
                           permission_gplay = permission_result_gplay,
                           URL_gplay = URL_result_gplay,
                           IP_gplay = IP_result_gplay,
                           categories_mapk = categories_result_mapk,
                           antivirus_mapk = antivirus_result_mapk,
                           permission_mapk = permission_result_mapk,
                           URL_mapk = URL_result_mapk,
                           IP_mapk = IP_result_mapk,
                           categories_APKPure = categories_result_APKPure,
                           antivirus_APKPure = antivirus_result_APKPure,
                           permission_APKPure = permission_result_APKPure,
                           URL_APKPure = URL_result_APKPure,
                           IP_APKPure = IP_result_APKPure
                           )


def daily_apks_by_categories(db_result):

    result = {}

    for i in db_result:
        if i['title'] in result:
            result[i['title']][i['rank']] = i

        else:
            result[i['title']] = {}
            result[i['title']][i['rank']] = i

    # return render_template('daily_category.html',
    #                        date=today,
    #                        categories=result)

    return result


def daily_apks_by_permission(db_result):

    result = defaultdict(dict)

    for i in db_result:
        if len(i['danger_permission']) > 0:
            result[i['title']][i['rank']] = {}
            for p in i['danger_permission']:
                result[i['title']][i['rank']][p] = True

        # elif len(i['normal_permission']) > 0:
        #     result[i['title']][i['rank']] = {}
        #     for p in i['normal_permission']:
        #         result[i['title']][i['rank']][p] = False
    return result

def daily_apks_by_URL(db_result):
    result = defaultdict(dict)

    for i in db_result:
        if len(i['interesting_strings_URL']) > 0:
            result[i['title']][i['rank']] = {}
            for p in i['interesting_strings_URL']:
                result[i['title']][i['rank']][p] = True
                # print p
    return result

def daily_apks_by_IP(db_result):
    result = defaultdict(dict)

    for i in db_result:
        if len(i['interesting_strings_IP']) > 0:
            result[i['title']][i['rank']] = {}
            for p in i['interesting_strings_IP']:
                result[i['title']][i['rank']][p] = True
                # print p
    return result
def daily_apks_by_antivirus(db_result):

    result = {}

    for i in db_result:
        if 'av_result' in i:
            if i['av_result']['summary']['positives'] > 0:
                if i['av_result']['summary']['positives'] in result:
                    result[i['av_result']['summary']['positives']][
                        i['name']] = i

                else:
                    result[i['av_result']['summary']['positives']] = {}
                    result[i['av_result']['summary']['positives']][
                        i['name']] = i

    # return render_template('daily_antivirus.html',
    #                        date=today,
    #                        times=result)

    return result


@ui.route('/all_apks/download/', methods=['POST'])
@ui.route('/daily_apks/download/', methods=['POST'])
def download_apk():
    """Get document Objectid and Download APK file
    """
    from core.db.Mongo import DB
    from bson.objectid import ObjectId

    my_db = DB()
    apk_id = request.form['download_apk']

    apk_info = my_db.get_apk({'_id': ObjectId(apk_id), 'limit': 1})
    logging.debug(
        'Download {}, {}'.format(apk_info['md5'], apk_info['apkdata']))
    apkdata = my_db.get_apk_file(apk_info['apkdata'])

    response = make_response(apkdata)
    response.headers[
        'Content-Type'] = 'application/vnd.android.package-archive'
    response.headers[
        'Content-Disposition'] = 'attachment; filename='+apk_info['pgname']+".apk"

    return response
