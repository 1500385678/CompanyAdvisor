# T3 对标匹配 Prompt v0.1

> **入库日期**:2026-09-01
> **对应主计划**:[项目开发计划.md §5 Phase 0 第 4 项(LLM 4 类任务基线 #3)](../../项目开发计划.md)
> **父设计稿**:[01-4类LLM任务基线设计稿.md §2(4 类任务一览 T3 行)](./01-4类LLM任务基线设计稿.md)
> **关联设计稿**:[../护城河/01-护城河评分schema设计稿.md](../护城河/01-护城河评分schema设计稿.md) + [02-T2护城河评估prompt-v0.1.md](./02-T2护城河评估prompt-v0.1.md)
> **种子清单**:[../公司/01-种子公司清单.md](../公司/01-种子公司清单.md)(38 家 · 8 行业 · 三市覆盖)
> **状态**:**设计稿**(尚需 1)种子清单 5 家头部批量回测对标质量,2)飞书 P0 用户盲评校准"为什么可比"叙事)
> **维护**:22-公司-Company 行业顾问

## 1. 背景与目标

- **来源**:T1 设计稿 §2 表第 3 行 T3 对标匹配,落地计划"2026-08-31 落地行业聚类 + 解释两段 prompt + 38 家种子清单对标回测"——08-31 cron 实际落地 T2 护城河评估(顺延),T3 顺延至今日(09-01)。
- **核心定位(与 T1/T2 的差异)**:T1 = LLM 主导(阅读理解 + 摘要),T2 = 规则主导 + LLM 辅(语义注释),**T3 = 规则聚类 + LLM 解释(中等权重)**。原因:可比公司筛选本质是"行业 + 主营相似度 + 规模/估值带"的分类问题,规则(申万二级 + 主营关键词)能给 5-10 家高质量候选,LLM 在两件事上发力:① 把候选筛成最终 Top-K 并解释"为什么可比",② 把候选公司的多维数据拼成对标表(营收/利润/毛利率/估值)。
- **目标**:在 Phase 0 结束前(09-06)给出 **行业聚类 + LLM 解释 + 多维对标表** 的最小可复用 prompt 模板,供 Phase 1 直接接 5-10 家头部公司跑通"对标矩阵"模块。
- **现状**(2026-09-01):4 项中 **2/4**(T1+T2)落地 → 今日补 **3/4**(T3 对标匹配),剩 T4 事件归因。

## 2. T3 在 4 类任务中的位置

| 项 | T1 财报速读 | T2 护城河评估 | **T3 对标匹配** | T4 事件归因 |
|---|---|---|---|---|
| LLM 角色 | 主导 | 辅(注释 + 校核) | **中(行业聚类后做"为什么可比"解释)** | 主导 |
| 输入主源 | pdfplumber JSON | 5 年财务指标 JSON + 规则预评分 | **目标公司基本面 + 38 家种子清单** | 近 5 年公告/新闻片段 |
| 期望输出 | 4 段摘要 + 同比 | 5 维 D1-D5 档位 + LLM 叙事 + 证据回链 | **5-10 家可比公司 + 多维对标表 + 可比理由** | 关键事件 + 因果链 |
| 状态 | ✅ v0.1 (08-29) | ✅ v0.1 (08-31) | **🚧 v0.1 (09-01,本文)** | ⏳ pending |

## 3. 输入契约

### 3.1 输入 JSON(两段:目标公司 + 候选池)

```jsonc
{
  "target": {
    "company": "<公司名,如 贵州茅台>",
    "ticker": "<600519.SH / 00700.HK / AAPL 等>",
    "industry_sw_l2": "<申万二级,如 白酒>",
    "industry_sw_l3": "<申万三级,如 白酒Ⅲ>",
    "main_business": "<主营一句话,如 高端白酒生产销售>",
    "fy_revenue_cny_yi": 1500.0,                  // 最近完整财年营收(亿元 RMB)
    "fy_net_income_cny_yi": 600.0,                // 最近完整财年净利(亿元 RMB)
    "market_cap_cny_yi": 22000.0,                 // 当前总市值(亿元 RMB,跨市场按即期汇率折算)
    "gross_margin_pct": 53.6,                     // 最近完整财年毛利率(%)
    "moat_type_hint": "deep"                      // 可选,来自 T2 评估;无则填 null
  },
  "candidate_pool": [                              // 由规则引擎预筛(申万二级 + 主营关键词 + 规模带)
    {
      "company": "五粮液",
      "ticker": "000858.SZ",
      "industry_sw_l2": "白酒",
      "main_business": "高端白酒生产销售",
      "fy_revenue_cny_yi": 800.0,
      "fy_net_income_cny_yi": 280.0,
      "market_cap_cny_yi": 6500.0,
      "gross_margin_pct": 75.2,
      "rule_pre_selected": true,                  // 规则引擎标记
      "rule_reasons": ["同申万二级", "同主营关键词", "市值带 5000-10000 亿"]
    },
    ...   // 通常 8-15 家候选,由 §4.1 规则引擎输出
  ],
  "max_matches": 10,                              // 期望输出可比公司数,默认 5-10
  "valuation_basis": "PE_TTM"                     // 对标表估值口径:PE_TTM / PB / PS / EV_EBITDA
}
```

### 3.2 数据源契约(Phase 1 落地)

| 字段 | 数据源 |
|---|---|
| `target.industry_sw_l2/l3` | 恒生聚源 `StockBelongIndustry` + 申万行业分类 |
| `target.main_business` | 公司画像 `MainBusiness` 字段(自维护)+ 年报"公司业务"节 |
| `target.fy_revenue/ni/market_cap` | 恒生聚源 `FinancialStatement` + `StockDailyQuote` |
| `target.gross_margin_pct` | 恒生聚源 `FinancialAnalysis.GrossMargin` |
| `target.moat_type_hint` | T2 护城河评估输出(可选,无则 null) |
| `candidate_pool` | 种子清单 38 家 + 申万二级匹配 + 主营关键词相似度(0.6+) |
| `valuation_basis` | 恒生聚源 `StockValueAnalysis` |

> **Phase 0 真实场景约束**:种子清单 38 家已在 08-26 入库,本任务用其中 5 家头部公司(茅台/腾讯/宁德/招行/英伟达)做 prompt 联调;批量对标回测放到 Phase 0 收口前。

## 4. Prompt 模板(两段式:规则聚类 → LLM 筛选 + 解释)

> **设计要点**:Phase 0 的 LLM **不直接找可比公司**,只做"筛 Top-K + 解释 + 对标表"——避免 LLM 在"哪几家可比"上幻觉(尤其跨市场时容易乱配)。

### 4.1 Prompt A — 候选池筛选(规则引擎,非 LLM,仅留契约)

> 本步骤在 Phase 1 由 Python 规则引擎执行(`scripts/peer_match_engine.py` 待落地),不在 LLM 侧。契约写下来保证 LLM 收到的是已对齐可比度量的输入。

| 过滤维度 | 通过条件 | 备注 |
|---|---|---|
| **行业(申万二级)** | `candidate.industry_sw_l2 == target.industry_sw_l2` | 硬约束,必须一致 |
| **行业(申万三级)** | `candidate.industry_sw_l3 == target.industry_sw_l3` 加分(不强制) | 三级一致优先于二级 |
| **主营关键词相似度** | 主营关键词 Jaccard ≥ 0.6(用 LLM/关键词抽取后的词袋比对) | 软约束,>= 0.4 即可入选 |
| **规模带** | 营收或市值在目标公司 0.3-3 倍区间 | 避免小公司对比巨头(失真) |
| **市场可覆盖** | A 股 / 港股 / 美股均可入池,跨市场时按汇率折算市值 | 不限单一市场,跨市场可比加分 |
| **护城河提示** | `moat_type_hint` 与候选 `moat_type` 一致时加分 | 可选,无则跳过 |

**规则引擎输出**:`candidate_pool` 通常含 8-15 家标的,每条带 `rule_pre_selected=true` + `rule_reasons[]`。**LLM 从中筛 5-10 家**(可少于候选数,不允许超出)。

### 4.2 Prompt B — LLM 筛选 + 解释 + 对标表(给 Claude / GPT-4o)

```
你是资深卖方分析师助手。给定一个"目标公司"+ 规则引擎预筛的候选池(同行业 + 规模带),请完成三件事:
1) 从候选池中筛出 5-10 家最可比公司(Top-K),并写"为什么可比"叙事(基于行业/主营/规模/护城河类型)
2) 生成多维对标表(营收/净利/毛利率/估值等关键指标)
3) 给目标公司一个"对标定位"总结(在可比组中的位置)

## 输入
- 目标公司: <target JSON>
- 候选池: <candidate_pool 列表,8-15 家,每家带 rule_reasons>
- 期望可比数: <max_matches,默认 5-10>
- 估值口径: <valuation_basis,如 PE_TTM>

## 输出(JSON,严格遵循 schema,不要多余字段)
{
  "target": {
    "company": "<公司名>",
    "ticker": "<ticker>",
    "industry_sw_l2": "<申万二级>",
    "summary": "<1 句话目标公司定位,如 高端白酒绝对龙头,深护城河>"
  },
  "matches": [
    {
      "company": "<可比公司名>",
      "ticker": "<ticker>",
      "comparable_dimensions": [
        "同申万二级(白酒)",
        "同主营(高端白酒)",
        "市值带 5000-10000 亿",
        "护城河类型匹配(deep)"
      ],
      "narrative": "<1-2 句话可比叙事,基于维度数组,中文,≤ 120 字>",
      "match_score": <int 1-10, 10=完全可比, 1=勉强可比>
    },
    ...   // 共 5-10 项,按 match_score 降序
  ],
  "comparison_table": {
    "headers": ["公司", "代码", "营收(亿)", "净利(亿)", "毛利率(%)", "市值(亿)", "估值(<valuation_basis>)"],
    "rows": [
      ["贵州茅台", "600519.SH", 1500.0, 600.0, 53.6, 22000.0, 28.5],
      ["五粮液", "000858.SZ", 800.0, 280.0, 75.2, 6500.0, 21.3],
      ...   // 第 1 行必须为目标公司,后续为 matches[]
    ]
  },
  "target_positioning": "<2-3 句话,在可比组中的相对位置,如 在毛利率维度领先(53.6% vs 组均值 65%),但净利率显著高于均值,体现品牌溢价;估值溢价 35%,反映 deep 护城河定价>",
  "limitations": [
    "<本评估的局限 1>",
    ...
  ],                                              // 1-3 条
  "confidence": "high | medium | low",
  "version": "peer-llm-v0.1"
}

## 约束
- matches[] 必须从 candidate_pool 选取,不允许 LLM 自由添加候选池外的公司
- comparable_dimensions 每条 ≤ 30 字,1-5 条,中文
- narrative 数字必须能从 target/candidate_pool JSON 验证,不允许编造
- comparison_table 第 1 行必须为目标公司(便于画图时锚定)
- match_score 反映"可比度",10=业务/规模/护城河/估值都高度可比,1=仅行业可比
- target_positioning 至少包含 1 维"目标 vs 可比组均值"的对比
- limitations 必须至少 1 条,提示本次对标的盲点(如 "候选池仅 38 家种子,可能漏掉边缘玩家")
- 中文输出,标点用全角
- 数字保留 1 位小数(百分比)或 2 位小数(估值倍数)
```

### 4.3 两段流程示意

```
[目标公司] → 画像(行业/主营/营收/市值/护城河)→ target JSON
                                                    ↓
[种子清单 38 家] → 申万二级 + 主营相似度 + 规模带 → 规则引擎
                                                    ↓
                                            candidate_pool(8-15 家)
                                                    ↓
                              target + candidate_pool + max_matches
                                                    ↓
                                                  [LLM]
                                                    ↓
                            matches[](5-10) + comparison_table + target_positioning
```

## 5. 输出契约(JSON Schema,Pydantic 雏形)

```python
from pydantic import BaseModel, Field
from typing import Literal

class TargetInfo(BaseModel):
    company: str
    ticker: str
    industry_sw_l2: str
    summary: str = Field(..., min_length=8, max_length=80)

class ComparableMatch(BaseModel):
    company: str
    ticker: str
    comparable_dimensions: list[str] = Field(..., min_length=1, max_length=5)
    narrative: str = Field(..., min_length=15, max_length=120)
    match_score: int = Field(..., ge=1, le=10)

class ComparisonRow(BaseModel):
    """单行 7 列:公司/代码/营收/净利/毛利率/市值/估值"""
    company: str
    ticker: str
    revenue_yi: float
    net_income_yi: float
    gross_margin_pct: float
    market_cap_yi: float
    valuation_multiple: float

class PeerMatchReport(BaseModel):
    target: TargetInfo
    matches: list[ComparableMatch] = Field(..., min_length=5, max_length=10)
    comparison_table: dict            # 必含 headers(7 列) + rows(>= 6 行:1 目标 + 5-10 可比)
    target_positioning: str = Field(..., min_length=20, max_length=200)
    limitations: list[str] = Field(..., min_length=1, max_length=3)
    confidence: Literal["high", "medium", "low"]
    version: str = "peer-llm-v0.1"

    @property
    def match_count(self) -> int:
        return len(self.matches)
```

> **关键继承**:`TargetInfo` 字段与护城河 schema 的 `MoatLLMReport.target` 对齐(同字段名),保证 Phase 1 把 T2 + T3 输出合并为"公司全景报告"时字段一致。

## 6. 4 档评分校准标准

| 档位 | 含义 | 通过条件 |
|---|---|---|
| 4 = **完全可用** | Top-K 选得准 + 可比叙事对齐候选池数据 + 对标表无错位 + 定位有数字支撑 | matches[] 全部在 candidate_pool 内;narrative 数字与 JSON 一致;comparison_table 7 列完整;target_positioning 至少 1 处"目标 vs 均值"对比 |
| 3 = **基本可用** | Top-K 合理 + 叙事合理但 dimensions 略泛化 + 对标表基本对齐 | matches[] 全部在 pool;允许 1 处轻微意译;comparison_table 数字可定位;limitations 存在 |
| 2 = **可参考** | Top-K 漏 1 家明显可比 / dimensions 含编造维度 / 对标表缺 1 列 | matches[] 缺 1 家候选池内公司(明显该选的);或 dimensions 引用了 pool 外信息;或 comparison_table 缺 1 列 |
| 1 = **不可用** | LLM 自由添加候选池外公司 / 严重 hallucination / JSON schema 破 | matches[] 含 pool 外公司(致命);narrative 数字与 JSON 不符;字段缺失或乱码;matches < 5 或 > 10 |

**Phase 0 收口标准**:至少 1 个模型在 5 份样例(种子清单前 5 家)上**平均 ≥ 3 档**,且 matches[] 全部命中候选池(pool 外公司 = 0)。

## 7. 验证步骤(本地最小闭环)

1. 准备 5 家样例(茅台 600519.SH / 腾讯 0700.HK / 宁德 300750.SZ / 招行 600036.SH / 英伟达 NVDA.US)的目标 JSON(用恒生聚源 + 种子清单字段)
2. 跑规则引擎(Phase 0 可手工对照 §4.1 过滤表,Phase 1 再写 `scripts/peer_match_engine.py`)筛出 8-15 家候选
3. 把 target + candidate_pool 喂给 LLM(Claude Sonnet 4 / Qwen-Finance / GPT-4o 任选),得 §5 PeerMatchReport
4. 用 §6 4 档标尺人工盲评(重点看"为什么可比"叙事是否真的有信息量,而非空话)
5. 写报告:`Inspiration/LLM基线/04-对标匹配基线报告.md`(Phase 0 收口时落地)
6. Phase 0 收口前(09-06)扩到种子清单前 10 家批量回测,出基线报告

## 8. 不做(本期边界)

- **不写规则引擎代码**(本期只定义契约,Phase 1 再落地 `scripts/peer_match_engine.py`;Phase 0 用手工对照过滤表联调 LLM)
- **不做模型对比基准**(本设计稿只跑 1 个模型做联调,Claude vs Qwen-Finance vs GPT-4o 对比放到 Phase 1)
- **不做动态行业映射**(本期固定用申万二级;Phase 2 考虑 GICS / 恒生行业并行)
- **不接 RAG**(纯 target + candidate_pool 输入,无外部公告/研报检索)
- **不评估 LLM 主导匹配**(本设计稿明确 LLM 只筛 + 解释 + 制表,不替代规则找候选;避免 LLM 幻觉"想出一家不存在的可比公司")
- **不强制同市场可比**(候选池允许跨 A 股 / 港股 / 美股,跨市场时按汇率折算;在 dimensions 中标注"跨市场"加分)

## 9. 变更记录

| 日期 | 版本 | 变更 |
|---|---|---|
| 2026-09-01 | v0.1 | 初稿:两段式契约(规则聚类 + LLM 筛/解释/制表) + 目标+候选池输入 JSON 模板 + Prompt A 过滤表 + Prompt B 选 Top-K + 多维对标表模板 + Pydantic schema(与护城河 schema 字段对齐) + 4 档校准 + 验证步骤 |

## 10. 关联文档

- [01-4类LLM任务基线设计稿.md §2(4 类任务一览 T3 行)](./01-4类LLM任务基线设计稿.md) — 父设计稿,T3 在 4 类任务中的位置
- [02-T2护城河评估prompt-v0.1.md](./02-T2护城河评估prompt-v0.1.md) — 同源姊妹篇,T2 输出可作为 T3 的 `moat_type_hint` 输入
- [../护城河/01-护城河评分schema设计稿.md](../护城河/01-护城河评分schema设计稿.md) — 字段对齐参考
- [../公司/01-种子公司清单.md](../公司/01-种子公司清单.md) — 候选池的源头(38 家 · 8 行业)
- [项目开发计划.md §5 Phase 0 第 4 项](../../项目开发计划.md) — 本任务对应主计划
- [公司顾问开发架构与计划.md §3 核心功能(对标矩阵模块)](../../公司顾问开发架构与计划.md)
- 后续:Phase 0 收口前落地 `Inspiration/LLM基线/04-对标匹配基线报告.md`(批量回测 + 4 档评分)
