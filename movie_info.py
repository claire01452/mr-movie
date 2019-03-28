#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib.request
import datetime
import json
import pandas
import csv
import os

# http://piaofang.maoyan.com/dashboard
def getboxinfo(date):
    req = \
        urllib.request.Request('https://box.maoyan.com/promovie/api/box/second.json?beginDate=%s'
                                % date.strftime('%Y%m%d'))
    try:
        f = urllib.request.urlopen(req, timeout=10)
    except Exception:
        print('fail to get box info for date: %s. skip...' % date.strftime('%Y-%m-%d'))
        return []

    res = json.loads(f.read())
    data = res['data']['list']

    data_trim = []
    for r in data:
        r_trim = {
            'date': date.strftime('%Y-%m-%d'),
            'movieId': r['movieId'],
            'movieName': r['movieName'],
            'boxInfo': r['boxInfo'],
            'splitBoxInfo': r['splitBoxInfo'],
            'sumBoxInfo': r['sumBoxInfo'],
            'splitSumBoxInfo': r['splitSumBoxInfo'],
            }
        data_trim.append(r_trim)
    return data_trim

# https://piaofang.maoyan.com/movie/1206605/promotion/weibo
def getweibo(m_id, start_d, end_d):
    req = \
        urllib.request.Request('https://piaofang.maoyan.com/movie/%d/promption-ajax?method=change&type=weibo&startDate=%s&endDate=%s'
                                % (m_id, start_d, end_d))
    req.add_header('User-Agent',
                   'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36'
                   )
    try:
        f = urllib.request.urlopen(req, timeout=10)
    except Exception:
        print('fail to get weibo for movie: %d. skip...' % m_id)
        return []

    res = json.loads(f.read())
    data = res['data']

    data_trim = []
    for r in data:
        r_trim = {
            'movieId': m_id,
            'date': r.get('date',''),
            'weiboCommentNum': r.get('commentNum',''),
            'weiboCount': r.get('count',''),
            'weiboForwardNum': r.get('forwardNum',''),
            'weiboLikeNum': r.get('likeNum',''),
            }
        data_trim.append(r_trim)
    return data_trim

box_res = []
curr_date = datetime.date(2019, 3, 24)
while curr_date >= datetime.date(2018, 1, 1):
    box_res += getboxinfo(curr_date)
    curr_date -= datetime.timedelta(days=1)

box_res_df = pandas.DataFrame(box_res)

weibo_res = []
m_ids = box_res_df['movieId'].unique()
for m_id in m_ids:
    weibo_res += getweibo(m_id, '2018-01-01', '2019-03-24')

weibo_res_df = pandas.DataFrame(weibo_res)

merge_res_df = pandas.merge(box_res_df, weibo_res_df, on=('movieId', 'date'), how='outer')

csv_file = '%s\\movie_info.csv' \
    % os.path.dirname(os.path.abspath(__file__))
merge_res_df.to_csv(csv_file, encoding='utf-8-sig')
