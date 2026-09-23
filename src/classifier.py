# -*- coding: utf-8 -*-
"""智能分类入账引擎：把流水摘要/对方户名自动映射到会计科目。

设计说明：
- 当前实现为「关键词 + 规则」引擎，透明、可解释、零外部依赖，适合简历演示与面试讲解。
- 预留扩展位：当命中置信度低（待分类）或需要语义理解时，可平滑替换为 LLM 接口，
  本引擎作为兜底与正则前置，降低调用成本。
- 输出「分类置信度」字段，用于对低置信样本排序、交人工复核，体现真实账务严谨性。
"""
import pandas as pd
from config import CLASSIFICATION_RULES

# 预转为小写，提升匹配效率
RULES = [(list(map(str.lower, kws)), subj, cat, dr)
         for kws, subj, cat, dr in CLASSIFICATION_RULES]


def classify_one(summary: str, counterpart: str):
    """对单条流水分类，返回 (科目, 类别, 方向, 置信度, 命中关键词)。"""
    text = f"{summary} {counterpart}".lower()
    for kws, subj, cat, dr in RULES:
        hit = [k for k in kws if k in text]
        if hit:
            conf = round(min(0.99, 0.6 + 0.2 * len(hit)), 2)
            return subj, cat, dr, conf, "/".join(hit[:3])
    # 未命中 -> 交人工复核
    return "待分类-人工复核", "未识别", "借", 0.30, ""


def classify_frame(df: pd.DataFrame) -> pd.DataFrame:
    """对整张流水 DataFrame 批量分类，原地新增分类相关列。"""
    res = df.apply(lambda r: classify_one(r["摘要"], r["对方户名"]), axis=1)
    df["会计科目"] = [x[0] for x in res]
    df["收支类别"] = [x[1] for x in res]
    df["借贷方向"] = [x[2] for x in res]
    df["分类置信度"] = [x[3] for x in res]
    df["匹配关键词"] = [x[4] for x in res]
    return df
