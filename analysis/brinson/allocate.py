from datetime import date

import pandas as pd

from analysis.brinson.brinson_data import PrepareData
from analysis.brinson.config import sw_index_nickname


class Allocate(PrepareData):
    @staticmethod
    def industry_allocate(data):
        """资产在行业上的配置和收益"""
        d_weight = data.groupby("industry")["i_weight"].sum()
        data = pd.merge(data, d_weight, on="industry", how="outer")
        data["return"] = data["i_weight_x"] * data["change"]/data["i_weight_y"]
        d_return = data.groupby("industry")["return"].sum()
        data = pd.merge(d_weight, d_return, left_index=True, right_index=True, how="inner")
        nickname = {y: x for x, y in sw_index_nickname.items()}
        nickname = pd.DataFrame(pd.Series(nickname, name="nickname"))
        data = pd.merge(nickname, data, left_index=True, right_index=True, how="left")
        data = data.fillna(0)
        return data

    def index_industry(self):
        """
        指数在行业上的配置和收益
        :return:
        """
        data = self.index_stock_allocate()
        data = Allocate.industry_allocate(data)
        return data

    def portfolio_industry(self):
        """组合在行业上的配置和收益"""
        data = self.portfolio_stock_allocate()
        data = Allocate.industry_allocate(data)
        data = data.sort_values('i_weight', ascending=False)
        return data


if __name__ == '__main__':
    a = Allocate({"110011.OF": 1}, date(2019, 12, 31))
    ret = a.portfolio_industry()
    print(ret)
