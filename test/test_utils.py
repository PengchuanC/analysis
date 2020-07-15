import unittest
import datetime

from analysis import util


class TestUtils(unittest.TestCase):

    def test_rpt_date_during(self):
        rpt = util.rpt_date_during(datetime.date(2012, 9, 28), datetime.date(2020, 6, 30))
        self.assertEqual(rpt[0], datetime.date(2012, 12, 31))
        self.assertEqual(rpt[-1], datetime.date(2019, 12, 31))
        self.assertIn(datetime.date(2017, 6, 30), rpt)


if __name__ == '__main__':
    unittest.main()
