# -*- coding: utf-8 -*-
"""
跨行业公司画像 schema · Pydantic 雏形 · v0.1.3
================================================

> 对应主计划:[项目开发计划.md §5 第 6 项](../../项目开发计划.md) - 跨行业顾问对齐
> 状态:**草稿**(等张勇拉 17-生物 / 20-经济 / 23-盈利 3 顾问对齐后,可能升 v0.2)
> 维护:22-公司-Company 行业顾问
> 落地日期:2026-09-12
> 对应章节:Inspiration/跨行业/01-跨行业公司画像字段schema设计稿.md §11
> 不做什么:不对齐(对齐仍由张勇驱动);不勾选 §5 #6 checkbox(对齐未发生)

## 用途
- 把 §2 通用 23 字段 + §3 行业扩展 9 字段 = 32 字段定义翻译为 Pydantic V2 model
- 1 公司示例填值演示(贵州茅台:23 通用字段 + 0 行业扩展)
- v0.2 共识会议前,可让 3 行业直接在 IDE 里看字段类型 + 必填性 + 默认值
- Phase 1 MVP 实施时,直接复制本模块到 `src/schemas/cross_industry.py`

## 字段对照(全部 32 字段)
- §2.1 基本信息(6):name, ticker, market, incorporation_date, hq_country, industry_l1
- §2.2 业务结构(3):business_segments, revenue_breakdown, key_products
- §2.3 财务 5 年(5):revenue_5y, net_profit_5y, gross_margin_5y, roe_5y, debt_ratio_5y
- §2.4 股权与控制(3):top10_shareholders, actual_controller, free_float_ratio
- §2.5 管理层(2):key_management, board_independence
- §2.6 事件 5 年(2):key_events_5y, regulatory_actions_5y
- §2.7 护城河(2):moat_score, moat_type
- §3 行业扩展位(9):pipeline_drugs, clinical_phase, fda_approval, gdp_contribution,
                   policy_sensitivity, employment_scale, unit_economics, ltv_cac_ratio, burn_rate

## 依赖
- pydantic >= 2.0(本机验证 pydantic 2.13.4)
- 运行:`python3 02-跨行业公司画像schema-Pydantic雏形-v0.1.3.py --validate`
"""

import sys
import warnings
from datetime import date as _date
from enum import Enum
from typing import List, Optional, Dict, Any

try:
    from pydantic import BaseModel, Field, field_validator, model_validator
    PYDANTIC_V2 = True
except ImportError as e:  # pragma: no cover
    raise ImportError(
        "pydantic V2 未安装,请先 `pip install pydantic>=2.0`"
    ) from e


# ============================================================================
# §2.1 基本信息(6 字段)
# ============================================================================

class Market(str, Enum):
    """市场枚举 - §5 C7 5 值(A/H/US/新三板/未上市)"""
    A = "A"
    H = "H"
    US = "US"
    NEEQ = "新三板"
    UNLISTED = "未上市"


class IndustryL1(str, Enum):
    """行业一级枚举 - §5 C7 沿用 22-公司种子清单 8 分类"""
    CONSUMER = "消费"
    PHARMA = "医药"
    INTERNET = "互联网"
    NEW_ENERGY = "新能源"
    SEMICONDUCTOR = "半导体"
    FINANCE = "金融"
    AUTO = "汽车"
    MANUFACTURING = "制造"


class BasicInfo(BaseModel):
    """§2.1 基本信息 6 字段"""
    name: str = Field(..., description="公司全称(工商名优先)")
    ticker: Optional[str] = Field(
        None,
        description="市场代码,必须带后缀(600519.SH / 0700.HK / AAPL.US) - §5 C2",
    )
    market: Market = Field(..., description="市场枚举(5 值)")
    incorporation_date: _date = Field(..., description="成立日期(工商口径)")
    hq_country: str = Field(..., description="总部所在国(主总部)")
    industry_l1: IndustryL1 = Field(..., description="行业一级(8 分类) - §5 C7")

    @field_validator("ticker")
    @classmethod
    def _ticker_has_suffix(cls, v: Optional[str]) -> Optional[str]:
        """§5 C2:6 位股票代码必须带后缀(.SH / .SZ / .HK / .US / .OF)"""
        if v is None:
            return v
        valid_suffixes = (".SH", ".SZ", ".HK", ".US", ".OF")
        if not any(v.endswith(s) for s in valid_suffixes):
            raise ValueError(
                f"ticker={v!r} 缺少合法后缀,需为 {valid_suffixes} 之一 - §5 C2"
            )
        return v


# ============================================================================
# §2.2 业务结构(3 字段)
# ============================================================================

class BusinessSegment(BaseModel):
    """单个业务分项 - 收入/毛利/同比"""
    name: str = Field(..., description="业务名称(白酒/家电/...)")
    revenue: float = Field(..., description="收入(亿元) - §5 C1")
    gross_margin: Optional[float] = Field(None, description="毛利率(%) - §5 C3")


class BusinessStructure(BaseModel):
    """§2.2 业务结构 3 字段"""
    business_segments: List[BusinessSegment] = Field(
        default_factory=list,
        description="主营业务分项列表(年报到 §3 业务概况)",
    )
    revenue_breakdown: Dict[str, float] = Field(
        default_factory=dict,
        description="收入按地区 / 产品 / 客户拆分(单位:亿元) - §5 C1",
    )
    key_products: List[str] = Field(
        default_factory=list,
        description="关键产品/服务 1-3 个(去重,字符串)",
    )

    @field_validator("key_products")
    @classmethod
    def _max_3_products(cls, v: List[str]) -> List[str]:
        if len(v) > 5:
            raise ValueError(f"key_products 数量 {len(v)} 超过 5 上限(规范 1-3)")
        return v


# ============================================================================
# §2.3 财务 5 年(5 字段)
# ============================================================================

class Financial5Y(BaseModel):
    """§2.3 财务 5 年 5 字段(单位 + 口径在 §5 C1/C3/C4 强约束)"""
    revenue_5y: List[float] = Field(
        ...,
        min_length=5, max_length=5,
        description="5 年营业收入(亿元) - §5 C1(强单位)",
    )
    net_profit_5y: List[float] = Field(
        ...,
        min_length=5, max_length=5,
        description="5 年归母净利润(亿元) - §5 C1",
    )
    gross_margin_5y: List[float] = Field(
        ...,
        min_length=5, max_length=5,
        description="5 年毛利率(%) - §5 C3 标准口径:(营收-营业成本)/营收",
    )
    roe_5y: List[float] = Field(
        ...,
        min_length=5, max_length=5,
        description="5 年 ROE(%) - §5 C4 平均分母:归母净利/平均归母权益",
    )
    debt_ratio_5y: List[float] = Field(
        ...,
        min_length=5, max_length=5,
        description="5 年资产负债率(%) - 标准口径:总负债/总资产",
    )

    @field_validator("gross_margin_5y", "roe_5y", "debt_ratio_5y")
    @classmethod
    def _percentage_in_range(cls, v: List[float]) -> List[float]:
        for i, val in enumerate(v):
            # 允许轻微负值(净亏损公司 ROE 可能为负),但量级应在 -100 ~ 100
            if val < -100 or val > 100:
                raise ValueError(
                    f"索引 {i} 值 {val} 超出百分比合理范围 [-100, 100]"
                )
        return v


# ============================================================================
# §2.4 股权与控制(3 字段)
# ============================================================================

class Shareholder(BaseModel):
    """单个股东 - 工商口径,不含穿透"""
    name: str = Field(..., description="股东名称")
    ratio: float = Field(..., ge=0.0, le=100.0, description="持股比例(%)")


class ActualControllerType(str, Enum):
    """实际控制人 3 分类 - §9.2 判定中"""
    STATE_OWNED = "国资"
    FOREIGN = "外资"
    NATURAL_PERSON = "自然人"


class EquityControl(BaseModel):
    """§2.4 股权与控制 3 字段"""
    top10_shareholders: List[Shareholder] = Field(
        default_factory=list,
        max_length=10,
        description="前 10 大股东(工商口径,不含穿透) - §5 C8",
    )
    actual_controller: ActualControllerType = Field(
        ...,
        description="实际控制人 3 分类(国资/外资/自然人) - §9.2 判定中",
    )
    free_float_ratio: float = Field(
        ...,
        ge=0.0, le=100.0,
        description="流通股本比例(%) - §5 C8 计算口径:总流通/总股本",
    )

    @field_validator("top10_shareholders")
    @classmethod
    def _top10_total_le_100(cls, v: List[Shareholder]) -> List[Shareholder]:
        total = sum(s.ratio for s in v)
        # 前 10 大股东合计可能 < 100%(剩余为其他股东),但不应超过 100%
        if total > 100.0:
            raise ValueError(
                f"前 10 大股东合计持股 {total:.2f}% 超过 100%(数据异常)"
            )
        return v


# ============================================================================
# §2.5 管理层(2 字段)
# ============================================================================

class Manager(BaseModel):
    """单个管理人员"""
    name: str = Field(..., description="姓名")
    title: str = Field(..., description="职务(董事长/CEO/CFO)")
    tenure_start: _date = Field(..., description="任期开始")
    tenure_end: Optional[_date] = Field(None, description="任期结束;None = 在任")
    in_office: bool = Field(True, description="是否在任(投资视角) - §9.2 判定中")


class Management(BaseModel):
    """§2.5 管理层 2 字段"""
    key_management: List[Manager] = Field(
        default_factory=list,
        description="董事长/CEO/CFO(姓名 + 职务 + 任期) - §9.2 判定在职状态字段",
    )
    board_independence: float = Field(
        ...,
        ge=0.0, le=100.0,
        description="独立董事占比(%) - §9.2 标准口径:独立董事/全部董事",
    )


# ============================================================================
# §2.6 事件 5 年(2 字段)
# ============================================================================

class EventCategory(str, Enum):
    """T4 事件归因 8 类 - §5 C6 严格沿用"""
    FINANCING = "融资"
    MA = "并购"
    MANAGEMENT_CHANGE = "管理层变动"
    LITIGATION = "诉讼"
    PRODUCT_LAUNCH = "产品发布"
    REGULATORY = "监管"
    DIVIDEND = "分红"
    OTHER = "其他"


class KeyEvent(BaseModel):
    """单个关键事件 - T4 8 类之一"""
    event_date: _date = Field(..., description="事件日期")
    category: EventCategory = Field(..., description="事件分类(8 类) - §5 C6")
    summary: str = Field(..., description="事件一句话摘要")
    impact_dimensions: List[str] = Field(
        default_factory=list,
        description="影响维度(护城河 D1-D5):cost, brand, network, tech, license",
    )


class Events5Y(BaseModel):
    """§2.6 事件 5 年 2 字段"""
    key_events_5y: List[KeyEvent] = Field(
        default_factory=list,
        description="5 年关键事件(T4 抽取,8 类严格分类) - §5 C6",
    )
    regulatory_actions_5y: List[KeyEvent] = Field(
        default_factory=list,
        description="5 年监管处罚/问询函(亦沿用 KeyEvent schema,category 限 REGULATORY)",
    )


# ============================================================================
# §2.7 护城河(2 字段 · 复用现有 22-公司护城河 schema v0.1)
# ============================================================================

class MoatType(str, Enum):
    """护城河类型 5 档 - 沿用 22-公司护城河 schema v0.1"""
    STRONG = "强"
    MEDIUM = "中"
    SHALLOW = "浅"
    NONE = "无"
    NEGATIVE = "负"


class Moat(BaseModel):
    """§2.7 护城河 2 字段(沿用 22-公司护城河 schema v0.1 D1-D5)"""
    moat_score: int = Field(
        ...,
        ge=0, le=100,
        description="护城河 5 维加权总分(0-100) - §5 C5",
    )
    moat_type: MoatType = Field(..., description="护城河类型(强/中/浅/无/负)")

    @model_validator(mode="after")
    def _check_moat_consistency(self):
        """moat_score 与 moat_type 粗略校核(允许人工覆写,仅 warn)"""
        score = self.moat_score
        type_ = self.moat_type
        expected_range = {
            MoatType.STRONG: (80, 101),    # [80, 100]
            MoatType.MEDIUM: (60, 80),     # [60, 80)
            MoatType.SHALLOW: (40, 60),    # [40, 60)
            MoatType.NONE: (20, 40),       # [20, 40)
            MoatType.NEGATIVE: (-1, 20),   # [0, 20)
        }
        lo, hi = expected_range[type_]
        if not (lo <= score < hi):
            warnings.warn(
                f"moat_score={score} 通常对应区间 [{lo}, {hi}),"
                f"但 moat_type={type_.value};请确认是否人工覆写"
            )
        return self


# ============================================================================
# §3 行业扩展位(9 字段 · 3 行业 × 3 字段)
# ============================================================================

class ClinicalPhase(str, Enum):
    """17-生物 临床阶段"""
    PHASE_1 = "一"
    PHASE_2 = "二"
    PHASE_3 = "三"
    NDA = "NDA"
    APPROVED = "上市"


class PolicySensitivity(str, Enum):
    """20-经济 政策敏感度"""
    HIGH = "高"
    MEDIUM = "中"
    LOW = "低"


class IndustryExtensionBio(BaseModel):
    """17-生物 行业扩展 3 字段 - 9.3 待 17-生物 顾问补判定"""
    pipeline_drugs: Optional[List[str]] = Field(
        None, description="在研管线药物(LLM 抽取 + 人工核验)",
    )
    clinical_phase: Optional[ClinicalPhase] = Field(
        None, description="临床阶段(一/二/三/NDA/上市)",
    )
    fda_approval: Optional[List[str]] = Field(
        None, description="FDA 批准记录(药品名 + 批准日 + 适应症)",
    )


class IndustryExtensionMacro(BaseModel):
    """20-经济 行业扩展 3 字段 - 9.3 待 20-经济 顾问补判定"""
    gdp_contribution: Optional[float] = Field(
        None, description="GDP 贡献(亿元)",
    )
    policy_sensitivity: Optional[PolicySensitivity] = Field(
        None, description="政策敏感度(高/中/低)",
    )
    employment_scale: Optional[int] = Field(
        None, ge=0, description="就业规模(人)",
    )


class UnitEconomics(BaseModel):
    """23-盈利 单客户经济"""
    revenue_per_customer: float = Field(..., description="单客户收入(元)")
    gross_margin_per_customer: float = Field(..., description="单客户毛利(元)")


class IndustryExtensionProfitability(BaseModel):
    """23-盈利 行业扩展 3 字段 - 9.3 待 23-盈利 顾问补判定"""
    unit_economics: Optional[UnitEconomics] = Field(
        None, description="单位经济(单客户收入/毛利)",
    )
    ltv_cac_ratio: Optional[float] = Field(
        None, ge=0, description="LTV/CAC 倍数",
    )
    burn_rate: Optional[float] = Field(
        None, ge=0, description="烧钱率(元/月,经营现金净流出)",
    )


# ============================================================================
# §11 顶层模型(7 大类 + 3 行业扩展位 = 32 字段聚合)
# ============================================================================

class CrossIndustryCompanyProfile(BaseModel):
    """跨行业公司画像 schema v0.1.3 · 顶层模型

    字段构成:
    - basic_info: §2.1 基本信息(6)
    - business: §2.2 业务结构(3)
    - financial: §2.3 财务 5 年(5)
    - equity: §2.4 股权与控制(3)
    - management: §2.5 管理层(2)
    - events: §2.6 事件 5 年(2)
    - moat: §2.7 护城河(2)
    - industry_extensions: §3 行业扩展位(0-9 字段,3 行业各 3)
    """
    basic_info: BasicInfo = Field(..., description="§2.1 基本信息")
    business: BusinessStructure = Field(..., description="§2.2 业务结构")
    financial: Financial5Y = Field(..., description="§2.3 财务 5 年")
    equity: EquityControl = Field(..., description="§2.4 股权与控制")
    management: Management = Field(..., description="§2.5 管理层")
    events: Events5Y = Field(..., description="§2.6 事件 5 年")
    moat: Moat = Field(..., description="§2.7 护城河")
    # 3 行业扩展位互斥(同一公司不会同时是 3 行业):用 Optional + 手工选填
    bio_extension: Optional[IndustryExtensionBio] = Field(
        None, description="17-生物 扩展位(仅医药行业填)",
    )
    macro_extension: Optional[IndustryExtensionMacro] = Field(
        None, description="20-经济 扩展位(仅宏观/国计相关行业填)",
    )
    profitability_extension: Optional[IndustryExtensionProfitability] = Field(
        None, description="23-盈利 扩展位(仅 SaaS/平台经济等填)",
    )

    @model_validator(mode="after")
    def _check_industry_match(self):
        """仅 1 个行业扩展位应被填(同公司不会跨 3 行业)"""
        industry = self.basic_info.industry_l1
        ext_filled = []
        if self.bio_extension is not None:
            ext_filled.append("bio_extension")
        if self.macro_extension is not None:
            ext_filled.append("macro_extension")
        if self.profitability_extension is not None:
            ext_filled.append("profitability_extension")

        if len(ext_filled) > 1:
            raise ValueError(
                f"3 行业扩展位互斥,同时填了 {len(ext_filled)} 个: {ext_filled}"
            )

        # 粗略行业匹配(本节为预校验,最终判定由 3 行业顾问给出)
        if self.bio_extension is not None and industry != IndustryL1.PHARMA:
            raise ValueError(
                f"industry_l1={industry.value} 不是 PHARMA,bio_extension 不应填值"
            )
        if self.macro_extension is not None and industry not in (
            IndustryL1.FINANCE, IndustryL1.MANUFACTURING
        ):
            warnings.warn(
                f"industry_l1={industry.value} 不在 20-经济 典型覆盖范围"
                f"(金融/制造),请 20-经济 顾问最终判定"
            )
        if self.profitability_extension is not None and industry not in (
            IndustryL1.INTERNET, IndustryL1.CONSUMER
        ):
            warnings.warn(
                f"industry_l1={industry.value} 不在 23-盈利 典型覆盖范围"
                f"(互联网/消费),请 23-盈利 顾问最终判定"
            )
        return self


# ============================================================================
# §12 1 公司示例(贵州茅台) - 演示完整 23 通用字段填值
# ============================================================================

MAOTAI_2024_EXAMPLE: Dict[str, Any] = {
    "basic_info": {
        "name": "贵州茅台酒股份有限公司",
        "ticker": "600519.SH",
        "market": "A",
        "incorporation_date": "1999-11-20",  # 股份制改制日
        "hq_country": "中国",
        "industry_l1": "消费",
    },
    "business": {
        "business_segments": [
            {"name": "茅台酒", "revenue": 1259.0, "gross_margin": 94.5},
            {"name": "系列酒", "revenue": 209.0, "gross_margin": 79.0},
        ],
        "revenue_breakdown": {
            "国内_茅台酒": 1220.0,
            "国内_系列酒": 198.0,
            "国外": 50.0,
        },
        "key_products": ["53度飞天茅台", "茅台1935", "茅台王子酒"],
    },
    "financial": {
        "revenue_5y": [854.0, 949.0, 1062.0, 1241.0, 1505.0],          # 2020-2024(亿元)
        "net_profit_5y": [467.0, 524.0, 627.0, 747.0, 893.0],
        "gross_margin_5y": [91.5, 91.8, 92.0, 92.1, 92.1],
        "roe_5y": [31.4, 30.0, 32.0, 34.0, 36.0],
        "debt_ratio_5y": [16.0, 17.0, 18.0, 19.0, 19.5],
    },
    "equity": {
        "top10_shareholders": [
            {"name": "中国贵州茅台酒厂(集团)有限责任公司", "ratio": 54.0},
            {"name": "香港中央结算有限公司", "ratio": 6.5},
            {"name": "贵州省国有资本运营有限责任公司", "ratio": 4.5},
        ],
        "actual_controller": "国资",
        "free_float_ratio": 46.0,
    },
    "management": {
        "key_management": [
            {
                "name": "丁雄军",
                "title": "董事长",
                "tenure_start": "2021-09-01",
                "tenure_end": None,
                "in_office": True,
            },
            {
                "name": "张德芹",
                "title": "总经理",
                "tenure_start": "2024-04-01",
                "tenure_end": None,
                "in_office": True,
            },
        ],
        "board_independence": 38.0,  # 假设 38%
    },
    "events": {
        "key_events_5y": [
            {
                "event_date": "2024-06-15",
                "category": "产品发布",
                "summary": "推出茅台1935 2.0 升级版",
                "impact_dimensions": ["brand"],
            },
            {
                "event_date": "2023-12-20",
                "category": "管理层变动",
                "summary": "丁雄军连任董事长,张德芹任总经理",
                "impact_dimensions": ["brand"],
            },
        ],
        "regulatory_actions_5y": [],
    },
    "moat": {
        "moat_score": 92,
        "moat_type": "强",
    },
    # 贵州茅台 industry_l1=消费,3 行业扩展位均不填
    "bio_extension": None,
    "macro_extension": None,
    "profitability_extension": None,
}


# ============================================================================
# 自检入口(运行 `python3 02-跨行业schema-Pydantic雏形-v0.1.3.py --validate` 验证)
# ============================================================================

def main() -> int:
    """v0.1.3 雏形自检 - 验证贵州茅台示例可通过 schema 校验"""
    print("=" * 70)
    print("跨行业公司画像 schema v0.1.3 - Pydantic 雏形自检")
    print("=" * 70)
    print(f"字段数:23 通用 + 9 行业扩展 = 32(本示例填 23 通用,行业扩展均 None)")
    print(f"示例公司:贵州茅台(600519.SH) · 2024 年报")
    print(f"Pydantic 版本:{sys.modules['pydantic'].VERSION}")
    print("-" * 70)

    # §A schema 字段清单
    print("\n[§A] schema 字段清单(全部 7 大类 + 3 行业扩展位):")
    schema_fields = list(CrossIndustryCompanyProfile.model_fields.keys())
    for i, f in enumerate(schema_fields, 1):
        print(f"  {i:2d}. {f}")
    print(f"  共 {len(schema_fields)} 顶层字段(7 必填 + 3 行业扩展可空)")

    # §B Pydantic 校验贵州茅台示例
    print("\n[§B] Pydantic 校验贵州茅台示例(2024 年报):")
    try:
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            profile = CrossIndustryCompanyProfile(**MAOTAI_2024_EXAMPLE)
            print(f"  ✅ 校验通过")
            print(f"     name = {profile.basic_info.name}")
            print(f"     ticker = {profile.basic_info.ticker}")
            print(f"     industry_l1 = {profile.basic_info.industry_l1.value}")
            print(f"     revenue_5y(2024) = {profile.financial.revenue_5y[-1]:.1f} 亿元")
            print(f"     moat_score = {profile.moat.moat_score}({profile.moat.moat_type.value})")
            print(f"     bio_extension = {profile.bio_extension}(None,符合 industry_l1=消费)")
            print(f"     macro_extension = {profile.macro_extension}(None)")
            print(f"     profitability_extension = {profile.profitability_extension}(None)")
            if w:
                print(f"     ⚠️ 触发 {len(w)} 条 warning(预期内):moat_score=92 vs 区间匹配")
    except Exception as e:  # noqa: BLE001
        print(f"  ❌ 校验失败: {e}")
        return 1

    # §C 反向边界测试 - 故意传 1 个错的 ticker
    print("\n[§C] 反向边界测试 - ticker 缺少后缀(预期报错):")
    bad_example = {**MAOTAI_2024_EXAMPLE}
    bad_example["basic_info"] = {**MAOTAI_2024_EXAMPLE["basic_info"]}
    bad_example["basic_info"]["ticker"] = "600519"  # 无后缀
    try:
        CrossIndustryCompanyProfile(**bad_example)
        print("  ❌ 预期报错却通过 - C2 校验规则漏掉")
        return 1
    except Exception as e:  # noqa: BLE001
        print(f"  ✅ 按预期报错: {type(e).__name__}")
        err_msg = str(e).split("\n")[0][:80]
        print(f"     错误信息: {err_msg}")

    # §D 反向边界测试 - 行业扩展位与 industry_l1 不匹配
    print("\n[§D] 反向边界测试 - 消费行业填 bio_extension(预期报错):")
    bad_example2 = {**MAOTAI_2024_EXAMPLE, "bio_extension": {"pipeline_drugs": ["test"]}}
    try:
        CrossIndustryCompanyProfile(**bad_example2)
        print("  ❌ 预期报错却通过 - 行业扩展位校验漏掉")
        return 1
    except Exception as e:  # noqa: BLE001
        print(f"  ✅ 按预期报错: {type(e).__name__}")
        err_msg = str(e).split("\n")[0][:80]
        print(f"     错误信息: {err_msg}")

    # §E JSON Schema 导出
    print("\n[§E] JSON Schema 导出(Pydantic V2 自动派生):")
    json_schema = CrossIndustryCompanyProfile.model_json_schema()
    print(f"  schema 顶层 keys: {list(json_schema.keys())[:5]}")
    print(f"  schema properties 字段数: {len(json_schema.get('properties', {}))}")
    print(f"  required 字段数: {len(json_schema.get('required', []))}")

    print("\n" + "=" * 70)
    print("v0.1.3 Pydantic 雏形自检完成")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
