# 护城河评分 Schema 设计稿(v0.1)

> 对应项目开发计划 §5 Phase 0 第 5 项 · 落地日期 2026-08-28
> 状态:**设计稿**(尚需种子 5 家头部公司盲评校准 + 飞书 P0 用户小范围反馈)
> 维护:22-公司-Company 行业顾问

## 1. 背景

- **来源**:公司顾问开发架构与计划 §3(护城河评估:5 维度评分 + 证据回链)
- **目标**:把"护城河"从主观印象转为可计算、可回链的结构化评分,支撑"公司画像"面板的"护城河"卡片
- **差异化**:评分不是"高/中/低"标签,而是 **5 维加权分数 + 每维证据原文回链 + 总体护城河类型分类**

## 2. 5 维评分维度

| # | 维度 | 核心问题 | 数据源(Phase 1) | 满分 |
|---|---|---|---|---|
| D1 | **毛利率稳定性** | 多年毛利率均值 + 标准差,反映定价权 | 恒生聚源 `FinancialStatement` + 5 年时间窗 | 20 |
| D2 | **ROIC / 资本回报** | 投入资本回报率,反映资本效率 | 恒生聚源 `FinancialAnalysis.ROIC` + 5 年 | 20 |
| D3 | **客户/订单集中度** | 前 5 大客户占比、Top10 收入贡献,反映议价权 | 年报"主要客户"节 + 关联交易披露 | 20 |
| D4 | **技术专利与研发** | 发明专利数、研发费用率、研发人员占比,反映技术壁垒 | 恒生聚源 `PatentAnnualStatistics` + 年报研发节 | 20 |
| D5 | **牌照与监管壁垒** | 行业准入牌照、特许经营、政府特许,反映准入门槛 | 公司画像 `License` 字段(自维护) | 20 |

**总分** = Σ D_i · 满分 100

## 3. 护城河类型分类(基于总分 + 维度结构)

| 总分区间 | 护城河类型 | 视觉标识 |
|---|---|---|
| 80-100 | **深护城河**(Strong Moat) | 🟢🟢🟢 |
| 60-79 | **中等护城河**(Moderate Moat) | 🟢🟢 |
| 40-59 | **浅护城河**(Narrow Moat) | 🟢 |
| 20-39 | **无显著护城河**(No Moat) | ⚪ |
| 0-19 | **负护城河**(负向信号,如毛利下滑) | 🔴 |

**类型细粒度**(用于 Phase 2):

- 毛利型(Moat 主导在 D1):高毛利 + 稳定 → 品牌/规模/定价权
- 资本型(D2 主导):高 ROIC → 轻资产/网络效应
- 客户型(D3 主导,占比低得高分):客户分散 → 不可替代
- 技术型(D4 主导):专利+研发 → 技术壁垒
- 牌照型(D5 主导):准入 → 监管壁垒

## 4. 评分等级(每维内部)

每维独立打分,统一使用 4 档:

| 档位 | 含义 | 区间示意(以 D1 毛利率稳定性为例) |
|---|---|---|
| 4 | 优秀 | 5 年均值 ≥ 50% 且 σ ≤ 3pp |
| 3 | 良好 | 5 年均值 30-50% 或 σ ≤ 5pp |
| 2 | 一般 | 5 年均值 15-30% 或 σ 5-8pp |
| 1 | 弱 | 5 年均值 < 15% 或 σ > 8pp |

**原始分 = 档位 × 维度权重**(例:D1=4 → 4 × 5 = 20 = 满分)

## 5. 证据回链(Evidence Anchor)契约

每一条评分必须挂 **至少 1 条证据原文**,JSON 字段:

```json
{
  "dimension": "D1",
  "score": 4,
  "evidence": [
    {
      "source": "annual_report_2024",
      "page": 87,
      "quote": "近 5 年综合毛利率分别为 52.3%、53.1%、51.8%、54.0%、53.6%,保持稳定",
      "url": "samples/_sample-fy2024.pdf#page=87"
    }
  ],
  "evaluated_at": "2026-08-28T03:30:00+08:00",
  "evaluator": "rule-v0.1"   // 或 "llm:claude-sonnet-4"
}
```

- **Phase 1**:用规则引擎跑(数据驱动,够稳)
- **Phase 2**:可叠加 LLM 评分(语义理解更强),两者结果不一致时双标注,UI 暴露给用户看

## 6. JSON Schema(Pydantic 雏形,Phase 1 落地)

```python
from pydantic import BaseModel, Field
from typing import Literal

class Evidence(BaseModel):
    source: str = Field(..., description="数据源标识,如 annual_report_2024")
    page: int | None = Field(None, description="PDF 页码,None=非 PDF 源")
    quote: str = Field(..., min_length=5, description="证据原文")
    url: str | None = Field(None, description="原文链接/本地路径")

class DimensionScore(BaseModel):
    dimension: Literal["D1", "D2", "D3", "D4", "D5"]
    score: Literal[1, 2, 3, 4]
    evidence: list[Evidence] = Field(..., min_length=1)
    evaluated_at: str
    evaluator: str

class MoatReport(BaseModel):
    company: str
    period: str = Field(..., description="评估期,如 2020-2024")
    dimensions: list[DimensionScore] = Field(..., min_length=5, max_length=5)
    total: int = Field(..., ge=0, le=100)
    moat_type: Literal["deep", "moderate", "narrow", "none", "negative"]
    version: str = "moat-v0.1"
```

## 7. 不做(本期边界)

- **不做 LLM 自动评分**(Phase 1 规则,Phase 2 叠加)
- **不做跨市场可比**(Phase 2 引入同行业对标,本设计稿只评估单一公司)
- **不做趋势预测**(只评估过去 5 年,不预测未来 5 年)
- **不做加权微调**(当前 5 维等权 20,后续校准后引入真实权重)

## 8. 变更记录

| 日期 | 版本 | 变更 |
|---|---|---|
| 2026-08-28 | v0.1 | 初稿:5 维(毛利/ROIC/客户/技术/牌照) + 等权 20 + 4 档评分 + Evidence Anchor 契约 + Pydantic schema |

## 9. 关联文档

- [项目开发计划.md §5 Phase 0 #5](../../项目开发计划.md)
- [Inspiration/公司/01-种子公司清单.md](../公司/01-种子公司清单.md)(盲评校准时抽取前 5 家头部)
- [公司顾问开发架构与计划.md §3 核心功能](../../公司顾问开发架构与计划.md)
