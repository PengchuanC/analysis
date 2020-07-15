from datetime import date
import pandas as pd

from WindPy import w

from analysis.style.database import DataBase


def fund_nav_data(fund_code, start="2019-01-01", end=date.today().strftime("%Y-%m-%d")):
    """获取单只基金净值数据"""
    w.start()
    data = w.wsd(fund_code, "NAV_adj", start, end, "")
    if data.ErrorCode != 0:
        raise BaseException("Wind接口出错")
    data = pd.DataFrame(data.Data, columns=data.Times, index=data.Codes).T
    return data


def simple_data(fund_code, end=date.today().strftime("%Y-%m-%d")):
    """
    从本地缓存中读取数据，若日期不匹配，则追加数据
    :param fund_code:基金代码
    :param end:
    :return:
    """
    db = DataBase()
    data = db.load(fund_code)
    if data is not None:
        last_day = data.index[-1].strftime("%Y-%m-%d")
        if last_day < end:
            data_extend = fund_nav_data(fund_code, last_day, end).iloc[1:, :]
            data = data.append(data_extend)
            db.update(fund_code, data)
    else:
        last_day = "2017-01-01"
        data = fund_nav_data(fund_code, last_day, end)
        db.dump(fund_code, data)
    index = len([x for x in data.index if x.strftime("%Y-%m-%d") <= end])
    data = data.iloc[: index+1, :]
    return data


if __name__ == '__main__':
    db = DataBase()
    ret = simple_data("110011.OF", "2019-10-31")
    print(ret)
