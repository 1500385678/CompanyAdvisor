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

> 最后更新:2026-08-28 (T5 落地护城河 schema 设计稿) · 当前 HEAD:`bb12491`
> 详细计划见 [项目开发计划.md](./项目开发计划.md) §5 · 截止 **2026-09-06**(剩 10 天)

| # | 项 | 状态 | 备注 |
|---|---|---|---|
| 1 | Inspiration 资料索引 | ✅ 完成 (08-24) | [Inspiration/00-索引.md](./Inspiration/00-索引.md) · 四类共 10 条 |
| 2 | 30-50 家公司种子数据 | ✅ 完成 (08-26) | [Inspiration/公司/01-种子公司清单.md](./Inspiration/公司/01-种子公司清单.md) · 38 家 · 8 行业 · 三市覆盖 |
| 3 | pdfplumber 财报解析 demo | ✅ 完成 (08-27) | [scripts/pdfplumber_demo.py](./scripts/pdfplumber_demo.py) · 支持 `--make-sample` 与 `--extract` 双模式 · 样例输出 [samples/demo-extract.json](./samples/demo-extract.json) |
| 4 | LLM 4 类任务基线评估 | ⏳ 未启动 | 依赖项 3(已解除) |
| 5 | 护城河评分 schema(5 维) | ✅ 完成 (08-28) | [Inspiration/护城河/01-护城河评分schema设计稿.md](./Inspiration/护城河/01-护城河评分schema设计稿.md) · 5 维等权 20 + 4 档评分 + Evidence Anchor 契约 + Pydantic schema |
| 6 | 跨行业顾问对齐(17-生物 / 20-经济 / 23-盈利) | ⏳ 未启动 | |

**整体进度**:4 / 6(66.7%)

**下一步(立即可执行)**:① 基于 pdfplumber demo 抽取 5 家头部公司真实年报(种子清单前 5 家)→ ② 跑 LLM 4 类任务基线 → ③ 与 17-生物 / 20-经济顾问对齐"公司画像统一字段"。
