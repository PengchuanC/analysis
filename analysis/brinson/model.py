from datetime import date
import pandas as pd

from analysis.brinson.allocate import Allocate
from analysis.brinson.config import base_index


class Model(Allocate):
    def __init__(self, pt: dict, rpt_date, index=base_index):
        super().__init__(pt, rpt_date, index)
        self.index = self.index_industry()
        self.portfolio = self.portfolio_industry()
        self.portfolio = self.portfolio[self.portfolio['i_weight'] > 0]

    @property
    def q1(self):
        """基准收益：基准中行业权重*基准中行业收益"""
        return self.index["i_weight"] * self.index["return"]

    @property
    def q2(self):
        """主动资产配置：组合中行业权重*基准中行业收益"""
        return self.portfolio["i_weight"] * self.index["return"]

    @property
    def q3(self):
        """主动股票选择：基准中行业权重*组合中行业收益"""
        return self.index["i_weight"] * self.portfolio["return"]

    @property
    def q4(self):
        """组合收益：组合中行业权重*组合中行业收益"""
        return self.portfolio["i_weight"] * self.portfolio["return"]

    def raa(self):
        """资产配置收益"""
        return self.q2 - self.q1

    def rss(self):
        """个股选择收益"""
        return self.q3 - self.q1

    def rin(self):
        """交互作用收益"""
        return self.q4 - self.q3 - self.q2 + self.q1

    def rtt(self):
        """总收益"""
        return self.q4 - self.q1

    def quick_look(self, preview=True):
        raa = self.raa()
        rss = self.rss()
        rin = self.rin()
        rto = self.rtt()
        data = pd.DataFrame(
            [self.q1, self.q2, self.q3, self.q4, raa, rss, rin, rto],
            index=["基准收益(Q1)", "主动资产配置(Q2)", "主动股票选择(Q3)", "组合收益(Q4)", "资产配置", "个股选择", "交叉作用", "超额总收益"]
        ).T
        if preview:
            print(data)
        return data


if __name__ == '__main__':
    """Brinson模块使用方式如下"""
    from analysis.brinson.external import get_holding

    _, weight = get_holding()
    dates = list(weight.keys())
    dates = sorted(dates)
    for date_ in dates:
        m = Model({"260112.OF": 1}, date_,)
        m.quick_look().to_clipboard()

