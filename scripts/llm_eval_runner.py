#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
llm_eval_runner · T1 财报速读 跑批骨架(Phase 0 §5 #4 跑批日历 09-04 上午项)
======================================================================

对应项目开发计划 §5 Phase 0 第 4 项:在 T1 财报速读 prompt v0.1 基础上,
跑 5 公司 × 5 年 = 25 份年报 × 4 模型 = 100 条结果,出 1 份基线报告。

本骨架兑现 [Inspiration/LLM基线/05-T1财报速读基线报告设计稿.md §9](../Inspiration/LLM基线/05-T1财报速读基线报告设计稿.md)
跑批日历 09-04 上午要求"写 scripts/llm_eval_runner.py(4 模型 × 25 样本)"。
**本骨架不实际调 LLM provider**——4 模型调用点全部以 stub 函数呈现,等
张勇分配 token + 选 provider 后,逐个替换为真实 API 调用即可。

三种子命令:

  1) --manifest
     打印 25 样本 manifest(5 公司 × 5 年报),每行:公司/期间/代码/行业/
     PDF 路径(占位) / 抽取状态(stub)。对应 05 §3 25 样本表。

  2) --dry-run
     全流程贯通,但不调 LLM:加载 25 manifest → 调 pdfplumber_demo.py
     抽取 pages JSON → 装载 T1 prompt(契约占位)→ 4 模型全部走 stub
     → 输出 100 条 jsonl 到 samples/llm_eval/05-t1-results.dryrun.jsonl。
     验证"流程跑通 + JSON 契约稳定"。

  3) --run
     真跑:与 --dry-run 同样骨架,但 4 模型调用点替换为真实 provider
     (Claude Sonnet 4 / GPT-4o / Qwen-Finance / Ollama qwen2.5-7b)。
     **本骨架仅留 TODO,不在 cron 任务中触发**(等张勇 + token 就绪后人工触发)。

输出契约(jsonl,每行 1 条模型对 1 个样本):
  {
    "run_id": "uuid4",
    "task": "T1-财报速读",
    "model": "claude-sonnet-4",
    "sample_id": 1,
    "company": "贵州茅台",
    "ticker": "600519.SH",
    "period": "FY2020",
    "pdf_path": "samples/llm_eval/raw/600519.SH-2020.pdf",
    "extract_status": "ok",
    "page_count": 128,
    "table_count": 32,
    "extract_seconds": 12.4,
    "prompt_version": "T1-v0.1",
    "llm_call_status": "ok-stub",   # 真实跑时应为 "ok"
    "llm_output": {...4 段摘要...},
    "self_eval_confidence": "high",
    "self_eval_score": 4,           # 1-4 档自评(沿用 01 §4 校准)
    "latency_seconds": 0.0,         # stub
    "cost_usd": 0.0,                # stub
    "timestamp": "2026-09-04T03:30:00+08:00"
  }

依赖:复用 pdfplumber_demo.py 的 extract_pdf(),新增加载 manifest + stub 调用层。
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import sys
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List

# 复用 08-27 落地的 pdfplumber 抽取(避免重复实现 PDF 解析层)
sys.path.insert(0, str(Path(__file__).resolve().parent))
from pdfplumber_demo import extract_pdf  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
EVAL_DIR = REPO_ROOT / "samples" / "llm_eval"
EVAL_DIR.mkdir(parents=True, exist_ok=True)
RAW_DIR = EVAL_DIR / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

# ---------- 4 模型清单(沿用 05 §5 模板) ----------------------------- #

MODELS: List[Dict[str, Any]] = [
    {
        "id": "claude-sonnet-4",
        "provider": "anthropic",
        "env_key": "ANTHROPIC_API_KEY",
        "cost_per_1k_usd": 0.015,  # 估算
        "stub": True,  # 本骨架阶段全部 stub,等 provider 接入
    },
    {
        "id": "gpt-4o",
        "provider": "openai",
        "env_key": "OPENAI_API_KEY",
        "cost_per_1k_usd": 0.010,
        "stub": True,
    },
    {
        "id": "qwen-finance",
        "provider": "dashscope",
        "env_key": "DASHSCOPE_API_KEY",
        "cost_per_1k_usd": 0.004,
        "stub": True,
    },
    {
        "id": "ollama-qwen2.5-7b",
        "provider": "ollama-local",
        "env_key": None,
        "cost_per_1k_usd": 0.0,
        "stub": True,
    },
]

# ---------- 5 公司 × 5 年 manifest(对应 05 §3 表) ------------------- #

# 5 公司 = 5 行业 覆盖:消费 / 互联网 / 新能源 / 金融 / 半导体
# 5 年 = 2020-2024 完整年报;25 份 = 5 × 5
SAMPLE_TABLE: List[Dict[str, Any]] = []

_COMPANIES = [
    ("贵州茅台", "600519.SH", "消费-白酒"),
    ("腾讯控股", "00700.HK", "互联网"),
    ("宁德时代", "300750.SZ", "新能源-动力电池"),
    ("招商银行", "600036.SH", "金融-银行"),
    ("英伟达",   "NVDA.US",   "半导体-算力"),
]
_YEARS = [2020, 2021, 2022, 2023, 2024]


def build_manifest() -> List[Dict[str, Any]]:
    """生成 25 样本 manifest(沿用 05 §3 选样原则 + 三市覆盖口径)。"""
    samples: List[Dict[str, Any]] = []
    sample_id = 1
    for company, ticker, industry in _COMPANIES:
        for year in _YEARS:
            market = ticker.split(".")[-1]  # SH / SZ / HK / US
            pdf_rel = f"samples/llm_eval/raw/{ticker}-{year}.pdf"
            samples.append(
                {
                    "sample_id": sample_id,
                    "company": company,
                    "ticker": ticker,
                    "market": market,
                    "industry": industry,
                    "period": f"FY{year}",
                    "pdf_path": pdf_rel,
                    "extract_status": "TODO",  # 真有 PDF 后改为 "ok"/"fail"
                    "page_count": None,
                    "table_count": None,
                    "note": "",
                }
            )
            sample_id += 1
    return samples


# ---------- T1 prompt 装载(契约占位) -------------------------------- #

def load_t1_prompt() -> Dict[str, Any]:
    """装载 T1 财报速读 prompt v0.1(本骨架仅给契约,真文件由 04 类 prompt 落地)。"""
    # 对应 Inspiration/LLM基线/01-4类LLM任务基线设计稿.md §3 T1 v0.1
    return {
        "task": "T1-财报速读",
        "version": "T1-v0.1",
        "system": (
            "你是 CompanyAdvisor 财报速读助手。读入 1 份年报抽取 JSON,"
            "按 4 段结构输出摘要(performance / drivers / risks / guidance),"
            "每条数据需带 evidence 原文(≤ 60 字)与定位页码。"
        ),
        "user_template": (
            "# 输入\n"
            "{pages_json}\n\n"
            "# 要求\n"
            "1. 严格按 4 段 JSON 结构输出。\n"
            "2. 每个数字必须可回溯到 pages 中某页某段。\n"
            "3. evidence 原文不超过 60 字。\n"
            "4. 给出 self_eval_confidence(high/medium/low)。"
        ),
        "output_schema": {
            "performance": "headline + yoy_revenue + yoy_net_income + segment_breakdown",
            "drivers": "list of {driver, evidence}",
            "risks": "list of {risk, evidence}",
            "guidance": "next_period_outlook + key_metrics_to_watch",
            "self_eval_confidence": "high/medium/low",
        },
    }


# ---------- 4 模型调用 stub(本骨架阶段) ----------------------------- #

def call_llm_stub(model: Dict[str, Any], prompt: Dict[str, Any], pages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """4 模型调用点占位。真跑时按 model["provider"] 分发到 anthropic / openai / dashscope / ollama。

    本函数严格遵循"不实际跑 LLM"边界,只返回结构稳定 stub,便于 --dry-run 验完整流程。
    """
    fake_output = {
        "performance": {
            "headline": "[STUB] 模型未真跑,本字段为占位",
            "yoy_revenue": "TODO",
            "yoy_net_income": "TODO",
            "segment_breakdown": [],
        },
        "drivers": [],
        "risks": [],
        "guidance": {"next_period_outlook": "TODO", "key_metrics_to_watch": []},
        "self_eval_confidence": "low",
    }
    return {
        "llm_call_status": "ok-stub",
        "llm_output": fake_output,
        "self_eval_confidence": "low",
        "self_eval_score": 1,  # stub 阶段自评 1 档(不可用),真跑后才给真实档
        "latency_seconds": 0.0,
        "cost_usd": 0.0,
    }


def call_llm(model: Dict[str, Any], prompt: Dict[str, Any], pages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """统一调用入口:目前全走 stub,等 provider 接入后按 model["provider"] 分发。"""
    if model.get("stub", True):
        return call_llm_stub(model, prompt, pages)
    # 真跑分支(本骨架留 TODO,不触发)
    raise NotImplementedError(
        f"真跑分支尚未实现 provider={model['provider']} model={model['id']};"
        "等张勇分配 token 后,按 [Inspiration/LLM基线/05 §4.1] 替换为真实 API 调用。"
    )


# ---------- 单样本跑批 --------------------------------------------- #

def run_single_sample(model: Dict[str, Any], sample: Dict[str, Any], prompt: Dict[str, Any]) -> Dict[str, Any]:
    """对 1 个样本(1 份年报) + 1 个模型,产出 1 条结果。"""
    run_id = str(uuid.uuid4())
    pdf_path = REPO_ROOT / sample["pdf_path"]
    record: Dict[str, Any] = {
        "run_id": run_id,
        "task": prompt["task"],
        "model": model["id"],
        "sample_id": sample["sample_id"],
        "company": sample["company"],
        "ticker": sample["ticker"],
        "period": sample["period"],
        "pdf_path": sample["pdf_path"],
        "extract_status": "skipped-stub",  # stub 模式不抽 PDF,验流程
        "page_count": 0,
        "table_count": 0,
        "extract_seconds": 0.0,
        "prompt_version": prompt["version"],
    }

    # 真实 PDF 存在 → 抽 PDF;不存在 → stub 跳过(不报错,体现边界)
    if pdf_path.is_file():
        t0 = time.time()
        try:
            payload = extract_pdf(pdf_path)
            record["extract_status"] = "ok"
            record["page_count"] = payload["page_count"]
            record["table_count"] = sum(len(p["tables"]) for p in payload["pages"])
            record["extract_seconds"] = round(time.time() - t0, 2)
            pages = payload["pages"]
        except Exception as exc:  # noqa: BLE001
            record["extract_status"] = f"fail:{type(exc).__name__}"
            pages = []
    else:
        pages = []  # stub 模式:无 PDF 也不报错

    # 调 LLM(stub 阶段)
    llm_result = call_llm(model, prompt, pages)
    record.update(llm_result)
    record["timestamp"] = _dt.datetime.now(_dt.timezone.utc).astimezone().isoformat(timespec="seconds")
    return record


# ---------- CLI ----------------------------------------------------- #

def _parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="llm_eval_runner · T1 财报速读 跑批骨架(Phase 0 §5 #4 跑批日历 09-04 上午项)",
    )
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--manifest", action="store_true", help="打印 25 样本 manifest 表")
    g.add_argument("--dry-run", action="store_true", help="全流程贯通,4 模型全 stub,输出 jsonl 验流程")
    g.add_argument("--run", action="store_true", help="真跑(本骨架阶段留 TODO,NotImplementedError)")
    p.add_argument(
        "--out", metavar="JSONL_PATH",
        help="jsonl 输出路径(默认 samples/llm_eval/05-t1-results.dryrun.jsonl)",
    )
    p.add_argument(
        "--models", nargs="+", metavar="MODEL_ID",
        help="仅跑指定模型(默认 4 模型全跑)",
    )
    p.add_argument(
        "--limit", type=int, default=0,
        help="仅跑前 N 个样本(0 = 全 25,调试用)",
    )
    return p.parse_args(argv)


def cmd_manifest(samples: List[Dict[str, Any]]) -> int:
    """--manifest:打印 25 样本表(对应 05 §3 表)。"""
    header = (
        f"{'#':>3}  {'公司':<8}  {'代码':<11}  {'行业':<14}  {'期间':<7}  "
        f"{'PDF 路径':<46}  {'状态':<12}"
    )
    print(header)
    print("-" * len(header))
    for s in samples:
        print(
            f"{s['sample_id']:>3}  {s['company']:<8}  {s['ticker']:<11}  "
            f"{s['industry']:<14}  {s['period']:<7}  {s['pdf_path']:<46}  "
            f"{s['extract_status']:<12}"
        )
    print(f"\n[OK] 共 {len(samples)} 个样本(5 公司 × 5 年)")
    return 0


def cmd_dry_run(samples: List[Dict[str, Any]], models: List[Dict[str, Any]], out_path: Path, limit: int) -> int:
    """--dry-run:4 模型 × N 样本 全流程贯通,输出 jsonl 验流程。"""
    if limit > 0:
        samples = samples[:limit]
    prompt = load_t1_prompt()
    out_path.write_text("", encoding="utf-8")  # 清空

    total = len(samples) * len(models)
    print(f"[DRY-RUN] 启动: {len(samples)} 样本 × {len(models)} 模型 = {total} 条结果")
    print(f"[DRY-RUN] prompt: {prompt['task']} {prompt['version']}")
    print(f"[DRY-RUN] 输出: {out_path}")
    print(f"[DRY-RUN] 注意: 4 模型调用全走 stub,无 LLM provider 实际调用\n")

    count = 0
    for sample in samples:
        for model in models:
            rec = run_single_sample(model, sample, prompt)
            with out_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            count += 1
            if count % 10 == 0 or count == total:
                print(f"[DRY-RUN] 进度 {count}/{total} ({count * 100 // total}%)")

    print(f"\n[OK] dry-run 完成 {count} 条,写入 {out_path}")
    return 0


def main(argv: List[str] | None = None) -> int:
    args = _parse_args(sys.argv[1:] if argv is None else argv)
    samples = build_manifest()

    if args.manifest:
        return cmd_manifest(samples)

    # 选定模型
    models = MODELS
    if args.models:
        ids = set(args.models)
        models = [m for m in MODELS if m["id"] in ids]
        if not models:
            print(f"[ERR] --models 指定全部不在 MODELS 列表里: {args.models}", file=sys.stderr)
            return 1

    out_path = (
        Path(args.out) if args.out
        else EVAL_DIR / "05-t1-results.dryrun.jsonl"
    )

    if args.dry_run:
        return cmd_dry_run(samples, models, out_path, args.limit)

    if args.run:
        # 真跑分支:本骨架阶段不实现,留 TODO。
        print("[ERR] --run 模式尚未实现,需先接 LLM provider(token + 选 provider)。", file=sys.stderr)
        print("      请按 [Inspiration/LLM基线/05-T1财报速读基线报告设计稿.md §4.1] 替换 call_llm() 真分支。", file=sys.stderr)
        return 2

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
