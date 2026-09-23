# -*- coding: utf-8 -*-
"""资金日报 / 月报生成模块。"""
import pandas as pd


def daily_report(df: pd.DataFrame) -> pd.DataFrame:
    """按日聚合：收入合计(借)、支出合计(贷)、笔数、净流量、当日期末余额。"""
    d = df.copy()
    d["日期"] = d["记账日期"].dt.date
    g = d.groupby("日期").agg(
        收入合计=("借方金额", "sum"),
        支出合计=("贷方金额", "sum"),
        笔数=("流水号", "count"),
    ).reset_index()
    g["净流量"] = g["收入合计"] - g["支出合计"]
    last_bal = d.sort_values("记账日期").groupby("日期")["账户余额"].last().reset_index()
    g = g.merge(last_bal, on="日期", how="left").rename(
        columns={"账户余额": "期末余额"})
    g = g.rename(columns={"收入合计": "收入合计(借)", "支出合计": "支出合计(贷)"})
    return g.sort_values("日期").reset_index(drop=True)


def monthly_report(df: pd.DataFrame) -> pd.DataFrame:
    """按月聚合：收入、支出、笔数、净流量。"""
    d = df.copy()
    d["月份"] = d["记账日期"].dt.to_period("M").astype(str)
    g = d.groupby("月份").agg(
        收入合计=("借方金额", "sum"),
        支出合计=("贷方金额", "sum"),
        笔数=("流水号", "count"),
    ).reset_index()
    g["净流量"] = g["收入合计"] - g["支出合计"]
    return g.sort_values("月份").reset_index(drop=True)
