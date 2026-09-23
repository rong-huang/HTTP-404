# -*- coding: utf-8 -*-
"""生成脱敏模拟银行流水（多账户 + 异常样本），仅供项目演示。
所有企业名称、户名、金额均为虚构，不涉及任何真实主体或个人隐私。
运行：python generate_sample_data.py
"""
import random
import datetime
import pandas as pd
from config import DATA_DIR

random.seed(20260923)


def _d(y, m, day):
    """原始日期字符串，用于故意埋入的异常样本（保留其周末属性）。"""
    return f"{y}/{m:02d}/{day:02d}"


def _next_workday(y, m, day):
    """若给定日期落在周末，顺延到下一个周一，避免正常业务日期误触非工作日预警。"""
    dt = datetime.date(y, m, day)
    while dt.weekday() >= 5:  # 5=周六 6=周日
        dt += datetime.timedelta(days=1)
    return dt


def _dd(y, m, day):
    """常规业务日期：自动避开周末。"""
    dt = _next_workday(y, m, day)
    return f"{dt.year}/{dt.month:02d}/{dt.day:02d}"


def make_icbc():
    """工商银行基本户：数值型金额（无符号），列名 借方发生额/贷方发生额。"""
    rows, bal, seq = [], 500000.0, 1
    for m in range(1, 7):
        amt = 186000.0
        bal -= amt
        rows.append([_dd(2026, m, 10), f"ICBC{seq:04d}", "代发工资-员工薪酬", 0, amt, round(bal, 2), "员工工资代发专户"]); seq += 1
        tax = 42000.0
        bal -= tax
        rows.append([_dd(2026, m, 15), f"ICBC{seq:04d}", "增值税及附加税费申报缴款", 0, tax, round(bal, 2), "国家税务总局"]); seq += 1
        oa = random.choice([2300, 1800, 3200, 2600])
        bal -= oa
        rows.append([_dd(2026, m, 18), f"ICBC{seq:04d}", "办公用品采购-文具耗材", 0, oa, round(bal, 2), "晨光文具批发部"]); seq += 1
        fee = 50.0
        bal -= fee
        rows.append([_dd(2026, m, 20), f"ICBC{seq:04d}", "账户管理费及网银手续费", 0, fee, round(bal, 2), "中国工商银行"]); seq += 1
        rev = random.choice([150000, 220000, 180000, 260000])
        bal += rev
        rows.append([_dd(2026, m, 25), f"ICBC{seq:04d}", "客户回款-货款", rev, 0, round(bal, 2), "江西华翔制造有限公司"]); seq += 1
        tr = 80000.0
        bal -= tr
        rows.append([_dd(2026, m, 28), f"ICBC{seq:04d}", "内部转账-调拨至招行一般户", 0, tr, round(bal, 2), "招商银行一般户"]); seq += 1
    # 异常：借贷不平（脏数据，保持原日期）
    bal -= 1000
    rows.append([_d(2026, 3, 12), "ICBC0099", "系统录入异常-借货同记测试", 1000, 2000, round(bal, 2), "测试供应商"])
    # 异常：周末交易（2026-04-04 为周六，故意保留以触发非工作日预警）
    bal -= 5600
    rows.append([_d(2026, 4, 4), "ICBC0100", "周末紧急采购-设备备件", 0, 5600, round(bal, 2), "五金机电经营部"])
    return rows


def make_cmb():
    """招商银行一般户：金额带千分位逗号，列名 支出/收入。"""
    rows, bal, seq = [], 200000.0, 1
    for m in range(1, 7):
        tr = random.choice([6800, 9200, 5400, 7600])
        bal -= tr
        rows.append([_dd(2026, m, 8), f"CMB{seq:04d}", "差旅费-机票住宿高铁", f"{tr:,.2f}", "0.00", f"{bal:,.2f}", "携程商旅"]); seq += 1
        ent = random.choice([3200, 4800, 2600])
        bal -= ent
        rows.append([_dd(2026, m, 14), f"CMB{seq:04d}", "业务招待费-客户餐饮", f"{ent:,.2f}", "0.00", f"{bal:,.2f}", "某餐饮有限公司"]); seq += 1
        adv = random.choice([30000, 45000, 25000])
        bal -= adv
        rows.append([_dd(2026, m, 22), f"CMB{seq:04d}", "广告推广费-线上投放", f"{adv:,.2f}", "0.00", f"{bal:,.2f}", "某信息科技有限公司"]); seq += 1
        pur = random.choice([12000, 18000, 9500])
        bal -= pur
        rows.append([_dd(2026, m, 26), f"CMB{seq:04d}", "材料采购-供应商货款", f"{pur:,.2f}", "0.00", f"{bal:,.2f}", "华东物资供应站"]); seq += 1
        intr = 120.0
        bal += intr
        rows.append([_dd(2026, m, 21), f"CMB{seq:04d}", "存款结息-利息收入", "0.00", f"{intr:,.2f}", f"{bal:,.2f}", "招商银行"]); seq += 1
    # 异常：重复交易（同对手同金额，间隔2天）
    bal -= 8000
    rows.append([_d(2026, 2, 10), "CMB0201", "办公用品采购-得力", "8,000.00", "0.00", f"{bal:,.2f}", "得力办公直供"])
    bal -= 8000
    rows.append([_d(2026, 2, 12), "CMB0202", "办公用品采购-得力", "8,000.00", "0.00", f"{bal:,.2f}", "得力办公直供"])
    # 异常：周末交易（2026-01-10 为周六）
    bal -= 4800
    rows.append([_d(2026, 1, 10), "CMB0203", "周末业务招待-客户宴请", "4,800.00", "0.00", f"{bal:,.2f}", "某餐饮有限公司"])
    return rows


def make_ccb():
    """建设银行专户：金额带 ¥ 与千分位，列名 付方金额/收方金额。"""
    rows, bal, seq = [], 300000.0, 1
    for m in range(1, 7):
        rent = 30000.0
        bal -= rent
        rows.append([_dd(2026, m, 1), f"CCB{seq:04d}", "办公室房租-租金", f"¥{rent:,.2f}", "¥0.00", f"¥{bal:,.2f}", "某商业地产有限公司"]); seq += 1
        util = random.choice([4200, 3800, 5100, 4600])
        bal -= util
        rows.append([_dd(2026, m, 5), f"CCB{seq:04d}", "水电费-物业费", f"¥{util:,.2f}", "¥0.00", f"¥{bal:,.2f}", "供电供水公司"]); seq += 1
        rep = random.choice([1500, 2200, 900])
        bal -= rep
        rows.append([_dd(2026, m, 16), f"CCB{seq:04d}", "设备维修维保费", f"¥{rep:,.2f}", "¥0.00", f"¥{bal:,.2f}", "某机电维修部"]); seq += 1
        tr = 80000.0
        bal += tr
        rows.append([_dd(2026, m, 28), f"CCB{seq:04d}", "内部转账-工行调入", "¥0.00", f"¥{tr:,.2f}", f"¥{bal:,.2f}", "工商银行基本户"]); seq += 1
    # 异常：大额设备采购（触发大额预警）
    bal -= 120000
    rows.append([_d(2026, 5, 18), "CCB0099", "生产设备采购-大额付款", f"¥{120000:,.2f}", "¥0.00", f"¥{bal:,.2f}", "某装备制造有限公司"])
    # 政府补助（收入，常规业务走工作日）
    bal += 50000
    rows.append([_dd(2026, 6, 20), "CCB0100", "政府补助-稳岗补贴", "¥0.00", f"¥{50000:,.2f}", f"¥{bal:,.2f}", "财政局社保中心"])
    return rows


def main():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    icbc = pd.DataFrame(make_icbc(), columns=["日期", "流水号", "摘要", "借方发生额", "贷方发生额", "余额", "对方户名"])
    cmb = pd.DataFrame(make_cmb(), columns=["交易日期", "凭证", "摘要说明", "支出", "收入", "账户余额", "交易对手"])
    ccb = pd.DataFrame(make_ccb(), columns=["记账日", "序号", "业务摘要", "付方金额", "收方金额", "期末余额", "对方名称"])
    icbc.to_csv(DATA_DIR / "工商银行_2026.csv", index=False, encoding="utf-8-sig")
    cmb.to_csv(DATA_DIR / "招商银行_2026.csv", index=False, encoding="utf-8-sig")
    ccb.to_csv(DATA_DIR / "建设银行_2026.csv", index=False, encoding="utf-8-sig")
    print("模拟流水已生成 ->", DATA_DIR)


if __name__ == "__main__":
    main()
