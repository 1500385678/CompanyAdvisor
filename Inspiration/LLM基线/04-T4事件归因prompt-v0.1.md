# T4 事件归因 Prompt v0.1

> **入库日期**:2026-09-02
> **对应主计划**:[项目开发计划.md §5 Phase 0 第 4 项(LLM 4 类任务基线 #4)](../../项目开发计划.md)
> **父设计稿**:[01-4类LLM任务基线设计稿.md §2(4 类任务一览 T4 行)](./01-4类LLM任务基线设计稿.md)
> **Schema 锚点**:
> - 证据回链复用:[../护城河/01-护城河评分schema设计稿.md §5 Evidence Anchor](../护城河/01-护城河评分schema设计稿.md)
> - 影响维度对齐:同源 schema §2(护城河 5 维 D1-D5)
> **姊妹篇**:
> - [02-T2护城河评估prompt-v0.1.md](./02-T2护城河评估prompt-v0.1.md)(T2 评估的"事件冲击"可作为 T4 素材)
> - [03-T3对标匹配prompt-v0.1.md](./03-T3对标匹配prompt-v0.1.md)(同公司对标组事件可横向对比)
> **种子清单**:[../公司/01-种子公司清单.md](../公司/01-种子公司清单.md)(38 家 · 8 行业)
> **状态**:**设计稿**(尚需 1)种子清单 5 家头部公司 5 年公告批量回测,2)飞书 P0 用户盲评校准"因果链"叙事合理性)
> **维护**:22-公司-Company 行业顾问

---

## 1. 背景与目标

- **来源**:T1 设计稿 §2 表第 4 行 T4 事件归因,落地计划"事件抽取 + 因果链"两段 prompt。
- **核心定位(与 T1/T2/T3 的差异)**:
  - T1 = LLM 主导(阅读理解 + 摘要,从单份 PDF)
  - T2 = 规则主导 + LLM 辅(语义注释,5 维量化评分)
  - T3 = 规则聚类 + LLM 解释(中权重,选 Top-K + 叙事)
  - **T4 = LLM 主导**(信息抽取 + 归因推理,从多份异构素材)
  - 原因:事件抽取是"无固定模板"的开放任务(公告/新闻/研报格式各异),规则难穷举;LLM 在两类事上发力:① 从非结构化文本中识别"是什么事件、什么时间、影响什么",② 在事件间建立因果链(A 导致 B,B 进一步影响 C),这是 LLM 推理的强项。
- **目标**:在 Phase 0 结束前(09-06)给出 **事件抽取 + 影响标注 + 因果链推理** 的最小可复用 prompt 模板,供 Phase 1 直接接 5-10 家头部公司跑通"事件时间线"模块。
- **现状**(2026-09-02):4 项中 **3/4**(T1+T2+T3)落地 → 今日补 **4/4**(T4 事件归因),**§5 #4 整段可勾选闭合**。

---

## 2. T4 在 4 类任务中的位置

| 项 | T1 财报速读 | T2 护城河评估 | T3 对标匹配 | **T4 事件归因** |
|---|---|---|---|---|
| LLM 角色 | 主导 | 辅(注释 + 校核) | 中(行业聚类后解释) | **主导(抽取 + 因果推理)** |
| 输入主源 | pdfplumber JSON(单份 PDF) | 5 年财务指标 JSON + 规则预评分 | 目标公司 + 38 家种子清单 | **近 5 年公告/新闻/研报片段(多源异构)** |
| 期望输出 | 4 段摘要 + 同比 | 5 维 D1-D5 档位 + LLM 叙事 + 证据回链 | 5-10 家可比公司 + 多维对标表 | **关键事件列表(类型/时间/影响) + 因果链** |
| 字段锚点 | 自有 schema | 护城河 schema §6(Pydantic) | 继承护城河 `target` 字段 | **继承护城河 `Evidence` + 5 维 `impact_dimensions`** |
| 状态 | ✅ v0.1 (08-29) | ✅ v0.1 (08-31) | ✅ v0.1 (09-01) | **🚧 v0.1 (09-02,本文)** |

---

## 3. 输入契约

### 3.1 输入 JSON(三段:目标公司 + 事件素材池 + 已知护城河画像)

```jsonc
{
  "target": {
    "company": "<公司名,如 贵州茅台>",
    "ticker": "<600519.SH / 00700.HK / AAPL 等>",
    "industry_sw_l2": "<申万二级,如 白酒>",
    "period": "<评估期,如 2020-2024>",
    "moat_hint": {                                   // 可选,来自 T2 输出;无则 null
      "moat_type": "deep",
      "weak_dimensions": ["D3"]                      // 弱项维度,影响"事件关注度"优先级
    }
  },
  "event_corpus": [                                  // 规则引擎预筛的近 5 年事件素材(公告/新闻/研报)
    {
      "doc_id": "evt_001",
      "source": "announcement",                      // 公告 / news(新闻) / research(研报) / social(社交媒体)
      "title": "<标题,如 关于回购公司股份方案的公告>",
      "publish_date": "2024-03-15",
      "url": "<原文链接或本地路径,如 samples/announce_2024_03_15.pdf>",
      "page": 1,                                     // 可选,PDF 页码
      "text": "<原文片段,≤ 500 字,关键段落提取>"
    },
    {
      "doc_id": "evt_002",
      "source": "news",
      "title": "茅台经销商大会释放提价信号",
      "publish_date": "2024-01-20",
      "url": "https://news.example.com/2024/01/20/xxx",
      "text": "在 1 月 18 日经销商大会上,公司表示..."
    },
    ...   // 通常 30-100 条素材,去重 + 时间排序后由 §4.1 规则引擎输出
  ],
  "options": {
    "min_events": 8,                                 // 期望最少事件数
    "max_events": 20,                                // 期望最多事件数
    "min_chains": 1,                                 // 最少因果链数
    "max_chains": 3,                                 // 最多因果链数(防过度归因)
    "date_window_years": 5                           // 时间窗,默认 5 年
  }
}
```

### 3.2 数据源契约(Phase 1 落地)

| 字段 | 数据源 |
|---|---|
| `target.industry_sw_l2` | 恒生聚源 `StockBelongIndustry` |
| `target.moat_hint` | T2 护城河评估输出(`MoatLLMReport` JSON) |
| `event_corpus[]` 公告 | 恒生聚源 `AShareAnnouncement` + `HKStockAnnouncement`(5 年) |
| `event_corpus[]` 新闻 | 全网舆情 `NewsInfoList` 关键词过滤(公司全称 + 简称 + ticker) |
| `event_corpus[]` 研报 | 恒生聚源 `ResearchReport` 按公司 + 5 年窗口 |
| `event_corpus[].text` | 公告/新闻/研报"原文片段",由 §4.1 规则引擎做去重 + 截断 |

> **Phase 0 真实场景约束**:本期用 1 家样例(贵州茅台)+ 模拟 5-8 条事件素材做 prompt 联调,Phase 0 收口前(09-06)扩到种子清单前 5 家批量回测。

---

## 4. Prompt 模板(两段式:规则预处理 → LLM 抽取 + 因果推理)

> **设计要点**:LLM 拿到的素材是**已去重 / 已时间排序 / 已截断**的精修输入,避免在长文里"漏事件"或"重复抽";LLM 主攻"事件是什么 + 影响什么 + 因果链",不重复造轮子。

### 4.1 Prompt A — 素材预处理(规则引擎,非 LLM,仅留契约)

> 本步骤在 Phase 1 由 Python 规则引擎执行(`scripts/event_corpus_preprocess.py` 待落地),不在 LLM 侧。契约写下来保证 LLM 收到的是已对齐的精修输入。

| 处理维度 | 规则 | 备注 |
|---|---|---|
| **去重** | 同标题 + 同 publish_date 合并为 1 条,保留信息密度最高版本 | 同一事件多家媒体报道,合并为 1 |
| **时间窗** | 仅保留 `publish_date` 距今 ≤ `date_window_years` 的素材 | 默认 5 年 |
| **正文截断** | 每条 `text` 截断到 500 字,优先保留"事件核心"段(去头去尾) | 公告通常 1000-3000 字,必须截 |
| **来源优先级** | 公告 > 研报 > 权威媒体(财新/路透/彭博)> 自媒体 | 用于多源去重时,优先保留高优先级源 |
| **噪音过滤** | 关键词排除:招股书模板段、封面页、目录、致谢 | 规则黑名单 ~30 个,Phase 1 维护 |
| **事件候选预筛** | 关键词命中"收购/回购/分红/减持/中标/中标/许可/诉讼/新品/任命/业绩预告/亏损/重组/分拆/上市"等 ≥ 1 个的素材入池 | 软约束,LLM 可从非命中文本抽事件 |

**规则引擎输出**:`event_corpus[]` 通常 30-100 条,LLM 从中识别 8-20 个有效事件。

### 4.2 事件类型枚举(8 类,与公司顾问开发架构 §3 核心功能对齐)

| 类型 code | 中文 | 示例 |
|---|---|---|
| `funding` | 融资 | IPO / 增发 / 可转债 / 优先股发行 |
| `ma` | 并购重组 | 收购 / 出售 / 合并 / 分拆 / 借壳 |
| `management` | 管理层变动 | CEO/CFO/董事长/独董变更 · 实控人变更 |
| `litigation` | 诉讼仲裁 | 重大诉讼 · 仲裁 · 处罚 · 调查 |
| `product` | 产品/技术 | 新品发布 · 技术突破 · 专利诉讼 |
| `contract` | 重大合同 | 中标 · 长单 · 战略合作 · 框架协议 |
| `regulatory` | 监管/合规 | 政策变化 · 行业准入 · 牌照获取/吊销 |
| `earnings_pivot` | 业绩拐点 | 业绩预告 · 重大亏损 · 营收/利润 ±20% 波动 |

> **边界说明**:`earnings_pivot` 专指"单期业绩突变"型事件;常规业绩公告走 T1 财报速读,不在 T4 重复抽取。

### 4.3 Prompt B — LLM 事件抽取 + 因果链推理(给 Claude / GPT-4o)

```
你是资深卖方分析师助手。给定一家公司近 5 年的事件素材(已去重/排序/截断),请完成三件事:
1) 从素材中识别 8-20 个"关键事件",每条标注类型/时间/影响维度/影响方向/证据回链
2) 在事件间建立 1-3 条"因果链",把孤立的点连成"故事线"
3) 提炼 1-3 个"主题"(这家公司在过去 5 年的主旋律)

## 输入
- 目标公司: <target JSON,含 company/ticker/industry_sw_l2/period/moat_hint>
- 事件素材池: <event_corpus 列表,30-100 条,每条含 doc_id/source/publish_date/text>
- 选项: <options 含 min_events/max_events/min_chains/max_chains>

## 输出(JSON,严格遵循 schema,不要多余字段)
{
  "target": {
    "company": "<公司名>",
    "ticker": "<ticker>",
    "industry_sw_l2": "<申万二级>",
    "period": "<评估期>"
  },
  "events": [
    {
      "event_id": "E001",                            // 顺序编号,固定前缀 E
      "event_type": "funding|ma|management|litigation|product|contract|regulatory|earnings_pivot",
      "event_date": "<YYYY-MM-DD>",
      "title": "<1 句话事件标题,≤ 30 字,中文>",
      "summary": "<2-3 句话事件摘要,中文,≤ 120 字>",
      "impact_dimensions": ["D1", "D3", ...],        // 关联护城河 5 维,可空数组
      "impact_direction": "positive|neutral|negative",
      "magnitude": "high|medium|low",                // 影响幅度,LLM 自评
      "evidence": [
        {
          "source": "<如 announcement_2024_03_15>",
          "doc_id": "<对应 event_corpus.doc_id>",
          "page": <int|null>,                       // PDF 页码,可空
          "quote": "<证据原文,≤ 80 字,从 event_corpus.text 复制,不允许编造>",
          "url": "<原文链接/本地路径>"
        }
      ],
      "confidence": "high|medium|low"
    },
    ...   // 共 8-20 项,按 event_date 升序
  ],
  "causal_chains": [
    {
      "chain_id": "C001",                            // 顺序编号,固定前缀 C
      "chain_title": "<1 句话因果链标题,如 '管理层换帅 → 战略转向 → 业绩反转'>",
      "events": ["E001", "E005", "E012"],            // 引用 event_id,顺序即因果方向
      "rationale": "<2-3 句话因果推理,中文,说明 A 为什么导致 B,基于 evidence>",
      "chain_type": "strategy|financial|governance|external",  // 因果链性质
      "evidence": [
        {
          "source": "<多源,可引用多条 evidence 串联>",
          "doc_id": "<对应 event_corpus.doc_id>",
          "page": <int|null>,
          "quote": "<证据原文,≤ 100 字>",
          "url": "<原文链接/本地路径>"
        }
      ],
      "confidence": "high|medium|low"
    },
    ...   // 共 1-3 条
  ],
  "major_themes": [
    "<主题 1,如 '渠道扁平化改革贯穿 5 年'>",
    "<主题 2>"
  ],                                                // 1-3 条
  "limitations": [
    "<局限 1,如 '素材池仅覆盖公告+新闻,缺研报深度观点'>",
    ...
  ],                                                // 1-3 条
  "confidence": "high|medium|low",
  "version": "event-timeline-v0.1"
}

## 约束
- events[] 必须从 event_corpus 抽取,不允许 LLM 自由编造未在素材中出现的事件
- 每条 event 至少 1 条 evidence,evidence.quote 必须从 event_corpus[].text 复制
- impact_dimensions 关联护城河 5 维(D1-D5),无明确关联时填 []
  - D1 毛利率 → 价格调整、产品结构变化
  - D2 ROIC → 资本运作、并购、分红/回购
  - D3 客户 → 渠道改革、战略合作、大客户协议
  - D4 技术 → 研发投入、专利、新品发布
  - D5 牌照 → 监管、资质、准入
- causal_chains[].events 必须是 events[] 中已存在的 event_id,且按时间先后排列
- causal_chains 数量严格 1-3 条,禁止"所有事件都串一条"或"事件两两配对"
- major_themes 是"故事级"归纳,不能只是事件分类(避免与 event_type 重复)
- limitations 必须至少 1 条,提示素材池覆盖盲点
- 中文输出,标点用全角
- event_date 严格遵循 YYYY-MM-DD,无法精确到日时按月份 1 日兜底且在 summary 中说明
- magnitude 校准:high=单事件能改变护城河 1 维档位 / medium=影响 1-2 年业绩 / low=边际信息
```

### 4.4 两段流程示意

```
[公告/新闻/研报 5 年原始素材]
            ↓
   [规则引擎 §4.1]
   去重 + 时间窗 + 截断 + 来源优先级 + 候选预筛
            ↓
   event_corpus[](30-100 条)
            ↓
   target + event_corpus + options
            ↓
        [LLM §4.3]
            ↓
   events[](8-20) + causal_chains[](1-3) + major_themes[](1-3)
```

---

## 5. 输出契约(JSON Schema,Pydantic,引用护城河 schema §5/§6)

```python
from pydantic import BaseModel, Field
from typing import Literal
from datetime import date

# —— 复用护城河 schema 的 Evidence 模型(对齐字段名)——
class Evidence(BaseModel):
    source: str = Field(..., description="数据源标识,如 announcement_2024_03_15")
    doc_id: str = Field(..., description="对应 event_corpus[].doc_id")
    page: int | None = Field(None, description="PDF 页码,None=非 PDF 源")
    quote: str = Field(..., min_length=5, max_length=100, description="证据原文")
    url: str | None = Field(None, description="原文链接/本地路径")

# —— 事件主体,impact_dimensions 严格对齐护城河 5 维 D1-D5 ——
MoatDimension = Literal["D1", "D2", "D3", "D4", "D5"]
EventType = Literal[
    "funding", "ma", "management", "litigation",
    "product", "contract", "regulatory", "earnings_pivot"
]
ImpactDirection = Literal["positive", "neutral", "negative"]
Magnitude = Literal["high", "medium", "low"]

class EventItem(BaseModel):
    event_id: str = Field(..., pattern=r"^E\d{3,}$", description="E 前缀 + 3 位以上数字")
    event_type: EventType
    event_date: date = Field(..., description="YYYY-MM-DD,精确到日最佳")
    title: str = Field(..., min_length=4, max_length=30)
    summary: str = Field(..., min_length=15, max_length=120)
    impact_dimensions: list[MoatDimension] = Field(default_factory=list, max_length=5)
    impact_direction: ImpactDirection
    magnitude: Magnitude
    evidence: list[Evidence] = Field(..., min_length=1, max_length=3)
    confidence: Literal["high", "medium", "low"]

# —— 因果链,chain_type 解释因果性质 ——
ChainType = Literal["strategy", "financial", "governance", "external"]

class CausalChain(BaseModel):
    chain_id: str = Field(..., pattern=r"^C\d{3,}$")
    chain_title: str = Field(..., min_length=8, max_length=60)
    events: list[str] = Field(..., min_length=2, max_length=5, description="引用 EventItem.event_id")
    rationale: str = Field(..., min_length=20, max_length=200)
    chain_type: ChainType
    evidence: list[Evidence] = Field(..., min_length=1, max_length=5)
    confidence: Literal["high", "medium", "low"]

class EventTimelineReport(BaseModel):
    target: dict = Field(..., description="必含 company/ticker/industry_sw_l2/period")
    events: list[EventItem] = Field(..., min_length=8, max_length=20)
    causal_chains: list[CausalChain] = Field(..., min_length=1, max_length=3)
    major_themes: list[str] = Field(..., min_length=1, max_length=3)
    limitations: list[str] = Field(..., min_length=1, max_length=3)
    confidence: Literal["high", "medium", "low"]
    version: str = "event-timeline-v0.1"

    @property
    def event_count(self) -> int:
        return len(self.events)

    @property
    def chain_count(self) -> int:
        return len(self.causal_chains)
```

> **关键继承**(与护城河 schema 字段对齐):
>
> - `Evidence` 模型字段与护城河 schema §6 完全一致(`source/page/quote/url`),**新增 `doc_id` 字段** 用于回链到 event_corpus
> - `impact_dimensions` 严格使用护城河 5 维 D1-D5,便于 Phase 1 把 T4 输出叠加到 T2 护城河评估上(同一事件冲击 → 对应维度档位调整)
> - `confidence` 三档体系与 T1/T2/T3 对齐(high/medium/low)

---

## 6. 4 档评分校准标准

| 档位 | 含义 | 通过条件 |
|---|---|---|
| 4 = **完全可用** | 事件抽取全 + 类型准确 + 影响维度合理 + 因果链有真实证据 + 主题有信息量 | events 8-20 项、全部在素材池内;impact_dimensions 至少 50% 命中;causal_chains 1-3 条,events 引用全合法;evidence.quote 可在原文中定位 |
| 3 = **基本可用** | 事件抽取基本全 + 类型大致准 + 因果链合理但 evidence 略泛化 | events ≥ 8;允许 1-2 处类型误判(可上调/下调);causal_chains rationale 合理;limitations 存在 |
| 2 = **可参考** | 事件漏 2-3 个明显该抽的 / 因果链 evidence 引用错误 / 影响维度有编造 | events < 8 或 > 20;causal_chains 含不在 events 中的 id;magnitude 与实际影响明显不符 |
| 1 = **不可用** | 大量编造事件 / 因果链完全虚构 / evidence 找不到原文 / JSON schema 破 | events 含素材池外事件(致命);causal_chains 全凭想象;字段缺失或乱码;events < 5 或 > 25 |

**Phase 0 收口标准**:至少 1 个模型在 5 份样例(种子清单前 5 家)上**平均 ≥ 3 档**,且:
- events 全部命中 event_corpus(池外事件 = 0)
- causal_chains[].events 引用全合法(无悬空 id)
- impact_dimensions 至少 50% 命中 D1-D5 实际关联

---

## 7. 验证步骤(本地最小闭环)

1. 准备 1 家样例(贵州茅台 600519.SH)+ 模拟 5-8 条事件素材(覆盖 2-3 种 event_type,含 1 条可串成因果链的事件组)
2. 跑规则引擎(Phase 0 可手工对照 §4.1 过滤表,Phase 1 再写 `scripts/event_corpus_preprocess.py`)筛出 5-10 条精修素材
3. 把 target + event_corpus + options 喂给 LLM(Claude Sonnet 4 / Qwen-Finance / GPT-4o 任选),得 §5 EventTimelineReport
4. 用 §6 4 档标尺人工盲评(重点看:① 事件抽取是否漏掉"明显该有的"如管理层变动,② 因果链 rationale 是否有信息量,③ 影响维度是否合理)
5. 写报告:`Inspiration/LLM基线/05-事件归因基线报告.md`(Phase 0 收口时落地)
6. Phase 0 收口前(09-06)扩到种子清单前 5 家批量回测,出基线报告

---

## 8. 不做(本期边界)

- **不写规则引擎代码**(本期只定义契约,Phase 1 再落地 `scripts/event_corpus_preprocess.py`;Phase 0 用手工对照过滤表联调 LLM)
- **不做模型对比基准**(本设计稿只跑 1 个模型做联调,Claude vs Qwen-Finance vs GPT-4o 对比放到 Phase 1)
- **不接 RAG**(纯 event_corpus 输入,无外部实时新闻检索;Phase 1 事件时间线模块可接 Milvus 公告全文 RAG)
- **不做多语言**(本设计稿只服务中文公告 + 中文新闻;英文 10-K/8-K 在 Phase 2 单独建契约)
- **不做实时事件流**(只评估过去 5 年已发生事件,不预测未来,不订阅实时新闻)
- **不做情绪分析**(本设计稿只抽取"发生了什么"+"影响什么",不做市场情绪打分;情绪分析是 Phase 2 单独任务)
- **不做事件聚类去重**(同一事件多家媒体报,Phase 1 由规则引擎合并;LLM 收到的是已合并素材)
- **不评估长因果链**(`causal_chains[].events` 上限 5 个 event_id,避免 LLM 强行"穿凿"远距离因果)

---

## 9. 变更记录

| 日期 | 版本 | 变更 |
|---|---|---|
| 2026-09-02 | v0.1 | 初稿:两段式契约(规则预处理 + LLM 抽取/归因) + 目标+事件素材池+moat_hint 输入 JSON 模板 + 8 类事件类型枚举 + Prompt A 过滤表 + Prompt B 抽取+因果链模板 + Pydantic schema(Evidence 复用护城河 + impact_dimensions 关联 D1-D5) + 4 档校准 + 验证步骤 |

---

## 10. 关联文档

- [01-4类LLM任务基线设计稿.md §2(4 类任务一览 T4 行)](./01-4类LLM任务基线设计稿.md) — 父设计稿,T4 在 4 类任务中的位置
- [02-T2护城河评估prompt-v0.1.md](./02-T2护城河评估prompt-v0.1.md) — 姊妹篇,T2 的 `moat_hint` 字段是 T4 的可选输入
- [03-T3对标匹配prompt-v0.1.md](./03-T3对标匹配prompt-v0.1.md) — 姊妹篇,同公司对标组事件可横向对比
- [../护城河/01-护城河评分schema设计稿.md §2/§5/§6](../护城河/01-护城河评分schema设计稿.md) — Evidence 模型 + 5 维 D1-D5 字段来源
- [../公司/01-种子公司清单.md](../公司/01-种子公司清单.md) — 5 份样例公告的取样源
- [项目开发计划.md §5 Phase 0 第 4 项](../../项目开发计划.md) — 本任务对应主计划(**§5 #4 整段可勾选闭合**)
- [项目开发计划.md §3 核心功能(事件时间线模块)](../../项目开发计划.md)
- [公司顾问开发架构与计划.md §3 核心功能(事件时间线)](../../公司顾问开发架构与计划.md)
- 后续:Phase 0 收口前落地 `Inspiration/LLM基线/05-事件归因基线报告.md`(批量回测 + 4 档评分)
