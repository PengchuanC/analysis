import pandas as pd

from analysis.sql_engine import oracle, datayes, mysql


def innercode_of_fund(fund):
    """将wind基金代码转为gildata基金内部代码"""
    fund = fund[:6]
    sql = f"SELECT INNERCODE FROM JYDB.SECUMAIN s WHERE s.SECUCATEGORY = 8 AND s.SECUCODE = '{fund}'"
    data = pd.read_sql(sql, con=oracle)
    code = data.iloc[0, 0]
    return code


def ratio_in_nv(innercode, date):
    """通过innercode获取前十大持仓股合计比例，并求取中位数"""
    sql = f"SELECT SUM(RATIOINNV) AS RATIO, REPORTDATE FROM JYDB.MF_KEYSTOCKPORTFOLIO mk WHERE INNERCODE = {innercode} " \
          f"AND REPORTDATE >= TO_DATE('{date}', 'yyyy-MM_DD') GROUP BY REPORTDATE"
    data = pd.read_sql(sql, con=oracle)
    median = round(data.ratio.median()*100, 2)
    return median


def position_level(innercode, date):
    """历史股票仓位"""
    sql = f"SELECT RATIOINNV FROM JYDB.MF_ASSETALLOCATION ma WHERE INNERCODE = {innercode} AND " \
          f"REPORTDATE >= TO_DATE('{date}', 'yyyy-MM-DD') AND ASSETTYPECODE = 10020"
    data = pd.read_sql(sql, con=oracle)
    ratio = data['ratioinnv']
    median, mean, max_, min_ = ratio.median(), ratio.mean(), ratio.max(), ratio.min()
    median, mean, max_, min_ = round(median*100, 4), round(mean*100, 4), round(max_*100, 4), round(min_*100, 4)
    return median, mean, max_, min_


def daily_exposure(date):
    columns = [
        "ticker_symbol",
        "beta",
        "momentum",
        "SIZE",
        "earnyild",
        "resvol",
        "growth",
        "btop",
        "leverage",
        "liquidty",
        "sizenl",
    ]
    sql = f'select * from DATAYES."dy1d_exposure" where trade_date={date.strftime("%Y%m%d")}'
    data = pd.read_sql_query(sql, con=datayes)
    data = data[columns]
    data = data.set_index("ticker_symbol")
    data = data.sort_index()
    return data


def funds_by_category(fund):
    sql = 'select max(update_date) as start from t_ff_classify;'
    max_date = pd.read_sql(sql, con=mysql).iloc[0, 0]
    sql = f'select branch, classify from t_ff_classify where windcode_id = "{fund}" and update_date = "{max_date}"'
    data = pd.read_sql(sql, con=mysql)
    branch, classify = data.iloc[0, 0], data.iloc[0, 1]
    sql = f"select distinct(windcode_id) from t_ff_classify where branch = '{branch}' and classify = '{classify}' " \
          f"and update_date = '{max_date}'"
    data = pd.read_sql(sql, con=mysql)
    return list(data['windcode_id'])
