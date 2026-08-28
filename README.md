# CompanyAdvisor

> 22-公司-Company 行业 Web 项目 · 内部代号 CompanyAdvisor

## 项目说明
基于张勇的 36 行业架构,CompanyAdvisor 是 公司-Company 行业的 Web 端顾问产品。

## 同步
- GitHub: https://github.com/1500385678/CompanyAdvisor
- Gitee: https://gitee.com/architectzy/CompanyAdvisor

## 自动化
- T4 每日 02:00 检查项目并更新开发计划
- T5 每日 03:00 完成小步开发并 commit + push

## Phase 0 进度速览

> 最后更新:2026-08-29 (T5 启动 §5 #4,4 任务基线设计稿 + T1 财报速读 prompt v0.1) · 当前 HEAD 见 `git log -1`
> 详细计划见 [项目开发计划.md](./项目开发计划.md) §5 · 截止 **2026-09-06**(剩 8 天)

| # | 项 | 状态 | 备注 |
|---|---|---|---|
| 1 | Inspiration 资料索引 | ✅ 完成 (08-24) | [Inspiration/00-索引.md](./Inspiration/00-索引.md) · 四类共 10 条 |
| 2 | 30-50 家公司种子数据 | ✅ 完成 (08-26) | [Inspiration/公司/01-种子公司清单.md](./Inspiration/公司/01-种子公司清单.md) · 38 家 · 8 行业 · 三市覆盖 |
| 3 | pdfplumber 财报解析 demo | ✅ 完成 (08-27) | [scripts/pdfplumber_demo.py](./scripts/pdfplumber_demo.py) · 支持 `--make-sample` 与 `--extract` 双模式 · 样例输出 [samples/demo-extract.json](./samples/demo-extract.json) |
| 4 | LLM 4 类任务基线评估 | 🚧 启动 (08-29) | [Inspiration/LLM基线/01-4类LLM任务基线设计稿.md](./Inspiration/LLM基线/01-4类LLM任务基线设计稿.md) · 4 任务一览 + T1 财报速读 prompt v0.1(1/4 prompt drafted) · 3/4 pending |
| 5 | 护城河评分 schema(5 维) | ✅ 完成 (08-28) | [Inspiration/护城河/01-护城河评分schema设计稿.md](./Inspiration/护城河/01-护城河评分schema设计稿.md) · 5 维等权 20 + 4 档评分 + Evidence Anchor 契约 + Pydantic schema |
| 6 | 跨行业顾问对齐(17-生物 / 20-经济 / 23-盈利) | ⏳ 未启动 | |

**整体进度**:4 / 6(66.7%) · #4 进入启动态,大项尚未勾选

**下一步(立即可执行)**:① 08-30 落地 T2 护城河 LLM prompt v0.1(基于已就绪 schema) → ② 08-31 落地 T3 对标匹配 prompt v0.1 → ③ 09-01 落地 T4 事件归因 prompt v0.1 → ④ 09-02~06 跑 5 家头部公司真实年报做 4 档盲评 → ⑤ 与 17-生物 / 20-经济顾问对齐"公司画像统一字段"。
