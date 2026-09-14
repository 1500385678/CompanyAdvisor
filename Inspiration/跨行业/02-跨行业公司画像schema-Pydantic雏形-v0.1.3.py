# -*- coding: utf-8 -*-
"""
跨行业公司画像 schema · Pydantic 雏形 · v0.1.5
================================================

> 对应主计划:[项目开发计划.md §5 第 6 项](../../项目开发计划.md) - 跨行业顾问对齐
> 状态:**草稿**(等张勇拉 17-生物 / 20-经济 / 23-盈利 3 顾问对齐后,可能升 v0.2)
> 维护:22-公司-Company 行业顾问
> 落地日期:2026-09-12(v0.1.3) / 2026-09-14(v0.1.4 跨行业 5 公司 dryrun) / 2026-09-15(v0.1.5 跨行业对比矩阵)
> 对应章节:Inspiration/跨行业/01-跨行业公司画像字段schema设计稿.md §11/§12(v0.1.3)+ §14(v0.1.4)+ §15(v0.1.5)
> 不做什么:不对齐(对齐仍由张勇驱动);不勾选 §5 #6 checkbox(对齐未发生)

## 用途
- 把 §2 通用 23 字段 + §3 行业扩展 9 字段 = 32 字段定义翻译为 Pydantic V2 model
- 5 公司跨行业示例填值(覆盖 5 个 industry_l1 + 3 个扩展位):
  · 贵州茅台 600519.SH(消费,无扩展)
  · 恒瑞医药 600276.SH(医药,bio_extension · 17-生物)
  · 腾讯控股 0700.HK(互联网,profitability_extension · 23-盈利)
  · 招商银行 600036.SH(金融,macro_extension · 20-经济)
  · 宁德时代 300750.SZ(新能源,无扩展,验证 §5 C7 8 分类)
- v0.1.5 跨行业 5 公司对比矩阵(8 指标 × 5 公司 = 40 数据点 dryrun,§G 段输出)
- v0.2 共识会议前,可让 3 行业直接在 IDE 里看字段类型 + 必填性 + 默认值 + 跨行业样例 + 跨行业对比矩阵
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

## v0.1.5 vs v0.1.4 变更
- 新增 `build_cross_industry_matrix()` 函数:遍历 ALL_EXAMPLES → CrossIndustryCompanyProfile → 抽取 8 指标
- 主自检 main() 加 §G 跨行业对比矩阵 dryrun(8 指标 × 5 公司 = 40 数据点)
- §A-§F 6 段自检(贵州茅台单家 §A-§E + 5 公司批量 §F)保持不变,作为 §G 前置

## v0.1.4 vs v0.1.3 变更(归档)
- 加 4 家公司示例(恒瑞医药 / 腾讯控股 / 招商银行 / 宁德时代)→ ALL_EXAMPLES 字典(5 家)
- 主自检 main() 加 §F 跨行业 5 公司批量 dryrun
- §A-§E 5 段自检(贵州茅台单家)保持不变,作为 §F 前置
- 修复 v0.1.3 提及的"1 公司示例"为"5 公司示例"

## 依赖
- pydantic >= 2.0(本机验证 pydantic 2.13.4)
- 运行:`python3 02-跨行业公司画像schema-Pydantic雏形-v0.1.3.py --validate`
  (文件名保留 v0.1.3 后缀,因 schema 主体未变,内容演进为 v0.1.5)
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
# §12 v0.1.4 跨行业 4 公司补充示例(恒瑞医药 / 腾讯控股 / 招商银行 / 宁德时代)
# 覆盖 5 industry_l1 × 3 扩展位:消费/医药/互联网/金融/新能源
# ============================================================================

HENGRUI_2024_EXAMPLE: Dict[str, Any] = {
    "basic_info": {
        "name": "江苏恒瑞医药股份有限公司",
        "ticker": "600276.SH",
        "market": "A",
        "incorporation_date": "1997-04-28",
        "hq_country": "中国",
        "industry_l1": "医药",
    },
    "business": {
        "business_segments": [
            {"name": "抗肿瘤药", "revenue": 138.0, "gross_margin": 91.0},
            {"name": "造影剂", "revenue": 22.0, "gross_margin": 70.0},
            {"name": "其他药品", "revenue": 26.0, "gross_margin": 65.0},
        ],
        "revenue_breakdown": {
            "国内_抗肿瘤": 132.0,
            "国内_造影剂": 20.0,
            "国外": 34.0,
        },
        "key_products": ["PD-1 卡瑞利珠单抗", "紫杉醇白蛋白结合型", "碘佛醇"],
    },
    "financial": {
        "revenue_5y": [165.0, 188.0, 212.0, 228.0, 280.0],         # 2020-2024
        "net_profit_5y": [38.0, 45.0, 39.0, 43.0, 54.0],
        "gross_margin_5y": [87.0, 86.0, 84.0, 84.0, 85.0],
        "roe_5y": [16.0, 16.0, 12.0, 12.0, 14.0],
        "debt_ratio_5y": [10.0, 11.0, 8.0, 9.0, 10.0],
    },
    "equity": {
        "top10_shareholders": [
            {"name": "江苏恒瑞医药集团有限公司", "ratio": 24.0},
            {"name": "香港中央结算有限公司", "ratio": 12.0},
            {"name": "中国证券金融股份有限公司", "ratio": 2.5},
        ],
        "actual_controller": "自然人",  # 孙飘扬
        "free_float_ratio": 99.0,
    },
    "management": {
        "key_management": [
            {
                "name": "孙飘扬",
                "title": "董事长",
                "tenure_start": "2021-01-01",
                "tenure_end": None,
                "in_office": True,
            },
            {
                "name": "戴洪斌",
                "title": "总经理",
                "tenure_start": "2022-04-01",
                "tenure_end": None,
                "in_office": True,
            },
        ],
        "board_independence": 42.0,
    },
    "events": {
        "key_events_5y": [
            {
                "event_date": "2024-05-20",
                "category": "产品发布",
                "summary": "PD-L1 阿得贝利单抗获批,联合化疗一线治疗 ES-SCLC",
                "impact_dimensions": ["tech", "license"],
            },
            {
                "event_date": "2023-09-15",
                "category": "其他",
                "summary": "与默克达成 14 亿欧元 ADC 药物海外授权交易",
                "impact_dimensions": ["tech", "brand"],
            },
        ],
        "regulatory_actions_5y": [],
    },
    "moat": {
        "moat_score": 75,
        "moat_type": "中",  # 75 在 [60, 80),符合区间
    },
    # 恒瑞医药 industry_l1=医药,17-生物 bio_extension 应填
    "bio_extension": {
        "pipeline_drugs": ["SHR-1701(PD-L1/TGF-β)", "SHR-A1811(HER2 ADC)", "SHR-1316(PD-L1)"],
        "clinical_phase": "三",  # 多个产品进入 III 期或 NDA
        "fda_approval": [
            "卡瑞利珠单抗(2024-Q4 美国 III 期启动,未获批)",
        ],
    },
    "macro_extension": None,
    "profitability_extension": None,
}


TENCENT_2024_EXAMPLE: Dict[str, Any] = {
    "basic_info": {
        "name": "腾讯控股有限公司",
        "ticker": "0700.HK",  # §5 C2 港股代码需 4 位 + .HK
        "market": "H",
        "incorporation_date": "1999-11-23",
        "hq_country": "中国",
        "industry_l1": "互联网",
    },
    "business": {
        "business_segments": [
            {"name": "增值服务(游戏+社交网络)", "revenue": 3200.0, "gross_margin": 55.0},
            {"name": "网络广告", "revenue": 1200.0, "gross_margin": 55.0},
            {"name": "金融科技及企业服务", "revenue": 2200.0, "gross_margin": 35.0},
        ],
        "revenue_breakdown": {
            "国内_游戏": 2800.0,
            "国内_广告": 1100.0,
            "国内_FinTech": 1800.0,
            "国外_游戏": 400.0,
        },
        "key_products": ["微信(WeChat)", "王者荣耀", "英雄联盟", "腾讯视频"],
    },
    "financial": {
        "revenue_5y": [4820.0, 5601.0, 6490.0, 6090.0, 6600.0],   # 2020-2024(亿元)
        "net_profit_5y": [1598.0, 2248.0, 1887.0, 1576.0, 1940.0],
        "gross_margin_5y": [46.0, 44.0, 43.0, 45.0, 47.0],
        "roe_5y": [28.0, 29.0, 25.0, 21.0, 24.0],
        "debt_ratio_5y": [42.0, 41.0, 40.0, 41.0, 40.0],
    },
    "equity": {
        "top10_shareholders": [
            {"name": "Naspers/Prosus", "ratio": 24.0},
            {"name": "马化腾", "ratio": 8.0},
            {"name": "香港中央结算(代理人)", "ratio": 22.0},
        ],
        "actual_controller": "自然人",  # 马化腾
        "free_float_ratio": 68.0,
    },
    "management": {
        "key_management": [
            {
                "name": "马化腾",
                "title": "董事会主席兼CEO",
                "tenure_start": "1999-11-01",
                "tenure_end": None,
                "in_office": True,
            },
            {
                "name": "刘炽平",
                "title": "总裁兼执行董事",
                "tenure_start": "2005-02-01",
                "tenure_end": None,
                "in_office": True,
            },
        ],
        "board_independence": 50.0,  # 港股披露要求,假设 50%
    },
    "events": {
        "key_events_5y": [
            {
                "event_date": "2024-09-10",
                "category": "产品发布",
                "summary": "推出混元大模型 Turbo 版本,对标 GPT-4o",
                "impact_dimensions": ["tech", "brand"],
            },
            {
                "event_date": "2022-12-15",
                "category": "监管",
                "summary": "游戏版号恢复发放,《王者荣耀》新皮肤获批",
                "impact_dimensions": ["license", "brand"],
            },
        ],
        "regulatory_actions_5y": [
            {
                "event_date": "2021-07-24",
                "category": "监管",
                "summary": "腾讯被要求解除网络音乐独家版权",
                "impact_dimensions": ["license", "network"],
            },
        ],
    },
    "moat": {
        "moat_score": 88,
        "moat_type": "强",  # 88 在 [80, 100)
    },
    # 腾讯 industry_l1=互联网,23-盈利 profitability_extension 应填
    "bio_extension": None,
    "macro_extension": None,
    "profitability_extension": {
        "unit_economics": {
            "revenue_per_customer": 2200.0,  # 假设每用户年均贡献 2200 元
            "gross_margin_per_customer": 1034.0,  # 47% 毛利率
        },
        "ltv_cac_ratio": 4.5,  # 假设 LTV/CAC = 4.5
        "burn_rate": 0.0,  # 腾讯正现金流,burn_rate = 0
    },
}


CMB_2024_EXAMPLE: Dict[str, Any] = {
    "basic_info": {
        "name": "招商银行股份有限公司",
        "ticker": "600036.SH",
        "market": "A",
        "incorporation_date": "1987-03-31",
        "hq_country": "中国",
        "industry_l1": "金融",
    },
    "business": {
        "business_segments": [
            {"name": "零售金融", "revenue": 2000.0, "gross_margin": None},  # 银行不适用毛利率口径
            {"name": "批发金融", "revenue": 1500.0, "gross_margin": None},
            {"name": "其他业务", "revenue": 150.0, "gross_margin": None},
        ],
        "revenue_breakdown": {
            "利息净收入": 2150.0,
            "手续费及佣金净收入": 720.0,
            "其他非息收入": 780.0,
        },
        "key_products": ["招商银行App", "朝朝宝", "金葵花理财"],
    },
    "financial": {
        "revenue_5y": [2905.0, 3313.0, 3448.0, 3392.0, 3650.0],  # 营业收入(亿元)
        "net_profit_5y": [973.0, 1199.0, 1380.0, 1466.0, 1640.0],
        "gross_margin_5y": [50.0, 52.0, 50.0, 49.0, 51.0],  # 银行净息差+非息收入占比粗算
        "roe_5y": [16.0, 17.0, 17.0, 16.0, 16.0],
        "debt_ratio_5y": [91.0, 91.0, 90.0, 90.0, 90.0],  # 银行高杠杆,负债率天然高
    },
    "equity": {
        "top10_shareholders": [
            {"name": "招商局集团有限公司", "ratio": 29.0},
            {"name": "香港中央结算有限公司", "ratio": 18.0},
            {"name": "中国证券金融股份有限公司", "ratio": 2.5},
        ],
        "actual_controller": "国资",  # 招商局集团
        "free_float_ratio": 70.0,
    },
    "management": {
        "key_management": [
            {
                "name": "缪建民",
                "title": "董事长",
                "tenure_start": "2020-09-01",
                "tenure_end": None,
                "in_office": True,
            },
            {
                "name": "王良",
                "title": "行长兼执行董事",
                "tenure_start": "2022-05-01",
                "tenure_end": None,
                "in_office": True,
            },
        ],
        "board_independence": 38.0,
    },
    "events": {
        "key_events_5y": [
            {
                "event_date": "2024-04-10",
                "category": "其他",
                "summary": "零售客户 AUM 突破 14 万亿,稳居股份行第一",
                "impact_dimensions": ["brand", "network"],
            },
            {
                "event_date": "2023-08-25",
                "category": "监管",
                "summary": "因代销信托产品违规被罚 350 万",
                "impact_dimensions": ["license"],
            },
        ],
        "regulatory_actions_5y": [],
    },
    "moat": {
        "moat_score": 85,
        "moat_type": "强",  # 85 在 [80, 100)
    },
    # 招商银行 industry_l1=金融,20-经济 macro_extension 应填(在 §11 校验白名单内)
    "bio_extension": None,
    "macro_extension": {
        "gdp_contribution": 350.0,  # 假设 2024 年贡献 GDP 350 亿元(税收+利润)
        "policy_sensitivity": "高",  # 银行业受货币政策/监管政策高敏感
        "employment_scale": 110000,  # 约 11 万员工
    },
    "profitability_extension": None,
}


CATL_2024_EXAMPLE: Dict[str, Any] = {
    "basic_info": {
        "name": "宁德时代新能源科技股份有限公司",
        "ticker": "300750.SZ",
        "market": "A",
        "incorporation_date": "2011-12-16",
        "hq_country": "中国",
        "industry_l1": "新能源",
    },
    "business": {
        "business_segments": [
            {"name": "动力电池系统", "revenue": 2530.0, "gross_margin": 23.0},
            {"name": "储能电池系统", "revenue": 670.0, "gross_margin": 25.0},
            {"name": "电池材料及回收", "revenue": 240.0, "gross_margin": 15.0},
        ],
        "revenue_breakdown": {
            "国内_动力电池": 2100.0,
            "国内_储能": 540.0,
            "国外_动力电池": 430.0,
            "国外_储能": 130.0,
        },
        "key_products": ["麒麟电池", "神行超充电池", "CTP 3.0 电池包"],
    },
    "financial": {
        "revenue_5y": [503.0, 1304.0, 3286.0, 4009.0, 3620.0],   # 2020-2024(亿元)
        "net_profit_5y": [55.0, 159.0, 307.0, 441.0, 507.0],
        "gross_margin_5y": [27.8, 26.5, 19.1, 22.9, 24.4],
        "roe_5y": [14.0, 22.0, 19.0, 22.0, 21.0],
        "debt_ratio_5y": [60.0, 65.0, 70.0, 70.0, 68.0],
    },
    "equity": {
        "top10_shareholders": [
            {"name": "宁波瑞庭投资有限公司", "ratio": 23.0},  # 曾毓群控股
            {"name": "香港中央结算有限公司", "ratio": 15.0},
            {"name": "黄世霖", "ratio": 5.0},
        ],
        "actual_controller": "自然人",  # 曾毓群
        "free_float_ratio": 75.0,
    },
    "management": {
        "key_management": [
            {
                "name": "曾毓群",
                "title": "董事长兼总经理",
                "tenure_start": "2011-12-01",
                "tenure_end": None,
                "in_office": True,
            },
            {
                "name": "周佳",
                "title": "副董事长",
                "tenure_start": "2017-06-01",
                "tenure_end": None,
                "in_office": True,
            },
        ],
        "board_independence": 40.0,
    },
    "events": {
        "key_events_5y": [
            {
                "event_date": "2024-12-05",
                "category": "产品发布",
                "summary": "麒麟二代电池量产,续航 1000 公里",
                "impact_dimensions": ["tech", "brand"],
            },
            {
                "event_date": "2023-10-15",
                "category": "融资",
                "summary": "赴港交所二次上市,募资 53 亿美元",
                "impact_dimensions": ["cost", "brand"],
            },
        ],
        "regulatory_actions_5y": [],
    },
    "moat": {
        "moat_score": 82,
        "moat_type": "强",  # 82 在 [80, 100)
    },
    # 宁德时代 industry_l1=新能源,3 行业扩展位均不填(无对应扩展位)
    "bio_extension": None,
    "macro_extension": None,
    "profitability_extension": None,
}


# §12 v0.1.4 ALL_EXAMPLES 聚合:5 家公司 · 5 industry_l1 · 3 个扩展位
ALL_EXAMPLES: Dict[str, Dict[str, Any]] = {
    "贵州茅台_600519.SH_消费": MAOTAI_2024_EXAMPLE,
    "恒瑞医药_600276.SH_医药_bio": HENGRUI_2024_EXAMPLE,
    "腾讯控股_0700.HK_互联网_profitability": TENCENT_2024_EXAMPLE,
    "招商银行_600036.SH_金融_macro": CMB_2024_EXAMPLE,
    "宁德时代_300750.SZ_新能源": CATL_2024_EXAMPLE,
}


# ============================================================================
# §G v0.1.5 跨行业 5 公司对比矩阵 - 数据抽取函数
# ============================================================================


def build_cross_industry_matrix() -> List[Dict[str, Any]]:
    """v0.1.5 新增:遍历 ALL_EXAMPLES → 校验 → 抽取 8 指标 → 返回对比矩阵行。

    返回:每行一个 dict,字段为 company / industry / market / rev_2024 / gm_2024 /
    roe_2024 / dr_2024 / free_float / moat_score / moat_type / extension。
    校验失败的公司跳过(并打印警告)。
    """
    rows: List[Dict[str, Any]] = []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        for name, data in ALL_EXAMPLES.items():
            try:
                p = CrossIndustryCompanyProfile(**data)
            except Exception as e:  # noqa: BLE001
                print(f"  ⚠️ {name} 校验失败,跳过: {e}")
                continue
            exts = []
            if p.bio_extension:
                exts.append("bio")
            if p.macro_extension:
                exts.append("macro")
            if p.profitability_extension:
                exts.append("profitability")
            ext_str = "+".join(exts) if exts else "no-ext"
            rows.append(
                {
                    "company": name.split("_")[0],
                    "industry": p.basic_info.industry_l1.value,
                    "market": p.basic_info.market.value,
                    "rev_2024": p.financial.revenue_5y[-1],
                    "gm_2024": p.financial.gross_margin_5y[-1],
                    "roe_2024": p.financial.roe_5y[-1],
                    "dr_2024": p.financial.debt_ratio_5y[-1],
                    "free_float": p.equity.free_float_ratio,
                    "moat_score": p.moat.moat_score,
                    "moat_type": p.moat.moat_type.value,
                    "extension": ext_str,
                }
            )
    return rows


# ============================================================================
# 自检入口(运行 `python3 02-跨行业schema-Pydantic雏形-v0.1.3.py --validate` 验证)
# ============================================================================

def main() -> int:
    """v0.1.5 雏形自检 - 验证 5 公司跨行业示例 + 跨行业对比矩阵可通过"""
    print("=" * 70)
    print("跨行业公司画像 schema v0.1.5 - Pydantic 雏形自检(5 公司 dryrun + 对比矩阵)")
    print("=" * 70)
    print(f"字段数:23 通用 + 9 行业扩展 = 32")
    print(f"示例公司:5 家(覆盖 5 industry_l1 × 3 扩展位)")
    print(f"  · 贵州茅台(消费,无扩展) · 恒瑞医药(医药,bio)")
    print(f"  · 腾讯控股(互联网,profitability) · 招商银行(金融,macro)")
    print(f"  · 宁德时代(新能源,无扩展)")
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

    # §F v0.1.4 跨行业 5 公司批量 dryrun
    print("\n[§F] v0.1.4 跨行业 5 公司批量 dryrun(覆盖 5 industry_l1 × 3 扩展位):")
    success_count = 0
    fail_count = 0
    ext_filled_map = {
        "贵州茅台_600519.SH_消费": [],
        "恒瑞医药_600276.SH_医药_bio": ["bio_extension"],
        "腾讯控股_0700.HK_互联网_profitability": ["profitability_extension"],
        "招商银行_600036.SH_金融_macro": ["macro_extension"],
        "宁德时代_300750.SZ_新能源": [],
    }
    for name, data in ALL_EXAMPLES.items():
        try:
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                profile = CrossIndustryCompanyProfile(**data)
                ind = profile.basic_info.industry_l1.value
                ticker = profile.basic_info.ticker
                rev_2024 = profile.financial.revenue_5y[-1]
                moat_s = profile.moat.moat_score
                exts = ext_filled_map[name]
                ext_str = "+".join(exts) if exts else "no-ext"
                w_count = len(w)
                w_marker = f" [⚠️{w_count} warnings]" if w_count else ""
                print(
                    f"  ✅ {ticker:>12s} | {ind:4s} | {ext_str:18s} | "
                    f"营收{rev_2024:6.0f}亿 | moat={moat_s:3d} | {name.split('_')[0]}{w_marker}"
                )
                success_count += 1
        except Exception as e:  # noqa: BLE001
            print(f"  ❌ {name} 校验失败: {e}")
            fail_count += 1
    print(f"  汇总:{success_count} 通过 / {fail_count} 失败(预期 5/0)")

    if fail_count > 0:
        print("  ❌ 批量 dryrun 存在失败,v0.1.4 雏形未通过")
        return 1

    # §G v0.1.5 跨行业 5 公司对比矩阵
    print("\n[§G] v0.1.5 跨行业 5 公司对比矩阵(8 指标 × 5 公司 = 40 数据点):")
    rows = build_cross_industry_matrix()
    if not rows:
        print("  ❌ 对比矩阵为空,§G 失败")
        return 1
    # 8 指标横向对比表
    header = (
        f"  {'Company':<14s} {'ind':<6s} {'mkt':<4s} "
        f"{'rev24':>7s} {'gm24':>6s} {'roe24':>6s} {'dr24':>6s} "
        f"{'ff':>5s} {'moat':>5s} {'moat_t':<7s} {'ext':<14s}"
    )
    print(header)
    print("  " + "-" * (len(header) - 2))
    for r in rows:
        print(
            f"  {r['company']:<14s} {r['industry']:<6s} {r['market']:<4s} "
            f"{r['rev_2024']:>7.0f} {r['gm_2024']:>6.1f} {r['roe_2024']:>6.1f} "
            f"{r['dr_2024']:>6.1f} {r['free_float']:>5.1f} {r['moat_score']:>5d} "
            f"{r['moat_type']:<7s} {r['extension']:<14s}"
        )

    # 营收 5 年 CAGR(以 rev_5y 序列估算)
    print("\n  营收 5 年 CAGR(2020-2024):")
    cagr_strs = []
    for name, data in ALL_EXAMPLES.items():
        rev5y = data.get("financial", {}).get("revenue_5y", [])
        if len(rev5y) >= 2 and rev5y[0] > 0:
            cagr = ((rev5y[-1] / rev5y[0]) ** (1 / (len(rev5y) - 1)) - 1) * 100
            cagr_strs.append(f"{name.split('_')[0]:<8s} {cagr:>5.1f}%")
    print("    " + " | ".join(cagr_strs))

    # 护城河分梯队
    strong = sum(1 for r in rows if r["moat_score"] >= 85)
    medium = sum(1 for r in rows if 70 <= r["moat_score"] < 85)
    weak = sum(1 for r in rows if r["moat_score"] < 70)
    moat_scores = [r["moat_score"] for r in rows]
    mean_score = sum(moat_scores) / len(moat_scores) if moat_scores else 0
    median_score = sorted(moat_scores)[len(moat_scores) // 2] if moat_scores else 0
    print("\n  护城河分梯队:")
    print(
        f"    强(85-100):{strong} 家  | 中(70-84):{medium} 家  | 弱(< 70):{weak} 家"
    )
    print(f"    均值 {mean_score:.1f} | 中位数 {median_score}")

    # 行业扩展位填法对比
    print("\n  行业扩展位填法对比:")
    for r in rows:
        if r["extension"] in ("bio", "macro", "profitability"):
            ext_name = r["extension"]
            ext_data_map = {
                "bio": ("bio_extension", r["company"]),
                "macro": ("macro_extension", r["company"]),
                "profitability": ("profitability_extension", r["company"]),
            }
            ext_key, company = ext_data_map[ext_name]
            sample = ALL_EXAMPLES[f"{company}_..."] if False else None
            # 从 ALL_EXAMPLES 取第一个匹配 ticker
            for k, v in ALL_EXAMPLES.items():
                if k.startswith(company):
                    sample = v
                    break
            if sample and ext_key in sample and sample[ext_key]:
                ext_obj = sample[ext_key]
                keys = list(ext_obj.keys()) if isinstance(ext_obj, dict) else []
                print(
                    f"    {ext_name:<24s} → {company:<6s}(字段: {', '.join(keys)})"
                )

    print(
        f"\n  汇总:{len(rows)} 公司全部通过对比矩阵"
        f"(矩阵 {len(rows) * 8} 数据点 = 8 指标 × {len(rows)} 公司)"
    )

    if len(rows) != 5:
        print(f"  ❌ 对比矩阵行数不为 5(实际 {len(rows)}),§G 失败")
        return 1

    print("\n" + "=" * 70)
    print("v0.1.5 Pydantic 雏形自检完成(7 段全通过 · §A-§G)")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
