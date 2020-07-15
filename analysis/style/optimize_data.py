import os
import shelve
from datetime import date

import pandas as pd
from WindPy import w

from analysis.style.database import DataBase


base_dir = os.path.dirname(__file__)


def index_data_from_wind(index_wind_code, _date=date.today().strftime("%Y-%m-%d")):
    """从wind提取指数数据，用于风格分析的风格指数数据"""
    cache = DataBase()
    name = "style"+_date
    data = cache.load(name)
    if data is not None:
        return data
    w.start()
    data = w.wsd(index_wind_code, "close", "2017-01-01", _date, "")
    data = pd.DataFrame(data.Data, columns=data.Times, index=data.Codes).T
    cache.dump(name, data)
    return data


def fund_holding_stocks(fund_code, _date):
    """
    获取基金中股票成分
    :param fund_code: 基金代码
     :param _date: 报告期
    """
    data = w.wset("allfundhelddetail",
                  f"rptdate={_date};windcode={fund_code};field=rpt_date,stock_code,stock_name,marketvalueofstockholdings")
    data = pd.DataFrame(data.Data, index=data.Fields, columns=data.Codes).T
    return data


def fund_data_from_wind(fund_wind_code, _date):
    w.start()
    name = w.wss(fund_wind_code, "sec_name").Data[0]
    data = w.wsd(fund_wind_code, "nav", "2016-01-01", _date, "PriceAdj=B")
    data = pd.DataFrame(data.Data, columns=data.Times).T
    data.columns = name
    save_data(name[0], data)
    return data


def save_data(name, data):
    file = os.path.join(base_dir, "dataset")
    with shelve.open(file) as f:
        f[name] = data


def load_data(name):
    file = os.path.join(base_dir, "dataset")
    with shelve.open(file) as f:
        data = f[name]
    return data


def preview_data_set():
    file = os.path.join(base_dir, "dataset")
    with shelve.open(file) as f:
        print(list(f.keys()))
