"""
获取表格所需要素
"""
import pandas as pd
import numpy as np
from WindPy import w

from analysis.brinson.multiperiodmodel import MultiPeriodModel
from analysis.config import END
from analysis.util import format_date, format_date_ymd, rpt_date_during
from analysis import exc
from analysis import sql_utils
from analysis.style.style import compute_style

from analysis.brinson.external import get_holding


w.start()


def manager(fund):
    """当前基金经理
    返回 (基金经理, 任职日期)
    """
    data = w.wss(fund, "fund_fundmanager,fund_manager_startdate", "order=1").Data
    _manager = data[0][0]
    _serve_date = data[1][0]
    return _manager, _serve_date


def interval_return(funds, start, end, annual=False, usedf=False):
    """区间回报，可选是否年化"""
    start = format_date_ymd(start)
    end = format_date_ymd(end)
    annual_no = 1 if annual else 0
    data = w.wss(funds, "return", f"annualized={annual_no};startDate={start};endDate={end}", usedf=usedf)
    return data


def interval_adjust_nav(fund, start, end):
    """区间复权单位净值"""
    start = format_date(start)
    end = format_date(end)
    err, data = w.wsd(fund, "NAV_adj", start, end, "", usedf=True)
    if err != 0:
        raise exc.WindRuntimeError(err)
    return data['NAV_ADJ']


def scale(fund, date):
    date = format_date_ymd(date)
    err, data = w.wss(fund, "prt_netasset", f"unit=1;rptDate={date}", usedf=True)
    if err != 0:
        raise exc.WindRuntimeError(err)
    data = round(data.iloc[0, 0] / 1e8, 2)
    return data


def scale_change(fund, date):
    """
    当前基金经理任职期间基金规模最大变化
    :param fund:
    :param date: 基金经理任职起始日
    :return: 基金经理任职期间，季度最大资产净值变化，单位：亿元
    """
    start = format_date(date)
    end = format_date(END)
    err, data = w.wsd(fund, "prt_netassetchange", start, end, "unit=1;Period=Q", usedf=True)
    if err != 0:
        raise exc.WindRuntimeError(err)
    change = data['PRT_NETASSETCHANGE'].dropna()
    max_ = max(change)
    min_ = min(change)
    change_ = min_
    if abs(max_) > abs(min_):
        change_ = max_
    change_ = round(change_/1e8, 2)
    return change_


def serve_return(fund, date, annual=False):
    """
    基金经理任职期间回报
    :param date: 基金经理任职日期
    :param fund: 基金代码
    :param annual: 若annual为True则返回年化回报
    :return: 基金经理任职期间累计收益率，单位：1
    """
    data = interval_return(fund, date, END, annual)
    if (err := data.ErrorCode) != 0:
        raise exc.WindRuntimeError(err)
    _return = round(data.Data[0][0] / 100, 4)
    return _return


def rank_by_category(fund, date):
    """基金经理任职以来年化回报在同类中的排名
    思路是获取同类基金，然后wind调取同类基金区间年化收益，然后排序
    """
    funds = sql_utils.funds_by_category(fund)
    err, funds_list = w.wss(funds, "fund_initial", usedf=True)
    if err != 0:
        raise exc.WindRuntimeError(err)
    funds = list(funds_list[funds_list['FUND_INITIAL'] == '是'].index)
    if fund not in funds:
        funds.insert(0, fund)
    err, data = interval_return(funds, date, END, annual=True, usedf=True)
    if err != 0:
        raise exc.WindRuntimeError(err)
    data = data.sort_values('RETURN', ascending=False)
    data = data.dropna(how='any')
    funds = list(data.index)
    rank = funds.index(fund) + 1
    return f"{rank}/{len(funds)}"


def risk_evaluate(fund, date):
    """风险指标
    return [sharpe, sortino, vol, ir, calmar]
    """
    start = format_date_ymd(date)
    end = format_date_ymd(END)
    err, data = w.wss(
        fund,
        "risk_annusharpe,risk_annuSortino,risk_stdevyearly,risk_annuinforatio,risk_calmar",
        f"startDate={start};endDate={end};period=1;returnType=1;riskFreeRate=1;index=000001.SH",
        usedf=True
    )
    if err != 0:
        raise exc.WindRuntimeError(err)
    sharpe, sortino, vol, ir, calmar = list(round(x, 4) for x in data.loc[fund, :])
    return sharpe, sortino, vol, ir, calmar


def draw_back(fund, date):
    """基金经理任职区间，前3大回撤"""
    nav = interval_adjust_nav(fund, date, END)
    high = 0.1
    draw = []
    for x in nav:
        if x >= high:
            high = x
        pct = round((x / high - 1)*100, 2)
        draw.append(pct)
    draw = sorted(draw)
    d1, d2, d3, *_ = draw
    return d1, d2, d3


def industry_concentrate_ratio_median(fund, date):
    """
    基金行业集中度历史中位数，CR3
    :param fund:
    :param date: 基金经理任职日期
    :return:
    """
    rpts = rpt_date_during(date, END)
    ratios = []
    for rpt in rpts:
        rpt_ymd = format_date_ymd(rpt)
        ratio = 0
        for rank in (1, 2, 3):
            data = w.wss(fund, "prt_topindustryvaluetonav_sw", f"rptDate={rpt_ymd};order={rank}")
            if (data := data.Data[0][0]) is not None:
                ratio += data
        ratios.append(ratio)
    ratios = pd.Series(ratios)
    median = round(ratios.median(), 4)
    return median


def stocks_concentrate_ratio_median(fund, date):
    """
    基金持股CR10历史中位数
    :param fund:
    :param date:
    :return:
    """
    date = format_date(date)
    innercode = sql_utils.innercode_of_fund(fund)
    median = sql_utils.ratio_in_nv(innercode, date)
    return median


def stock_position(fund, date):
    """股票仓位，中位数、均值、最大值、最小值"""
    date = format_date(date)
    innercode = sql_utils.innercode_of_fund(fund)
    median, mean, max_, min_ = sql_utils.position_level(innercode, date)
    return median, mean, max_, min_


def fund_style(fund, end="2019-12-31"):
    """获取基金风格"""
    data = compute_style(fund, end)
    mean = data.mean()
    mean.name = 'mean'
    data = data.append(mean)
    ret = []
    for date, row in data.iterrows():
        row['小盘'] = row['小盘价值'] + row['小盘成长']
        row['中盘'] = row['中盘价值'] + row['中盘成长']
        row['大盘'] = row['大盘价值'] + row['大盘成长']
        row['价值'] = row['小盘价值'] + row['中盘价值'] + row['中盘价值']
        row['成长'] = row['小盘成长'] + row['中盘成长'] + row['中盘成长']
        mkt_ = [('小盘', row['小盘']), ('中盘', row['中盘']), ('大盘', row['大盘'])]
        mkt_ = sorted(mkt_, key=lambda x:x[-1], reverse=True)
        mkt = mkt_[0][0]
        style = '成长' if row['成长'] > row['价值'] else '价值'
        if date != 'mean':
            ret.append((date, mkt, style))
        else:
            mean = mkt+style
    ret = pd.DataFrame(ret, columns=['日期', '市值风格', '市场风格']).set_index('日期').T
    ret = list(ret.loc['市值风格', :]) + list(ret.loc['市场风格', :]) + [mean]
    return ret


def brinson(fund, date):
    model = MultiPeriodModel({fund: 1}, date)
    data = model.quick_look(preview=False)
    print(data.sum())
    sum_ = data.sum()
    rtt = sum_['超额总收益']
    raa = sum_['资产配置']
    rss = sum_['个股选择']
    rin = sum_['交叉作用']
    high, low = [], []
    for ind, row in data.iterrows():
        if (r := row['超额总收益']) > 0:
            high.extend([ind, round(r, 4)])
        else:
            low.extend([ind, round(r, 4)])
    return high[:6] + low[:6] + [rtt, raa, rss, rin]


def barra(rpt):
    """获取基金指定日期因子暴露度"""
    data, _ = get_holding()
    weight = data.get(rpt)
    weight.columns = ['code', 'weight']
    weight['code'] = weight['code'].apply(lambda x: x[:6])
    weight['weight'] = weight['weight'] / 100
    exposure = sql_utils.daily_exposure(rpt)
    exposure = exposure[exposure.index.isin(weight['code'])]
    exposure = exposure.sort_index()
    weight = weight.sort_values(['code'])
    ret = np.dot(weight['weight'], exposure)
    symbol = exposure.columns = [
        '贝塔因子', '动量因子', '市值因子', '盈利因子', '波动因子', '成长因子', '质量因子', '杠杆因子', '流动因子', '非线性市值因子'
    ]
    ret = pd.Series(ret, index=symbol)
    ret = round(ret, 4)
    return list(ret)


if __name__ == '__main__':
    from datetime import date
    d = barra(date(2020, 7, 14))
    print(d)