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


project_path = os.path.dirname(os.path.dirname(__file__))
external_file_path = os.path.join(project_path, 'external')


def get_holding():
    convert = {'日期': str, '证券代码': str}
    path = os.path.join(external_file_path, '持仓.xlsx')
    data = pd.read_excel(path, converters=convert)
    data = data.dropna(how='all')
    data['日期'] = data['日期'].apply(lambda x: parse(x).date())
    group = data.groupby('日期')
    ret = {}
    for g, d in group:
        d = d[['证券代码', '市值']].copy()
        d['市值'] = d['市值'] / d['市值'].sum()
        d['证券代码'] = d['证券代码'].apply(lambda x: x+'.SH' if x.startswith('6') else x+'.SZ')
        ret.update({g: d})
    return ret
