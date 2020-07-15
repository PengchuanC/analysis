import pandas as pd

from analysis.style.optmize_cvxopt import optimize_and_r
from analysis.style.optimize_data import index_data_from_wind
from analysis.style.fund_data import simple_data
from analysis.style.date_util import HalfYear


def preprocess(fund, date):
    index_code = {
        "小盘价值": "399377.SZ",
        "小盘成长": "399376.SZ",
        "中盘价值": "399375.SZ",
        "中盘成长": "399374.SZ",
        "大盘价值": "399373.SZ",
        "大盘成长": "399372.SZ",
        "中证全债": "H11001.CSI"
    }
    fd = simple_data(fund, date)
    index_wind_code = ",".join(list(index_code.values()))
    ind = index_data_from_wind(index_wind_code, date)
    ind.columns = index_code.keys()
    data = pd.merge(fd, ind, how="inner", left_index=True, right_index=True)
    data = data.pct_change().dropna(how="any")
    dates = data.index
    dates = HalfYear.date_list(dates[0], dates[-1])
    data = [(i[1], data[(data.index <= i[1]) & (data.index > i[0])]) for i in dates]
    return data


def compute_style(fund, date):
    data = preprocess(fund, date)
    index = ['小盘价值', '小盘成长', '中盘价值', '中盘成长', '大盘价值', '大盘成长', '中证全债', "R2"]
    style = pd.DataFrame()
    for x, y in data:
        ret = optimize_and_r(y)
        ret = pd.Series(ret, index=index, name=x)
        style[x] = ret
    return style.T


if __name__ == '__main__':
    d = compute_style("110011.OF", "2019-12-31")
    d.to_clipboard()
    print(d)
