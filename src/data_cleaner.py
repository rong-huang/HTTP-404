# -*- coding: utf-8 -*-
"""银行流水清洗模块：把多家银行、多种格式的流水统一为标准台账字段。

演示价值：现实中的银行流水 CSV 列名、日期、金额格式各不相同，
本模块负责把它们规范成统一的「标准资金台账」输入，是自动化流水线的第一关。
"""
import re
import pandas as pd
from config import DATA_DIR, ACCOUNTS

# 各银行账户「原始列名 -> 标准列名」映射（体现多源数据清洗）
COLUMN_MAP = {
    "工商银行": {
        "日期": "记账日期", "流水号": "流水号", "摘要": "摘要",
        "借方发生额": "借方金额", "贷方发生额": "贷方金额",
        "余额": "账户余额", "对方户名": "对方户名",
    },
    "招商银行": {
        "交易日期": "记账日期", "凭证": "流水号", "摘要说明": "摘要",
        "支出": "贷方金额", "收入": "借方金额",
        "账户余额": "账户余额", "交易对手": "对方户名",
    },
    "建设银行": {
        "记账日": "记账日期", "序号": "流水号", "业务摘要": "摘要",
        "付方金额": "贷方金额", "收方金额": "借方金额",
        "期末余额": "账户余额", "对方名称": "对方户名",
    },
}

# 标准列（清洗后保留）
STD_COLS = ["记账日期", "流水号", "摘要", "借方金额", "贷方金额", "账户余额", "对方户名"]


def _parse_date(s):
    """兼容 2026/01/05、2026-01-05、2026年1月5日 等多种格式"""
    s = str(s).strip()
    m = re.search(r"(\d{4})[年/\-](\d{1,2})[月/\-](\d{1,2})", s)
    if m:
        try:
            return pd.Timestamp(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            return pd.NaT
    return pd.NaT


def _parse_amount(s):
    """兼容 '1,234.50'、'¥1,234.50'、'1234.5'、空/'-' 等写法"""
    if pd.isna(s):
        return 0.0
    s = str(s).replace(",", "").replace("¥", "").replace("元", "").strip()
    if s in ("", "-", "—", "nan", "None"):
        return 0.0
    try:
        return float(s)
    except ValueError:
        return 0.0


def load_all_flows():
    """读取全部模拟银行流水，清洗并合并为统一 DataFrame。"""
    frames = []
    file_map = {
        "工商银行": "工商银行_2026.csv",
        "招商银行": "招商银行_2026.csv",
        "建设银行": "建设银行_2026.csv",
    }
    for bank, fname in file_map.items():
        path = DATA_DIR / fname
        if not path.exists():
            continue
        raw = pd.read_csv(path, dtype=str)
        raw = raw.rename(columns=COLUMN_MAP[bank])
        raw = raw[[c for c in STD_COLS if c in raw.columns]]
        # 缺失列补零
        for c in STD_COLS:
            if c not in raw:
                raw[c] = 0.0 if c in ("借方金额", "贷方金额", "账户余额") else ""
        raw["记账日期"] = raw["记账日期"].apply(_parse_date)
        for c in ["借方金额", "贷方金额", "账户余额"]:
            raw[c] = raw[c].apply(_parse_amount)
        raw["摘要"] = raw["摘要"].astype(str).str.strip()
        raw["对方户名"] = raw["对方户名"].astype(str).str.strip()
        raw["账户"] = ACCOUNTS.get(bank, bank)
        raw["账户代码"] = bank
        raw = raw.dropna(subset=["记账日期"])
        frames.append(raw)

    if not frames:
        raise FileNotFoundError("未找到模拟银行流水，请先运行 generate_sample_data.py")
    df = pd.concat(frames, ignore_index=True)
    df = df.sort_values("记账日期").reset_index(drop=True)
    return df
