import unittest
import datetime

from analysis.factors import *


date = datetime.date(2012, 9, 28)


class TestFactors(unittest.TestCase):

    def test_manager(self):
        _manager, _date = manager('180012.OF')
        print(_date)
        assert _manager == '焦巍'

    def test_scale_change(self):
        change = scale_change('180012.OF', '2018-12-17')
        print(change)

    def test_serve_return(self):
        _return = serve_return('180012.OF', '2018-12-27')
        print(_return)
        _return = serve_return('180012.OF', '2018-12-27', True)
        print(_return)

    def test_rank_by_category(self):
        rank = rank_by_category('110011.OF', '2012-09-28')
        self.assertEqual(rank, '10/422')

    def test_risk_evaluate(self):
        data = risk_evaluate('180012.OF', '2018-12-27')
        print(data)

    def test_draw_back(self):
        d1, d2, d3 = draw_back('110011.OF', '2012-09-28')
        print(d1, d2, d3)

    def test_industry_concentrate_ratio_medium(self):
        data = industry_concentrate_ratio_median('110011.OF', date)
        self.assertEqual(data, 64.9422)

    def test_stocks_concentrate_ratio_median(self):
        median = stocks_concentrate_ratio_median('110011.OF', '2012-09-28')
        self.assertEqual(median, 67.44)

    def test_stocks_position(self):
        median = stock_position('110011.OF', '2012-09-28')
        self.assertIn(87.9276, median)

    def test_fund_style(self):
        ret = fund_style('110011.OF')
        print(ret)

    def test_brinson(self):
        ret = brinson('110011.OF', datetime.date(2019, 12, 31))
        print(ret)

    def test_barra(self):
        ret = barra('110011.OF', datetime.date(2020, 5, 29))
        print(ret)


if __name__ == '__main__':
    unittest.main()
