import datetime

from dateutil.parser import parse


def format_date(date):
    if isinstance(date, datetime.date) or isinstance(date, datetime.datetime):
        return date.strftime('%Y-%m-%d')
    date = parse(date).strftime('%Y-%m-%d')
    return date


def format_date_ymd(date):
    if isinstance(date, datetime.date) or isinstance(date, datetime.datetime):
        return date.strftime('%Y%m%d')
    date = parse(date).strftime('%Y%m%d')
    return date


def rpt_date_during(start: datetime.date, end: datetime.date):
    """
    获取区间的半年报和年报日期
    :param start:
    :param end:
    :return:
    """
    start_year = start.year
    start_month = start.month
    end_year = end.year
    end_month = end.month
    rpt = []
    for year in range(start_year, end_year+1):
        for month in (6, 12):
            day = 30 if month == 6 else 31
            date = datetime.date(year, month, day)
            rpt.append(date)
    if start_month > 6:
        rpt = rpt[1:]
    if end_month <= 6:
        rpt = rpt[:-2]
    return rpt
