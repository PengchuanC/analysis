"""
external
~~~~~~~~~~~~~~~~~~~~~~~
@author: chuanchao.peng
@date: 2020-07-15
@desc: 读取外部文件
"""
import os

import pandas as pd

from dateutil.parser import parse
from functools import lru_cache


project_path = os.path.dirname(os.path.dirname(__file__))
external_file_path = os.path.join(project_path, 'external')


@lru_cache(None)
def get_holding():
    data = get_data()
    data['flag'] = data['证券代码'].apply(lambda x: 1 if '.SZ' in x or '.SH' in x else 2)
    group = data.groupby('日期')
    ret = {}
    w = {}
    for g, d in group:
        d = d[['证券代码', '市值', 'flag']].copy()
        weight = d[d['flag'] == 1]['市值'].sum() / d['市值'].sum()
        d = d[d['flag'] == 1]
        d = d[['证券代码', '市值']].copy()
        d['市值'] = d['市值'] / d['市值'].sum()
        ret.update({g: d})
        w.update({g: weight})
    return ret, w


@lru_cache(None)
def get_data():
    convert = {'日期': str, '证券代码': str}
    path = os.path.join(external_file_path, '持仓.xlsx')
    data = pd.read_excel(path, converters=convert)
    data = data.fillna(method='ffill')
    data = data.dropna(how='all')
    data['日期'] = data['日期'].apply(lambda x: parse(x).date())
    return data


def get_nav():
    data = get_data()
    nav = data.drop_duplicates('日期').copy()
    # nav['日期'] = nav['日期'].apply(lambda x: x.strftime("%Y-%m-%d"))
    nav = nav.set_index('日期')
    nav = nav[['单位净值']]
    return nav

nav = get_nav()
nav.to_clipboard()