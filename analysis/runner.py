from datetime import date
from analysis.factors import *


def run(fund, rpt):
    _, start = manager(fund)
    ret = [
        manager(fund)[0], scale(fund, rpt), scale_change(fund, start), serve_return(fund, start),
        serve_return(fund, start, True), rank_by_category(fund, start)
    ]
    ret += risk_evaluate(fund, start)
    ret += draw_back(fund, start)
    ret += [industry_concentrate_ratio_median(fund, start), stocks_concentrate_ratio_median(fund, start)]
    ret += stock_position(fund, start)
    ret += fund_style(fund)
    ret += brinson(fund, rpt)
    ret += barra(fund, rpt)
    columns = [
        '基金经理', '任期规模(亿)', '任期规模最大变化(亿)', '累计收益率(任期回报)', '年化收益率(任期回报)', '同类排名(任期回报)',
        '夏普(任期业绩指标(年化))', '索提诺(任期业绩指标(年化))', '波动率(任期业绩指标(年化))', '信息比率(任期业绩指标(年化))',
        '收益回撤比(任期业绩指标(年化))', '最大回撤(任期回撤)', '第二大回撤(任期回撤)', '第三大回撤(任期回撤)', '行业集中度中位数',
        '个股集中度中位数', '任期仓位中位数', '长期仓位水平', '最低仓位水平', '最高仓位水平', '市值风格201706', '市值风格201712',
        '市值风格201806', '市值风格201812', '市值风格201906', '市值风格201912', '市场风格201706', '市场风格201712',
        '市场风格201806', '市场风格201812', '市场风格201906', '市场风格201912', '总体风格', '擅长行业（申万一级）仓位高且拿到超额回报',
        '超额收益', '擅长行业（申万一级）仓位高且拿到超额回报', '超额收益', '擅长行业（申万一级）仓位高且拿到超额回报', '超额收益',
        '不擅长行业（申万一级）仓位高，未获得超额回报', '超额收益', '不擅长行业（申万一级）仓位高，未获得超额回报', '超额收益',
        '不擅长行业（申万一级）仓位高，未获得超额回报', '超额收益', '超额总收益', '资产配置收益', '个股选择收益', '交互作用收益',
        '贝塔因子', '动量因子', '市值因子', '盈利因子', '波动因子', '成长因子', '质量因子', '杠杆因子', '流动因子', '非线性市值因子'
    ]
    ret = pd.Series(ret, index=columns)
    ret.T.to_excel(f'{fund}.xlsx')
    print(ret)


if __name__ == '__main__':
    run('007345.OF', date(2019, 12, 31))
