# -*- coding: utf-8 -*-
"""异常与风险预警模块：识别大额支出、借贷不平、疑似重复交易、非工作日交易。"""
import pandas as pd
from config import LARGE_AMOUNT_THRESHOLD, REPEAT_WINDOW_DAYS


def detect(df: pd.DataFrame, large_threshold: float = LARGE_AMOUNT_THRESHOLD) -> pd.DataFrame:
    """返回异常记录 DataFrame：日期, 账户, 流水号, 摘要, 涉及金额, 异常类型, 风险等级, 说明。"""
    recs = []

    # 1) 大额支出（贷方，排除内部转账类以免误报）
    big = df[(df["贷方金额"] >= large_threshold) & (df["收支类别"] != "转账")]
    for _, r in big.iterrows():
        recs.append((
            r["记账日期"].date(), r["账户"], r["流水号"], r["摘要"], round(r["贷方金额"], 2),
            "大额支出", "高",
            f"单笔支出 ¥{r['贷方金额']:,.2f} 超过预警线 ¥{large_threshold:,.2f}",
        ))

    # 2) 借贷不平（同一笔流水借方与贷方同时非零）
    dup = df[(df["借方金额"] > 0) & (df["贷方金额"] > 0)]
    for _, r in dup.iterrows():
        recs.append((
            r["记账日期"].date(), r["账户"], r["流水号"], r["摘要"],
            round(r["借方金额"] + r["贷方金额"], 2),
            "借贷不平", "高", "同一笔流水借方与贷方同时发生，疑似录入错误，需复核",
        ))

    # 3) 疑似重复交易（同对手 + 同金额 + 窗口期内）
    sub = df[(df["借方金额"] > 0) | (df["贷方金额"] > 0)].copy()
    sub["净额"] = sub["借方金额"] - sub["贷方金额"]  # 付款为负
    arr = sub.reset_index(drop=True)
    for i in range(len(arr)):
        a = arr.iloc[i]
        for j in range(i + 1, len(arr)):
            b = arr.iloc[j]
            if (a["对方户名"] == b["对方户名"]
                    and abs(a["净额"] - b["净额"]) < 0.01
                    and 0 <= (b["记账日期"] - a["记账日期"]).days <= REPEAT_WINDOW_DAYS):
                recs.append((
                    b["记账日期"].date(), b["账户"], b["流水号"], b["摘要"], abs(b["净额"]),
                    "疑似重复交易", "中",
                    f"与 {a['记账日期'].date()} 同对手({a['对方户名']})同金额 ¥{abs(b['净额']):,.2f}，疑似重复付款",
                ))

    # 4) 非工作日交易（周六/周日）
    wk = df[df["记账日期"].dt.dayofweek >= 5]
    for _, r in wk.iterrows():
        amt = round(r["借方金额"] + r["贷方金额"], 2)
        recs.append((
            r["记账日期"].date(), r["账户"], r["流水号"], r["摘要"], amt,
            "非工作日交易", "低", "交易发生在周末，关注业务合理性",
        ))

    out = pd.DataFrame(recs, columns=["日期", "账户", "流水号", "摘要", "涉及金额", "异常类型", "风险等级", "说明"])
    return out
