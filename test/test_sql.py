import unittest

import analysis.sql_utils as su


class SQLUtilsTest(unittest.TestCase):
    def test_innercode_of_fund(self):
        code = su.innercode_of_fund('110011.SZ')
        self.assertEqual(code, 6999)

    def test_ratio_in_nv(self):
        data = su.ratio_in_nv(6999, '2012-09-28')
        self.assertEqual(data, 67.44)

    def test_position_level(self):
            data = su.position_level(6999, '2012-09-28')
            print(data)
