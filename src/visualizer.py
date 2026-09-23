# -*- coding: utf-8 -*-
"""可视化看板：用 matplotlib 生成图表 PNG，供 Excel「可视化看板」工作表嵌入。"""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from config import OUTPUT_DIR

plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "Arial Unicode MS", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False


def build_charts(monthly_df: pd.DataFrame, pie_df: pd.DataFrame):
    """生成趋势图与支出结构饼图，返回 {key: Path}。"""
    paths = {}

    # 1) 月度收支趋势
    fig, ax = plt.subplots(figsize=(9, 4))
    months = monthly_df["月份"].astype(str).tolist()
    ax.bar(months, monthly_df["收入合计"], label="收入", color="#2e8b57", alpha=0.85)
    ax.bar(months, -monthly_df["支出合计"], label="支出", color="#cd5c5c", alpha=0.85)
    ax.plot(months, monthly_df["净流量"], color="#1f4e78", marker="o", label="净流量")
    ax.axhline(0, color="#888888", lw=0.8)
    ax.set_title("月度资金收支趋势", fontsize=13)
    ax.set_ylabel("金额（元）")
    ax.legend()
    fig.tight_layout()
    p = OUTPUT_DIR / "chart_trend.png"
    fig.savefig(p, dpi=110)
    plt.close(fig)
    paths["trend"] = p

    # 2) 支出结构饼图
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.pie(pie_df["金额"], labels=pie_df["科目"], autopct="%1.1f%%",
           startangle=90, textprops={"fontsize": 9})
    ax.set_title("支出结构（按会计科目 Top10）", fontsize=13)
    fig.tight_layout()
    p = OUTPUT_DIR / "chart_pie.png"
    fig.savefig(p, dpi=110)
    plt.close(fig)
    paths["pie"] = p

    return paths
