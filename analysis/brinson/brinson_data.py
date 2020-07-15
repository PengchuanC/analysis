from datetime import date
import pandas as pd

from WindPy import w

from analysis.brinson.config import base_index


class PrepareData(object):
    def __init__(self, pt: dict, rpt_date, base_index=base_index):
        """组合内部股票配置，单一基金采用如下方式{'000001.OF': 1.0}"""
        w.start()
        self.pt = pt
        self.rpt_date = rpt_date
        self.bi = base_index

    def stock_allocate(self, windcode):
        """
        基金股票配置，获取单个基金在个股上的配置
        :return:
        """
        data = w.wset("allfundhelddetail",
                      f"rptdate={self.rpt_date.strftime('%Y%m%d')};windcode={windcode};field=stock_code,proportiontototalstockinvestments"
                      )
        data = pd.DataFrame(data.Data, index=["stock_code", "i_weight"], columns=data.Codes).T  # 此处获取的实际为holding
        return data

    def stock_industry(self, data):
        """个股所属行业"""
        stocks = data.index
        stocks = ",".join(stocks)
        ind = w.wss(stocks, "industry_swcode", f"tradeDate={date.today()};industryType=1")
        ind = pd.DataFrame(ind.Data, index=['industry'], columns=ind.Codes).T
        data = pd.merge(ind, data, left_index=True, right_index=True, how="inner")
        return data

    def stock_change(self, data):
        """个股涨跌幅"""
        month = self.rpt_date.month
        year = self.rpt_date.year
        if month == 6:
            start = date(year, 1, 1)
        else:
            start = date(year, 7, 1)
        stocks = data.index
        stocks = ",".join(stocks)
        pct = w.wss(stocks, "pct_chg_per", f"startDate={start};endDate={self.rpt_date}")
        pct = pd.DataFrame(pct.Data, index=['change'], columns=pct.Codes).T
        data = pd.merge(data, pct, left_index=True, right_index=True, how="inner")
        return data

    def index_stock_allocate(self):
        """
        指数在个股上的配置权重及个股所属行业和个股收益
        :return:
        """
        data = w.wset("indexconstituent", f"date={self.rpt_date};windcode={self.bi};field=wind_code,i_weight")
        data = pd.DataFrame(data.Data, index=["stock_code", "i_weight"], columns=data.Codes).T
        data["i_weight"] = data["i_weight"] / 100
        data = data.set_index("stock_code")
        data = self.stock_industry(data)
        data = self.stock_change(data)
        return data

    def portfolio_stock_allocate(self):
        """
        组合在个股上的配置权重及个股所属行业和个股收益
        :return:
        """
        data_set = pd.DataFrame()
        for key in self.pt.keys():
            data = self.stock_allocate(key)
            data["i_weight"] = data["i_weight"]*self.pt.get(key)
            data_set = data_set.append(data)
        data_set = data_set.groupby("stock_code").sum()
        # data = data_set / data_set.sum()
        data = data_set / 100
        data = self.stock_industry(data)
        data = self.stock_change(data)
        return data


if __name__ == '__main__':
    ppd = PrepareData({"110011.OF": 1.0}, date(2019, 12, 31))
    ret = ppd.portfolio_stock_allocate()
    print(ret)
