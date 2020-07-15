"""
multiperiodmodel
~~~~~~~~~~~~~~~~
多期Brinson模型，主要是Q1~Q4的计算方式与单期略有不同
多期Brinson模型Q的计算方式计算方法（以Q1为例）：
    在单期模型中，可以计算出Q1，对于一个多期模型，通常为一年，即4个单期，
    Q1 = (1+Q1_1)(1+Q1_2)(1+Q1_3)(1+Q1_4)-1, 其中Q1_1指第一季度的Q1，
实际上利用单期模型可以得到多期模型
"""

from datetime import date

import pandas as pd

from analysis.brinson.model import Model, base_index
from analysis.brinson.config import sw_index_nickname


class MultiPeriodModel(Model):
    def __init__(self, pt: dict, rpt_date, index=base_index):
        super().__init__(pt, rpt_date, index)
        self.pt = pt
        self.rpt_date = rpt_date
        self.index = index
        self._init_model()

    def compute_multi_period(self):
        rpt = self.rpt_date
        month = rpt.month
        year = rpt.year
        if month == 6:
            ret = [date(year, 6, 30)]
        else:
            ret = [date(year, 6, 30), date(year, 12, 31)]
        return ret

    def _init_model(self):
        rpts = self.compute_multi_period()
        nickname = {y: x for x, y in sw_index_nickname.items()}
        nickname = pd.DataFrame(pd.Series(nickname, name="nickname"))
        q1, q2, q3, q4 = pd.DataFrame(nickname).copy(), pd.DataFrame(nickname).copy(), pd.DataFrame(nickname).copy(), pd.DataFrame(nickname).copy()
        for rpt in rpts:
            m = Model(self.pt, rpt, self.index)
            q1[rpt] = (m.q1/100).copy()
            q2[rpt] = (m.q2/100).copy()
            q3[rpt] = (m.q3/100).copy()
            q4[rpt] = (m.q4/100).copy()
        data = {"q1": q1.copy(), "q2": q2.copy(), "q3": q3.copy(), "q4": q4.copy()}
        for key, value in data.items():
            value = value.set_index("nickname")
            value = [(value.fillna(0)+1).T.cumprod().T.iloc[:, -1]-1]*100
            data[key] = value[value != 0]
        self.data = data

    @property
    def q1(self):
        return self.data.get("q1")

    @property
    def q2(self):
        return self.data.get("q2")

    @property
    def q3(self):
        return self.data.get("q3")

    @property
    def q4(self):
        return self.data.get("q4")   


if __name__ == '__main__':
    m = MultiPeriodModel({"110011.OF": 1}, date(2019, 12, 31))
    d = m.quick_look()
