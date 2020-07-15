"""
时间处理模块
"""
from dateutil import rrule

from datetime import datetime, timedelta, date
from typing import Tuple


class Month(object):
    @staticmethod
    def last_day_of_month(date: datetime) -> datetime:
        """
        根据输入日期获取当月最后一天
        :param date: 指定日期
        :return: 当月最后一天
        """
        year, month = date.year, date.month
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1
        first_day_of_next_month = datetime(year, month, 1)
        _last_day_of_month = first_day_of_next_month - timedelta(1)
        return _last_day_of_month

    @staticmethod
    def first_day_of_month(date: datetime) -> datetime:
        """
        根据指定日期获取当月第一天
        :param date: 指定的日期
        :return: 当月第一天
        """
        year, month = date.year, date.month
        _first_day_of_month = datetime(year, month, 1)
        return _first_day_of_month

    @staticmethod
    def first_and_last_day_of_month_in_series(date_series: list) -> Tuple[list, list]:
        """
        获取指定序列中的每月第一天和最后一天，此处的第一天或最后一天与实际日历可能会出现不同，原因在于：
        如果输入序列为['2019-01-01', '2019-01-02']，那么序列中的每月最后一天实际上是['2019-01-02']
        :param date_series: 日期序列 :list<datetime>
        :return: 序列中每月的最后一天
        """
        first_days, last_days = [date_series[0]], []

        init_date = date_series[0]
        for i in range(1, len(date_series)):
            date = date_series[i]
            if date.month != init_date.month:
                init_date = date
                first_days.append(date)
                last_days.append(date_series[i-1])
        last_days.append(date_series[-1])
        return first_days, last_days

    @staticmethod
    def monthly_report_period(date_series: list) -> list:
        """
        根据日期获取月度报告期所需要的日期，一般为区间首尾和序列中的月度最后一天，如：
        输入[datetime(2019, 5, 5), datetime(2019, 5, 6), datetime(2019, 5, 8), datetime(2019, 6, 1)]
        则返回[datetime(2019, 5, 5), datetime(2019, 5, 8), datetime(2019, 6, 1)]
        :param date_series: 时间序列
        :return: 月度报告所需日期
        """
        report_dates = [date_series[0]]
        init_day = date_series[0]

        for i in range(1, len(date_series)):
            date = date_series[i]
            if init_day.month != date.month:
                init_day = date
                report_dates.append(date_series[i-1])

        report_dates.append(date_series[-1])
        return report_dates


class HalfYear(object):
    @staticmethod
    def date_list(start, end):
        start_of_half = rrule.rrule(freq=rrule.MONTHLY, dtstart=start, until=end, bymonth=(1, 7))
        end_of_jun = rrule.rrule(freq=rrule.MONTHLY, dtstart=start, until=end, bymonth=6, bymonthday=30)
        end_of_dec = rrule.rrule(rrule.MONTHLY, dtstart=start, until=end, bymonth=12, bymonthday=31)
        dates = list(start_of_half) + list(end_of_jun) + list(end_of_dec)
        dates = sorted(dates)
        dates = [
            (dates[x*2].date(), dates[x*2+1].date())
            for x in range(0, int(len(dates)/2))
        ]
        return dates


