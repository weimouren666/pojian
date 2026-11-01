# 《破茧》项目学习手册 —— 跟着做一遍 analyze.py

> 这份手册面向 Python 初学者：不需要你提前会 pandas 和 matplotlib。
> 每一课的结构都是：**这一步在干什么（意义）→ 知识点讲解 → 动手练习**。
> 全部课程学完，你应该能不看原代码、只看本手册，自己敲出整个 analyze.py。

---

## 开始之前

你需要已经会的东西很少：**变量、字符串、列表、for 循环、函数调用**（就是 Python 课最开头那几节）。

环境确认（在项目根目录 `pojian/` 打开终端执行）：

```bash
python --version          # 应显示 3.x
python -c "import pandas; print(pandas.__version__)"
python -c "import matplotlib; print(matplotlib.__version__)"
```

三条都不报错，就可以开始。

---

## 全局地图：analyze.py 一共干了五件事

```
① 导入工具 + 定路径        （第 0 课）
② 读入数据 → 得到"表格"   （第 1 课）
③ 清洗：去重 / 修日期 / 翻译类别 （第 2 课）
④ 三个分析，每个都"算一下 + 画一张图"（第 3、4、5 课）
⑤ 存图收尾                （第 6 课）
```

先把 analyze.py 打开放在旁边，每学一课就去原代码里找到对应的那几行对照。

---

## 第 0 课：导入工具与路径

**这一步在干什么**：把要用的工具（库）搬进来，并告诉程序"数据在哪里、图存哪里"。

### 知识点 1：import —— 借工具

Python 本体很小，干活靠"库"。 analyze.py 开头四行：

```python
import json                    # 读 JSON 文件用（类别翻译表是 JSON 格式）
from pathlib import Path       # 现代化的路径（文件位置）处理工具
import matplotlib.pyplot as plt  # 画图工具，习惯上缩写为 plt
import pandas as pd            # 表格处理工具，习惯上缩写为 pd
```

`as pd` 的意思是"起个短别名"——之后写 `pd.read_csv(...)` 而不是 `pandas.read_csv(...)`。这只是约定俗成，你写全名也能跑。

### 知识点 2：Path —— 路径是个对象

```python
ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)
```

逐行拆解：

| 代码 | 意思 |
|---|---|
| `Path(__file__)` | `__file__` 是"当前这个 .py 文件自己的位置"，包上 Path 变成路径对象 |
| `.resolve()` | 把相对路径变成绝对路径（如 `C:\...\pojian\src\analyze.py`） |
| `.parent` | 往上跳一层目录。`.parent.parent` 就是跳两层：`src/` → `pojian/` |
| `ROOT / "data"` | Path 对象用 `/` 拼接子目录（这是 Path 特有的写法，等价于字符串拼接，但不用操心 `\` 还是 `/`） |
| `.mkdir(exist_ok=True)` | 创建文件夹；`exist_ok=True` = 已经存在也不报错 |

**为什么要这么绕？** 因为写死 `C:/Users/.../data` 的代码，换台电脑就废了。用"从脚本自身位置推算"的写法，谁拿到项目都能跑。

### 动手练习 0

新建 `src/practice0.py`，打印出你的项目根目录：

```python
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
print(ROOT)
print(ROOT / "data")
```

在 `src/` 下运行，确认第二行打印的是 `...\pojian\data`。

---

## 第 1 课：读入数据 —— 认识 DataFrame

**这一步在干什么**：把 CSV 文件读成 Python 里的"表格对象"，后续所有操作都基于它。

### 知识点 3：CSV 和 DataFrame

CSV 就是"用逗号分隔的文本表格"，Excel 能开，纯文本能看。

```python
df = pd.read_csv(DATA / "USvideos.csv")
```

这一行返回的对象叫 **DataFrame**（数据框）——你可以把它理解成"Python 里的 Excel 表"：

- 有**行**（每行 = 一条记录，这里是"某视频在某天登上热门榜"）
- 有**列**（每列 = 一个字段，如 title、views）
- `df["views"]` 取出一列，得到的是 **Series**（带索引的一串数）

### 知识点 4：先"体检"再干活

拿到数据永远先看三样：

```python
print(df.shape)        # (行数, 列数)，本项目 (40949, 16)
print(df.head(3))      # 前 3 行长什么样
print(df["views"].max())  # 某列的最大值，验证数字列能正常算
```

### 动手练习 1

```python
import pandas as pd
from pathlib import Path
DATA = Path(__file__).resolve().parent.parent / "data"
df = pd.read_csv(DATA / "USvideos.csv")
print(df.shape)
print(df[["title", "views"]].head(5))   # 双中括号 = 同时取多列
```

---

## 第 2 课：清洗三件事

**这一步在干什么**：原始数据总有"重复的、格式不对的、看不懂的"，先收拾干净再分析。

### 知识点 5：去重 drop_duplicates

```python
df = df.drop_duplicates()
```

一行完全相同的记录只留一条。本项目去掉了 48 条重复记录。为什么会有重复？采集数据时同一条记录被记录两次很常见——**先去重是数据分析的肌肉记忆**。

### 知识点 6：日期解析 to_datetime

CSV 里的日期只是字符串（`"18.14.01"`），不能比较先后、不能画时间轴，要转成日期类型：

```python
df["trend_dt"] = pd.to_datetime(df["trending_date"], format="%y.%d.%m")
```

- `df["trend_dt"] = ...`：**新建一列**，把转换结果存进去（原列不动）
- `format="%y.%d.%m"`：告诉 pandas 这串字符的格式是 **两位年.日.月**（`%y`=两位年份，`%d`=日，`%m`=月）
- 这个数据集的日期偏偏是"年.日.月"顺序（比如 `18.14.01` 其实是 2018 年 1 月 14 日），不写 format 就会被解析错

### 知识点 7：字典 + map —— 给类别"翻译"

`category_id` 列全是数字（22、24、10……），人看不懂。翻译表存在 JSON 文件里：

```python
with open(DATA / "US_category_id.json", encoding="utf-8") as f:
    cat_items = json.load(f)["items"]
id2name = {int(item["id"]): item["snippet"]["title"] for item in cat_items}
df["category"] = df["category_id"].map(id2name)
```

两个新东西：

1. `with open(...) as f`：打开文件的标准写法，代码块结束自动关闭文件
2. `{A: B for item in 列表}`：**字典推导式**——循环构建字典。这句把 JSON 里的 32 个类别压成 `{22: "People & Blogs", 10: "Music", ...}` 这样的对照表

然后 `df["category_id"].map(id2name)`：对这一列的**每个值**，去字典里查对应的中文/英文名，整列一次性翻译完。

### 动手练习 2

接练习 1 的代码继续写：

```python
df = df.drop_duplicates()
df["trend_dt"] = pd.to_datetime(df["trending_date"], format="%y.%d.%m")
print("唯一视频数:", df["video_id"].nunique())   # nunique = 数一列里有几个不同值
print("日期范围:", df["trend_dt"].min().date(), "->", df["trend_dt"].max().date())
```

预期输出：唯一视频 6351，日期 2017-11-14 到 2018-06-14。**对上了就说明你的清洗是对的。**

---

## 第 3 课：分析① 类型分布 —— value_counts 与条形图

**这一步在干什么**：数一数 32 个类别各占多少条上榜记录，画成横条图，回答"谁在霸榜"。

### 知识点 8：value_counts —— 分类计数神器

```python
cat_counts = df["category"].value_counts()
```

一行得到：每个类别出现几次、按次数降序排好。它返回一个 Series，索引是类别名，值是次数。

```python
cat_share = cat_counts / cat_counts.sum() * 100   # 整列除一个数 = 每个值都除，得到百分比
top3_share = cat_share.head(3).sum()              # 前 3 名占比相加
```

**Series 的算术是"整列一起算"**——这叫向量化运算，不用写 for 循环。

### 知识点 9：画横条图 barh

```python
top10 = cat_counts.head(10)[::-1]      # 取前10再反转：barh 从下往上画，反转后最大的在顶部
fig1, ax1 = plt.subplots(figsize=(10, 6), dpi=150)
ax1.barh(top10.index, top10.values, color=C_MAIN, height=0.62)
fig1.savefig(OUT / "fig1_类型分布.png", bbox_inches="tight")
plt.close(fig1)
```

记住这套"画图五件套"，matplotlib 每张图都是这个节奏：

1. `plt.subplots(figsize, dpi)` → 创建画布（fig）和坐标系（ax），返回两个对象
2. `ax.某图表函数(...)` → 在坐标系上画
3. `ax.set_title / set_xlabel...` → 加标题和轴标签
4. `fig.savefig(路径)` → 存文件（**必须在 show/close 之前**）
5. `plt.close(fig)` → 释放内存

### 知识点 10：zip —— 给每根条写数值

```python
for bar, val in zip(bars, top10.values):
    ax1.text(bar.get_width() + 60, bar.get_y() + bar.get_height() / 2, f"{val} 条")
```

`zip` 把"每根条的图形对象"和"对应的数值"一一配对，循环里就能拿到条的位置和长度，把数字写在条旁边。`f"{val}"` 是 f-string 格式化，`f"{x:.1f}%"` 表示保留 1 位小数。

### 动手练习 3

只算不画，打印 Top3 类别和占比：

```python
cat_counts = df["category"].value_counts()
top3 = cat_counts.head(3)
for name, n in top3.items():          # items() 让循环同时拿到索引和值
    print(f"{name}: {n} 条 ({n / cat_counts.sum() * 100:.1f}%)")
```

预期看到 Entertainment、Music、Howto & Style 三行，合计约 50.3%。

---

## 第 4 课：分析② 流量集中度 —— groupby 与洛伦兹曲线

**这一步在干什么**：把 6351 个视频按播放量从高到低排队，画"累计流量占比"曲线——看头部 20% 的视频吃掉多少流量。这是全项目最核心的一段。

### 知识点 11：groupby —— 分组聚合

一个关键事实：**数据集里同一个视频会出现很多天**（霸榜 6 天就是 6 行）。所以"每个视频的播放量"不能直接看，要先分组：

```python
video_views = df.groupby("video_id")["views"].max().sort_values(ascending=False)
```

从左往右读这句话：

| 片段 | 意思 |
|---|---|
| `df.groupby("video_id")` | 按 video_id 分组——同一个 id 的所有行归为一组 |
| `["views"]` | 每组里只看 views 这一列 |
| `.max()` | 每组取最大值（= 该视频霸榜期间的最高播放量） |
| `.sort_values(ascending=False)` | 整列按数值降序排列 |

groupby 的口诀：**分组 → 选列 → 聚合**（聚合就是 max/sum/mean/count 这类"多变一"操作）。

### 知识点 12：cumsum —— 累计求和

```python
cum_share = video_views.cumsum() / video_views.sum()
```

`cumsum` 给个直观例子：`[1, 2, 3, 4]` 的 cumsum 是 `[1, 3, 6, 10]`——每个位置变成"从头到这里的总和"。

除以总和后，每个位置的值变成 0~1 之间：**第 k 名位置 = 播放量前 k 名的视频共占全部流量的比例**。把这条线画出来，就是经济学里的"洛伦兹曲线"——线越陡（越快逼近 100%），说明流量越集中。

### 知识点 13：iloc —— 按位置取值

```python
top20_pct = int(n_videos * 0.2)          # 前20%是第几个视频
top20_share = cum_share.iloc[top20_pct - 1] * 100   # 取该位置的累计占比
```

`iloc[数字]` = "取第 N 个"（从 0 数）。想知道"前 20% 的人占了多少"，就是去曲线的第 20% 位置读数。

### 知识点 14：辅助线与标注

```python
ax2.axvline(top20_pct, color=C_ACCENT, ls="--", lw=1.5)   # 竖虚线
ax2.axhline(top20_share / 100, color=C_ACCENT, ls="--", lw=1.5)  # 横虚线
ax2.annotate("头部 20% 视频占 79.4% 播放量",
             xy=(top20_pct, top20_share / 100),       # 箭头指向哪
             xytext=(n_videos * 0.32, top20_share / 200),  # 文字放哪
             arrowprops=dict(arrowstyle="->", color=C_ACCENT))
```

`axvline/axhline` 画参考线，`annotate` 画"文字+箭头"。让图自己讲出结论，是数据可视化的关键。

### 动手练习 4

不算图，只打印两个关键数字：

```python
video_views = df.groupby("video_id")["views"].max().sort_values(ascending=False)
cum = video_views.cumsum() / video_views.sum()
n = len(video_views)
print(f"头部20%视频占: {cum.iloc[int(n*0.2)-1]*100:.1f}%")
print(f"尾部50%视频占: {100 - cum.iloc[int(n*0.5)-1]*100:.1f}%")
```

预期：79.4% 和 4.8%。**这两个数字就是报告里的核心论据，你现在能自己算出来了。**

---

## 第 5 课：分析③ 霸榜天数 —— nunique 与直方图

**这一步在干什么**：统计每个视频在榜上待了几天，看分布——大量视频长期霸榜，说明榜单在"复读"。

### 知识点 15：nunique —— 数不同值的个数

```python
days_on_trend = df.groupby("video_id")["trend_dt"].nunique()
```

还是 groupby 口诀：按视频分组 → 看 trend_dt 列 → 数**不同日期的个数**（`.nunique()`）。得到的结果就是"每个视频霸榜了几天"的 Series。

聚合函数三兄弟：`.max()` 取最大、`.sum()` 求和、`.nunique()` 数不同值。`.median()` 中位数也常用：`days_on_trend.median()`。

### 知识点 16：hist 直方图 + 一行两图

```python
fig3, (ax3a, ax3b) = plt.subplots(1, 2, figsize=(12, 5.2),
                                  gridspec_kw={"width_ratios": [1.4, 1]})
ax3a.hist(days_on_trend, bins=range(1, days_on_trend.max() + 2), color=C_MAIN, edgecolor="white")
```

- `plt.subplots(1, 2)` = 一行两列两个坐标系，返回值用 `(ax3a, ax3b)` 两个变量接住
- `gridspec_kw={"width_ratios": [1.4, 1]}` = 左图宽右图窄（1.4 : 1）
- `hist` 直方图：把数值切桶（`bins`）数个数画柱子，用来看"分布"。`edgecolor="white"` 让相邻柱子有白色分隔线，更清晰

右边的"钉子户"图用普通 `bar` 柱状图：`ax3b.bar(labels, vals)`，再配合 `ax3b.text(i, v+1.5, f"{v:.0f}%", ha="center")` 在柱顶写百分比。

### 动手练习 5

```python
days = df.groupby("video_id")["trend_dt"].nunique()
stayers = days[days >= 7].index          # 布尔筛选：霸榜≥7天的视频id列表
vv = df.groupby("video_id")["views"].max()
share = vv[vv.index.isin(stayers)].sum() / vv.sum() * 100
print(f"钉子户({len(stayers)}个)占播放量: {share:.1f}%")
```

预期：2528 个，72.8%。注意 `days[days >= 7]` 这种**布尔筛选**写法（条件写在方括号里）——pandas 最常用的取子集方式。

---

## 第 6 课：图表的公共细节

**这一步在干什么**：所有图共享的配置，放在脚本开头设一次，全篇生效。

### 知识点 17：中文字体与配色常量

```python
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]   # 图里能显示中文
plt.rcParams["axes.unicode_minus"] = False               # 修复负号显示成方块的问题

C_MAIN = "#1B3A6B"     # 深蓝：主色
C_ACCENT = "#C9A227"   # 金色：强调
```

`#1B3A6B` 这种是颜色的十六进制编码（可以直接从配色网站抄）。用**大写常量**存起来，改配色时只改一处。

### 知识点 18：收尾三件套

```python
fig.tight_layout()      # 自动调整边距，防止文字被裁掉
fig.savefig(OUT / "xxx.png", bbox_inches="tight")   # bbox_inches="tight" 存紧凑版
plt.close(fig)          # 关闭画布释放内存（批量画图时不关会越用越卡）
```

### 动手练习 6（把前 5 课串起来）

把练习 3 和练习 4 合并成一个脚本跑通，你就已经写出了 analyze.py 的核心逻辑——剩下的只是把它画出来。

---

## 第 7 课：从零拼装（终极检验）

现在关掉 analyze.py，只开本手册，从空白文件敲起。建议顺序：

1. 抄第 0 课的导入和路径（这 8 行可以照抄，不用背）
2. 第 1、2 课：读数据、清洗，跑通打印 shape
3. 第 3 课：算类型分布 → 画 fig1
4. 第 4 课：算集中度 → 画 fig2
5. 第 5 课：算霸榜天数 → 画 fig3
6. 跟原版输出对比，三张图数字一致即毕业

### 常见报错对照表

| 报错 | 原因 | 解决 |
|---|---|---|
| `FileNotFoundError` | 路径不对 | 打印 `DATA` 检查指向哪里；确认在 `src/` 下运行 |
| `KeyError: 'xxx'` | 列名拼错 | `print(df.columns)` 对照真实列名 |
| 图里中文变方块 | 字体没设 | 检查 rcParams 那两行是否在画图**之前**执行 |
| `ValueError` 日期 | format 不对 | 记住是 `%y.%d.%m`（年.日.月） |

---

## 附：知识点速查表

### pandas（本项目用到的全部）

| 方法 | 作用 | 项目中的用途 |
|---|---|---|
| `read_csv(路径)` | 读 CSV 成 DataFrame | 读入 40949 条记录 |
| `df.shape` / `df.head()` | 看规模 / 预览 | 每次拿到数据先体检 |
| `drop_duplicates()` | 删全同行 | 清洗 48 条重复 |
| `to_datetime(列, format=)` | 字符串→日期 | 解析"年.日.月"格式 |
| `df["新列"] = ...` | 新建一列 | 存日期、存翻译后类别 |
| `.map(字典)` | 按字典逐值翻译 | category_id → 类别名 |
| `.value_counts()` | 分类计数降序 | 类型分布 |
| `.groupby(列)[列].agg()` | 分组→选列→聚合 | 每视频取 max views / 数 nunique 天数 |
| `.sort_values(ascending=False)` | 降序排序 | 集中度排队 |
| `.cumsum()` | 累计求和 | 洛伦兹曲线 |
| `.iloc[n]` | 按位置取值 | 读 20% 处的占比 |
| `.sum() / .max() / .median() / .nunique()` | 聚合四兄弟 | 各种统计 |
| `df[条件]` | 布尔筛选 | 取霸榜≥7天的视频 |

### matplotlib（本项目用到的全部）

| 函数 | 作用 |
|---|---|
| `plt.subplots(行, 列, figsize, dpi)` | 创建画布和坐标系 |
| `ax.barh / ax.bar / ax.plot / ax.hist` | 横条 / 柱状 / 折线 / 直方图 |
| `ax.set_title / set_xlabel / set_ylabel` | 标题与轴标签 |
| `ax.text / ax.annotate` | 写文字 / 文字+箭头 |
| `ax.axvline / ax.axhline` | 竖/横参考线 |
| `ax.spines[...].set_visible(False)` | 隐藏边框 |
| `fig.tight_layout()` / `fig.savefig()` / `plt.close()` | 收尾三件套 |
| `plt.rcParams[...]` | 全局配置（中文字体） |

---

## 学习说明

本手册与 src/analyze.py 配套，是「AI 协作学习法」第三步（独立重写跑通）的练习材料：**思路是我自己拆的，代码是 AI 讲解后我重写的**——这正是我在职业规划大赛报告中写明的学习方法。
