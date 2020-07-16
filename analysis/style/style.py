import pandas as pd

from analysis.style.optmize_cvxopt import optimize_and_r
from analysis.style.optimize_data import index_data_from_wind
from analysis.brinson.external import get_nav
from analysis.style.date_util import HalfYear


def preprocess():
    index_code = {
        "小盘价值": "399377.SZ",
        "小盘成长": "399376.SZ",
        "中盘价值": "399375.SZ",
        "中盘成长": "399374.SZ",
        "大盘价值": "399373.SZ",
        "大盘成长": "399372.SZ",
        "中证全债": "H11001.CSI"
    }
    fd = get_nav()
    index_wind_code = ",".join(list(index_code.values()))
    ind = index_data_from_wind(index_wind_code)
    data = pd.merge(fd, ind, how="inner", left_index=True, right_index=True)
    data = data.pct_change().dropna(how="any")
    return data


def compute_style():
    data = preprocess()
    index = ['小盘价值', '小盘成长', '中盘价值', '中盘成长', '大盘价值', '大盘成长', '中证全债', "R2"]
    style = pd.DataFrame()
    ret = optimize_and_r(data)
    ret = pd.Series(ret, index=index)
    print(ret)
    return style.T


if __name__ == '__main__':
    d = compute_style()
    d.to_clipboard()
    print(d)
