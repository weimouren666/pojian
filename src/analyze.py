# -*- coding: utf-8 -*-
"""
「破茧」项目 · 第一步：热门内容同质化数据分析
================================================
数据集：YouTube 美国区热门视频榜单（Trending YouTube Video Statistics）
        来源 Kaggle，GitHub 镜像：the-codingschool/TRAIN-datasets
        时间跨度 2017-11 ~ 2018-06，40,949 条上榜记录

回答的问题：热门内容是否存在"同质化"——
  分析① 类型分布：谁在霸榜？（内容类型是否高度集中）
  分析② 流量集中度：二八定律是否成立？（少数视频吃掉多数流量）
  分析③ 时间演化：霸榜能持续多久？（同一内容反复霸榜 = 算法复读机）

运行方式：python src/analyze.py  （在项目根目录 pojian/ 下运行）
"""

import json
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

# ---------------------------------------------------------------
# 路径设置：Path 是 Python 处理路径的现代方式（比字符串拼接安全）
# Path(__file__) 是本脚本文件的位置，.parent 一层层向上走
# ---------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)  # 输出目录不存在就创建

# 让 matplotlib 显示中文（Windows 自带微软雅黑）
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False  # 修复负号显示为方块的问题

# 统一配色：深蓝主色 + 金色强调（与参赛报告/PPT 视觉一致）
C_MAIN = "#1B3A6B"
C_ACCENT = "#C9A227"
C_GRAY = "#9AA5B4"

# ===============================================================
# 第 1 步：数据加载与清洗
# ===============================================================
df = pd.read_csv(DATA / "USvideos.csv")

# 完全重复的行直接去掉（同一视频同一天被记录两次的情况）
df = df.drop_duplicates()

# trending_date 的格式很反直觉："18.14.01" 其实是 2018年01月14日
# 即 年.日.月，所以 format 写成 '%y.%d.%m'（%y=两位年 %d=日 %m=月）
df["trend_dt"] = pd.to_datetime(df["trending_date"], format="%y.%d.%m")

# category_id 只是个数字（如 10），要靠 JSON 文件翻译成人类可读的类别名
# JSON 结构：items 列表，每项有 id 和 snippet.title
with open(DATA / "US_category_id.json", encoding="utf-8") as f:
    cat_items = json.load(f)["items"]
id2name = {int(item["id"]): item["snippet"]["title"] for item in cat_items}
df["category"] = df["category_id"].map(id2name)

# 每行 = 某视频在某天登上热门榜。同一个视频会在榜上停留多天，
# 所以"上榜记录数"和"视频个数"是两个不同的口径，分析时要分清。
print(f"清洗后：{len(df)} 条上榜记录，"
      f"{df['video_id'].nunique()} 个唯一视频，"
      f"时间跨度 {df['trend_dt'].min().date()} ~ {df['trend_dt'].max().date()}")

# ===============================================================
# 分析① 类型分布：谁在霸榜？
# 口径：热门榜单上每个"上榜记录"计一次，看各类别的记录数占比
# ===============================================================
cat_counts = df["category"].value_counts()          # 按类别计数，降序
cat_share = cat_counts / cat_counts.sum() * 100     # 转成百分比

fig1, ax1 = plt.subplots(figsize=(10, 6), dpi=150)
top10 = cat_counts.head(10)[::-1]  # 反转让最大的画在条形图最上方
colors = [C_ACCENT if i >= len(top10) - 3 else C_MAIN for i in range(len(top10))]
bars = ax1.barh(top10.index, top10.values, color=colors, height=0.62)

# 在每根条右端标注数量和占比（zip 把条和数值一一配对）
for bar, val in zip(bars, top10.values):
    ax1.text(bar.get_width() + 60, bar.get_y() + bar.get_height() / 2,
             f"{val} 条 ({val / cat_counts.sum() * 100:.0f}%)",
             va="center", fontsize=10, color="#2A3441")

ax1.set_title("谁在霸榜？YouTube 热门视频类型分布 Top 10", fontsize=15, pad=14, color=C_MAIN)
ax1.set_xlabel("上榜记录数（条）")
ax1.spines[["top", "right"]].set_visible(False)  # 去掉上右边框，更像报表
fig1.tight_layout()
fig1.savefig(OUT / "fig1_类型分布.png", bbox_inches="tight")
plt.close(fig1)

top3_share = cat_share.head(3).sum()
print(f"[分析①] Top3 类别（{cat_share.head(3).index.tolist()}）合计占 {top3_share:.1f}%")

# ===============================================================
# 分析② 流量集中度：二八定律是否成立？
# 口径：每个唯一视频取其榜单生涯的【最高播放量】（最后一次记录），
#      按播放量从高到低排序，看累计流量曲线有多陡
# ===============================================================
# groupby 把同一个视频的多条记录压缩成一条，取 max views
video_views = df.groupby("video_id")["views"].max().sort_values(ascending=False)
n_videos = len(video_views)

# cumsum 是累计和：第 k 个视频处的值 = 前 k 个视频的总播放量
# 除以总和后，纵轴变成"累计流量占比"（0→1），就是教科书上的洛伦兹曲线画法
cum_share = video_views.cumsum() / video_views.sum()

fig2, ax2 = plt.subplots(figsize=(10, 6), dpi=150)
ax2.plot(range(1, n_videos + 1), cum_share.values, color=C_MAIN, lw=2.5)

# 关键读数：头部 20% 视频吃掉多少流量？
top20_pct = int(n_videos * 0.2)
top20_share = cum_share.iloc[top20_pct - 1] * 100
ax2.axvline(top20_pct, color=C_ACCENT, ls="--", lw=1.5)
ax2.axhline(top20_share / 100, color=C_ACCENT, ls="--", lw=1.5)
ax2.annotate(f"头部 20% 视频\n占 {top20_share:.0f}% 播放量",
             xy=(top20_pct, top20_share / 100),
             xytext=(n_videos * 0.32, top20_share / 200),
             fontsize=13, color=C_ACCENT, fontweight="bold",
             arrowprops=dict(arrowstyle="->", color=C_ACCENT))

# 50% 分位辅助读数
mid_pct = int(n_videos * 0.5)
mid_share = cum_share.iloc[mid_pct - 1] * 100
print(f"[分析②] 头部 20% 视频占 {top20_share:.1f}% 播放量；"
      f"尾部 50% 视频合计仅占 {100 - mid_share:.1f}%")

ax2.set_title("流量集中度：少数视频吃掉多数流量（累计播放量曲线）",
              fontsize=15, pad=14, color=C_MAIN)
ax2.set_xlabel(f"视频（按播放量降序，共 {n_videos} 个）")
ax2.set_ylabel("累计播放量占比")
ax2.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
ax2.set_yticklabels(["0%", "25%", "50%", "75%", "100%"])
ax2.spines[["top", "right"]].set_visible(False)
fig2.tight_layout()
fig2.savefig(OUT / "fig2_流量集中度.png", bbox_inches="tight")
plt.close(fig2)

# ===============================================================
# 分析③ 时间演化：霸榜能持续多久？
# 口径：每个视频统计"上榜天数"（出现过的日期个数），
#      看分布——如果大量视频连续霸榜 10 天以上，
#      说明榜单在"复读"同样的内容
# ===============================================================
# groupby 后 .nunique() 数每个视频出现过多少个不同日期
days_on_trend = df.groupby("video_id")["trend_dt"].nunique()

fig3, (ax3a, ax3b) = plt.subplots(1, 2, figsize=(12, 5.2), dpi=150,
                                  gridspec_kw={"width_ratios": [1.4, 1]})

# 左图：霸榜天数的分布直方图（bins 按 1,2,3...30 天分桶）
bins = range(1, days_on_trend.max() + 2)
ax3a.hist(days_on_trend, bins=bins, color=C_MAIN, edgecolor="white")
ax3a.axvline(days_on_trend.median(), color=C_ACCENT, ls="--", lw=1.5)
ax3a.text(days_on_trend.median() + 0.6, ax3a.get_ylim()[1] * 0.9,
          f"中位数 {days_on_trend.median():.0f} 天", color=C_ACCENT, fontsize=12)
ax3a.set_title("一个视频能在热门榜待几天？", fontsize=14, color=C_MAIN)
ax3a.set_xlabel("上榜天数（天）")
ax3a.set_ylabel("视频个数")
ax3a.spines[["top", "right"]].set_visible(False)

# 右图：霸榜 ≥7 天的"钉子户"视频，占多少播放量？
stayers = days_on_trend[days_on_trend >= 7].index
share_by_stayers = video_views[stayers].sum() / video_views.sum() * 100
labels = ["霸榜 <7 天", "霸榜 ≥7 天\n（钉子户）"]
vals = [100 - share_by_stayers, share_by_stayers]
ax3b.bar(labels, vals, color=[C_GRAY, C_ACCENT], width=0.5)
for i, v in enumerate(vals):
    ax3b.text(i, v + 1.5, f"{v:.0f}%", ha="center", fontsize=13,
              fontweight="bold", color="#2A3441")
ax3b.set_title("钉子户视频占多少播放量？", fontsize=14, color=C_MAIN)
ax3b.set_ylabel("占全部播放量比例（%）")
ax3b.set_ylim(0, 110)
ax3b.spines[["top", "right"]].set_visible(False)

print(f"[分析③] 上榜天数中位数 {days_on_trend.median():.0f} 天，最长 {days_on_trend.max()} 天；"
      f"{len(stayers)} 个'≥7天钉子户'视频占 {share_by_stayers:.1f}% 播放量")

fig3.tight_layout()
fig3.savefig(OUT / "fig3_霸榜持续性.png", bbox_inches="tight")
plt.close(fig3)

print("\n三张图已输出到 output/ 目录")
