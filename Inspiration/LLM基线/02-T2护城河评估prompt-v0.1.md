# T2 护城河评估 Prompt v0.1

> **入库日期**:2026-08-31
> **对应主计划**:[项目开发计划.md §5 Phase 0 第 4 项(LLM 4 类任务基线 #2)](../../项目开发计划.md)
> **父设计稿**:[01-4类LLM任务基线设计稿.md §2(4 类任务一览 T2 行)](./01-4类LLM任务基线设计稿.md)
> **Schema 锚点**:[../护城河/01-护城河评分schema设计稿.md](../护城河/01-护城河评分schema设计稿.md)(v0.1,2026-08-28 入库,5 维等权 20 + 4 档评分 + Evidence Anchor + Pydantic)
> **状态**:**设计稿**(尚需 1)真实种子 5 家头部公司批量回测,2)飞书 P0 用户小范围盲评校准)
> **维护**:22-公司-Company 行业顾问

## 1. 背景与目标

- **来源**:T1 设计稿 §2 表第 2 行 T2 护城河评估,落地计划"2026-08-30 落地 5 维 LLM 评分 prompt + 证据回链契约"——08-30 cron 断档未落地,今日(08-31)补做。
- **核心定位(与 T1 的差异)**:**T1 = LLM 主导**(阅读理解 + 摘要),**T2 = 规则引擎主导 + LLM 辅**。原因:5 维评分有明确量化口径(毛利 σ、ROIC 均值、Top5 客户占比等),用规则算够稳且可复现;LLM 只在两件事上发力:① 把规则算出的档位翻译成"护城河叙事"(为什么这家是 3 档而非 2 档),② 校核证据原文是否真的支持该档位(防规则误判)。
- **目标**:在 Phase 0 结束前(09-06)给出 **5 维评分 + 证据回链 + LLM 语义注释** 的最小可复用 prompt 模板,供 Phase 1 直接接 5-10 家头部公司跑通。
- **现状**(2026-08-31):4 项中 **1/4**(T1 财报速读)落地 → 今日补 **2/4**(T2 护城河评估),剩 T3 对标匹配 + T4 事件归因。

## 2. T2 在 4 类任务中的位置

| 项 | T1 财报速读 | **T2 护城河评估** | T3 对标匹配 | T4 事件归因 |
|---|---|---|---|---|
| LLM 角色 | 主导 | **辅(语义注释 + 证据校核)** | 中(行业聚类后做"为什么可比"解释) | 主导 |
| 输入主源 | pdfplumber JSON | **5 年财务指标 JSON + 规则引擎预评分** | 目标公司 + 38 家种子清单 | 近 5 年公告/新闻片段 |
| 期望输出 | 4 段摘要 + 同比 | **5 维 D1-D5 档位 + LLM 叙事 + Evidence Anchor 校核** | 5-10 家可比公司 + 多维对标表 | 关键事件 + 因果链 |
| 状态 | ✅ v0.1 (08-29) | **🚧 v0.1 (08-31,本文)** | ⏳ pending | ⏳ pending |

## 3. 输入契约

### 3.1 输入 JSON(两段:量化数据 + 规则引擎预评分)

```jsonc
{
  "company": "<公司名,如 贵州茅台>",
  "ticker": "<600519.SH / 00700.HK / AAPL 等>",
  "industry": "<申万二级,如 白酒>",
  "period": "<评估期,如 2020-2024>",
  "metrics": {
    // —— D1 毛利率稳定性 ——
    "D1_gross_margin": {
      "yearly": [52.3, 53.1, 51.8, 54.0, 53.6],   // 5 年毛利率(%)
      "mean": 52.96,
      "std": 0.85                                 // 标准差(pp)
    },
    // —— D2 ROIC / 资本回报 ——
    "D2_roic": {
      "yearly": [28.5, 30.1, 29.4, 32.0, 33.2],   // 5 年 ROIC(%)
      "mean": 30.64,
      "std": 1.86
    },
    // —— D3 客户/订单集中度 ——
    "D3_customer_concentration": {
      "top5_revenue_pct": 8.5,                     // 前 5 大客户营收占比(%)
      "top1_revenue_pct": 2.1,                     // 第 1 大客户占比
      "related_party_pct": 0.0
    },
    // —— D4 技术专利与研发 ——
    "D4_tech_rd": {
      "invention_patents_total": 142,              // 累计发明专利数
      "rd_expense_ratio": {"yearly": [1.8, 2.0, 2.1, 2.3, 2.5], "mean": 2.14},  // 研发费用率(%)
      "rd_headcount_ratio": 12.5                   // 研发人员占比(%)
    },
    // —— D5 牌照与监管壁垒 ——
    "D5_license": {
      "items": [
        {"name": "白酒生产许可证", "type": "行业准入", "expiry": "2030-12-31"},
        {"name": "地理标志保护(茅台镇)", "type": "地理标志", "expiry": null}
      ],
      "count_total": 2,
      "exclusive_count": 1
    }
  },
  "rule_pre_scores": {                            // 规则引擎预跑(Phase 1 落地,Phase 0 留空对象 {})
    "D1": null, "D2": null, "D3": null, "D4": null, "D5": null
  },
  "raw_evidence_pool": [                          // 候选证据池(年报/公告原文片段)
    {
      "source": "annual_report_2024",
      "page": 87,
      "text": "近 5 年综合毛利率分别为 52.3%、53.1%、51.8%、54.0%、53.6%,保持稳定"
    },
    {
      "source": "annual_report_2023",
      "page": 12,
      "text": "前五大客户销售合计占年度销售总额的 8.5%,无单一客户占比超过 3%"
    }
  ]
}
```

### 3.2 数据源契约(Phase 1 落地)

| 字段 | 数据源 |
|---|---|
| `metrics.D1_gross_margin` | 恒生聚源 `FinancialStatement` 5 年时间窗 |
| `metrics.D2_roic` | 恒生聚源 `FinancialAnalysis.ROIC` 5 年 |
| `metrics.D3_customer_concentration` | 年报"主要客户"节 + 关联交易披露 |
| `metrics.D4_tech_rd` | 恒生聚源 `PatentAnnualStatistics` + 年报"研发投入"节 |
| `metrics.D5_license` | 公司画像 `License` 字段(自维护)+ 国家企业信用信息公示系统 |

> **Phase 0 真实场景约束**:种子清单前 5 家头部公司的 5 年指标在 08-30 cron 断档时未批量回填,本期先用 1 家样例(贵州茅台)做 prompt 联调;批量回测放到 Phase 0 收口前。

## 4. Prompt 模板(两段式:规则算分 → LLM 注释)

> **设计要点**:Phase 0 的 LLM **不直接打分**,只做"叙事 + 校核"——避免 LLM 在 5 维量化指标上"幻觉打分"。

### 4.1 Prompt A — 5 维档位计算(规则引擎,非 LLM,仅留契约)

> 本步骤在 Phase 1 由 Python 规则引擎执行(`scripts/moat_rule_engine.py` 待落地),不在 LLM 侧。契约写下来保证 LLM 收到的是已对齐护城河 schema 的输入。

| 维度 | 4 档(优秀) | 3 档(良好) | 2 档(一般) | 1 档(弱) |
|---|---|---|---|---|
| **D1 毛利率稳定性** | 5 年均值 ≥ 50% **且** σ ≤ 3pp | 5 年均值 30-50% **或** σ ≤ 5pp | 5 年均值 15-30% **或** σ 5-8pp | 5 年均值 < 15% **或** σ > 8pp |
| **D2 ROIC** | 5 年均值 ≥ 20% **且** σ ≤ 3pp | 5 年均值 10-20% **或** σ ≤ 5pp | 5 年均值 5-10% **或** σ 5-8pp | 5 年均值 < 5% **或** σ > 8pp |
| **D3 客户集中度** | Top5 ≤ 15% **且** Top1 ≤ 5% | Top5 15-30% **或** Top1 5-10% | Top5 30-50% **或** Top1 10-20% | Top5 > 50% **或** Top1 > 20% |
| **D4 技术专利与研发** | 发明专利 ≥ 100 **且** 研发费用率 ≥ 3% **且** 研发人员占比 ≥ 10% | 发明专利 30-100 **或** 研发费用率 1.5-3% **或** 研发人员 5-10% | 发明专利 10-30 **或** 研发费用率 0.5-1.5% | 发明专利 < 10 **且** 研发费用率 < 0.5% |
| **D5 牌照与监管壁垒** | 独占性牌照 ≥ 1 **且** 牌照总数 ≥ 3 | 独占性牌照 ≥ 1 **或** 行业准入 ≥ 1 | 仅一般行业资质 ≥ 2 | 无显著牌照 |

**档位→原始分**:D_i 原始分 = 档位 × 5(满分 20,5 维等权)
**总分** = Σ D_i,满分 100
**moat_type** 按护城河 schema §3 映射:80-100=deep / 60-79=moderate / 40-59=narrow / 20-39=none / 0-19=negative

### 4.2 Prompt B — LLM 语义注释 + 证据校核(给 Claude / GPT-4o)

```
你是资深卖方分析师助手。给定一份公司的 5 维护城河量化评分结果(规则引擎已算好档位),请完成两件事:
1) 为每个维度写 1 句话"叙事注释"(用证据池原文,说明为什么是这个档位)
2) 校核规则引擎的档位判断是否被证据支持(若 evidence 缺失或反向证据存在,允许下调 1 档)

## 输入
- 公司: <company>
- 行业: <industry>
- 评估期: <period>
- 量化指标(5 年): <metrics>
- 规则预评分(可能为空对象,Phase 0 占位): <rule_pre_scores>
- 候选证据池: <raw_evidence_pool 列表,每条含 source/page/text>

## 输出(JSON,严格遵循 schema,不要多余字段)
{
  "company": "<公司名>",
  "ticker": "<ticker>",
  "industry": "<行业>",
  "period": "<评估期>",
  "dimensions": [
    {
      "dimension": "D1",
      "rule_score": <1|2|3|4>,                // 规则引擎给的档位
      "llm_confirmed": <true|false>,          // LLM 校核是否确认
      "llm_override_score": <1|2|3|4|null>,   // 仅在 llm_confirmed=false 时填,允许下调 1 档
      "narrative": "<1 句话叙事,≤ 80 字,中文,基于证据>",
      "evidence": [
        {
          "source": "<如 annual_report_2024>",
          "page": <int|null>,
          "quote": "<证据原文,≤ 80 字,从 raw_evidence_pool 复制,不允许编造>",
          "url": "<原文链接/本地路径,可空>"
        }
      ]
    },
    ...   // 共 5 项 D1-D5,顺序固定
  ],
  "total": <int,0-100,= Σ(最终档位 × 5)>,
  "moat_type": "deep | moderate | narrow | none | negative",
  "moat_narrative": "<2-3 句话总体护城河叙事,基于 5 维结构,中文>",
  "limitations": ["<本评估的局限 1>", ...],   // 1-3 条,如 "D5 牌照清单自维护,可能不全"
  "confidence": "high | medium | low",
  "version": "moat-llm-v0.1"
}

## 约束
- 严格基于 raw_evidence_pool,evidence.quote 必须从 pool.text 复制,不允许编造或意译
- llm_override_score 仅在 evidence 明确反向时使用,且仅允许下调 1 档(不允许上调)
- narrative 中数字必须能从 metrics 字段验证
- limitations 必须至少 1 条,提示本次评估的盲点
- 中文输出,标点用全角
- rule_score 为 null(Phase 0 占位)时,llm 暂退化为"基于 metrics 自行给档位",但仍需在 limitations 中说明"未走规则引擎,档位仅 LLM 估计"
```

### 4.3 两段流程示意

```
[年报/公告] → 恒生聚源 + 自维护 → metrics JSON
                                  ↓
                          [规则引擎] → rule_pre_scores(D1-D5 档位)
                                  ↓
                  metrics + rule_pre_scores + raw_evidence_pool
                                  ↓
                               [LLM]
                                  ↓
                  LLM 注释 + 校核 → 最终 dimensions[] + total + moat_type
```

## 5. 输出契约(JSON Schema,Pydantic,引用护城河 schema §6)

```python
from pydantic import BaseModel, Field
from typing import Literal

class Evidence(BaseModel):
    source: str = Field(..., description="数据源标识,如 annual_report_2024")
    page: int | None = Field(None, description="PDF 页码,None=非 PDF 源")
    quote: str = Field(..., min_length=5, max_length=80, description="证据原文,必须从 pool 复制")
    url: str | None = Field(None, description="原文链接/本地路径")

class DimensionLLM(BaseModel):
    dimension: Literal["D1", "D2", "D3", "D4", "D5"]
    rule_score: Literal[1, 2, 3, 4] | None = Field(None, description="规则引擎档位,Phase 0 可空")
    llm_confirmed: bool
    llm_override_score: Literal[1, 2, 3, 4] | None = Field(None, description="仅在 llm_confirmed=false 时填")
    narrative: str = Field(..., min_length=8, max_length=80)
    evidence: list[Evidence] = Field(..., min_length=1, max_length=3)

    @property
    def final_score(self) -> int:
        return self.llm_override_score if self.llm_confirmed is False and self.llm_override_score else self.rule_score

class MoatLLMReport(BaseModel):
    company: str
    ticker: str
    industry: str
    period: str
    dimensions: list[DimensionLLM] = Field(..., min_length=5, max_length=5)
    total: int = Field(..., ge=0, le=100)
    moat_type: Literal["deep", "moderate", "narrow", "none", "negative"]
    moat_narrative: str = Field(..., min_length=20, max_length=200)
    limitations: list[str] = Field(..., min_length=1, max_length=3)
    confidence: Literal["high", "medium", "low"]
    version: str = "moat-llm-v0.1"
```

> **关键继承**:`Evidence` / `MoatReport` 字段与护城河 schema §6 严格对齐,只在每维增加 `rule_score` / `llm_confirmed` / `llm_override_score` / `narrative` 4 个 LLM 侧字段,保证 Phase 1 规则引擎跑出来的结果可与 LLM 注释结果合并为同一 JSON。

## 6. 4 档评分校准标准(在护城河 schema §4 之上叠加 LLM 维度)

| 档位 | 含义 | LLM 校核通过条件 |
|---|---|---|
| 4 = **完全可用** | 规则档位 + LLM 叙事 + 证据回链全部对齐,无 hallucination | `llm_confirmed=true`;evidence 全部可在 pool 中定位;narrative 数字与 metrics 一致 |
| 3 = **基本可用** | 规则档位合理,LLM 叙事合理但 evidence 略泛化(quote 较长或跨段拼接) | `llm_confirmed=true`;evidence 存在但允许轻微意译;数字一致 |
| 2 = **可参考** | 规则档位 1 处偏差 / LLM 主动下调 1 档 / evidence 池缺失 1 维 | `llm_override_score` 非空且 ≤ rule_score;evidence 缺失维有 limitations 说明 |
| 1 = **不可用** | LLM 幻觉 / 严重偏离护城河 schema / JSON 字段缺失 | 数字与 metrics 不符;evidence 在 pool 找不到;moat_type 与 total 不匹配(80+ 不是 deep) |

**Phase 0 收口标准**:至少 1 个模型在 5 份样例(种子清单前 5 家)上**平均 ≥ 3 档**,且 `llm_confirmed=true` 占比 ≥ 60%(LLM 不轻易否决规则)。

## 7. 验证步骤(本地最小闭环)

1. 准备 1 家样例(贵州茅台 600519.SH)2020-2024 五年 metrics JSON + raw_evidence_pool(从年报摘 3-5 段原文)
2. 跑规则引擎(Phase 0 可手工对照 §4.1 档位表,Phase 1 再写 `scripts/moat_rule_engine.py`)得出 rule_pre_scores
3. 把 metrics + rule_pre_scores + raw_evidence_pool 喂给 LLM(Claude Sonnet 4 / Qwen-Finance / GPT-4o 任选),得 §5 MoatLLMReport
4. 用 §6 4 档标尺人工盲评
5. 写报告:`Inspiration/LLM基线/03-护城河基线报告.md`(Phase 0 收口时落地)
6. Phase 0 收口前(09-06)扩到种子清单前 5 家批量回测,出基线报告

## 8. 不做(本期边界)

- **不写规则引擎代码**(本期只定义契约,Phase 1 再落地 `scripts/moat_rule_engine.py`;Phase 0 用手工对照档位表联调 LLM)
- **不做模型对比基准**(本设计稿只跑 1 个模型做联调,Claude vs Qwen-Finance vs GPT-4o 对比放到 Phase 1)
- **不做跨市场可比**(护城河 schema §7 已声明,本设计稿不破边界)
- **不接 RAG**(纯 metrics + raw_evidence_pool 输入,无外部知识)
- **不评估 LLM 主导打分**(本设计稿明确 LLM 只注释 + 校核,不替代规则打分;避免在量化指标上幻觉)

## 9. 变更记录

| 日期 | 版本 | 变更 |
|---|---|---|
| 2026-08-31 | v0.1 | 初稿:两段式契约(规则打分 + LLM 注释) + 5 维输入 JSON 模板 + Prompt A 档位表 + Prompt B 注释/校核模板 + Pydantic schema(继承护城河 schema) + 4 档校准 + 验证步骤 |

## 10. 关联文档

- [01-4类LLM任务基线设计稿.md §2(4 类任务一览 T2 行)](./01-4类LLM任务基线设计稿.md) — 父设计稿,T2 在 4 类任务中的位置
- [../护城河/01-护城河评分schema设计稿.md](../护城河/01-护城河评分schema设计稿.md) — Schema 锚点,本设计稿严格继承
- [项目开发计划.md §5 Phase 0 第 4 项](../../项目开发计划.md) — 本任务对应主计划
- [公司顾问开发架构与计划.md §3 核心功能(护城河评估模块)](../../公司顾问开发架构与计划.md)
- [../公司/01-种子公司清单.md](../公司/01-种子公司清单.md) — Phase 0 收口时 5 份样例的取样源
- 后续:Phase 0 收口前落地 `Inspiration/LLM基线/03-护城河基线报告.md`(批量回测 + 4 档评分)
